import json
from dataclasses import dataclass

import tiktoken

MODEL_CONTEXT_LIMIT_TOKENS = 128_000
PROMPT_TOKEN_BUDGET = 100_000
ENCODING_NAME = "cl100k_base"


@dataclass(frozen=True)
class ContextItem:
    kind: str
    payload: dict
    created_order: int


encoding = tiktoken.get_encoding(ENCODING_NAME)


def count_text_tokens(text: str) -> int:
    return len(encoding.encode(text))


def count_messages_tokens(messages: list[dict[str, str]]) -> int:
    # 这里用 cl100k_base 对实际发送给 provider 的 role/content 做确定性计数。
    # 不把 provider 私有 chat wrapper 开销算进去，是因为 Ollama/OpenRouter/vLLM
    # 的包装差异不同；本项目用 100k 阈值给 128k 上下文留出了足够余量。
    return sum(count_text_tokens(message.get("role", "") + "\n" + message.get("content", "")) for message in messages)


def build_budgeted_context(
    *,
    system_prompt: str,
    current_user_content: str,
    action: str,
    recent_messages: list[dict],
    card_summaries: list[dict],
    token_budget: int = PROMPT_TOKEN_BUDGET,
) -> list[dict[str, str]]:
    required_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": current_user_content},
    ]
    required_tokens = count_messages_tokens(required_messages)
    if required_tokens > token_budget:
        raise ValueError("system prompt and current user input exceed token budget")

    items: list[ContextItem] = []
    for index, message in enumerate(recent_messages):
        items.append(ContextItem(kind="message", payload=message, created_order=index))
    offset = len(items)
    for index, summary in enumerate(card_summaries):
        items.append(ContextItem(kind="card_summary", payload=summary, created_order=offset + index))

    # 从新到旧尝试纳入历史。超过 100k 后自然丢弃最老内容。
    selected: list[ContextItem] = []
    for item in sorted(items, key=lambda value: value.created_order, reverse=True):
        candidate = sorted([*selected, item], key=lambda value: value.created_order)
        context_payload = _context_payload(action, candidate)
        candidate_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(context_payload, ensure_ascii=False)},
            {"role": "user", "content": current_user_content},
        ]
        if count_messages_tokens(candidate_messages) <= token_budget:
            selected.append(item)

    context_payload = _context_payload(
        action,
        sorted(selected, key=lambda value: value.created_order),
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(context_payload, ensure_ascii=False)},
        {"role": "user", "content": current_user_content},
    ]


def _context_payload(action: str, items: list[ContextItem]) -> dict:
    return {
        "action": action,
        "action_policy": (
            "start 表示第一张卡片，必须先介绍主题、用途、学习路线和起点；"
            "continue 表示沿着 next_topic 继续学习一个最小知识点。"
        ),
        "recent_messages": [
            item.payload for item in items if item.kind == "message"
        ],
        "card_summaries": [
            item.payload for item in items if item.kind == "card_summary"
        ],
    }
