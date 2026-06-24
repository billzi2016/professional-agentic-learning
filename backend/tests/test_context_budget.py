import json

from apps.learning.context import (
    PROMPT_TOKEN_BUDGET,
    build_budgeted_context,
    count_messages_tokens,
)


def test_context_budget_discards_oldest_items():
    old_marker = "oldest-message-marker"
    newest_marker = "newest-message-marker"
    large_text = "数据库 查询 关系 表 字段 " * 5000
    recent_messages = [
        {"role": "user", "content": old_marker + large_text},
        *[
            {"role": "assistant", "content": f"middle-{index}" + large_text}
            for index in range(18)
        ],
        {"role": "user", "content": newest_marker},
    ]

    messages = build_budgeted_context(
        system_prompt="你是老师。",
        current_user_content="继续学习 SQL",
        action="continue",
        recent_messages=recent_messages,
        card_summaries=[],
        token_budget=20_000,
    )

    serialized = json.dumps(messages, ensure_ascii=False)
    assert count_messages_tokens(messages) <= 20_000
    assert newest_marker in serialized
    assert old_marker not in serialized


def test_default_prompt_budget_is_100k_for_128k_context():
    assert PROMPT_TOKEN_BUDGET == 100_000
