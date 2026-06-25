from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass

from django.db import transaction
from django.db.models import Max
from json_repair import repair_json
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

from apps.conversations.models import Conversation, Message
from apps.learning.context import build_budgeted_context
from apps.learning.models import LearningCard, Quiz, QuizAttempt
from apps.learning.prompts import LEARNING_CARD_SYSTEM_PROMPT, QUIZ_SYSTEM_PROMPT
from apps.providers.services import get_chat_provider


def normalize_learning_summary(summary: str, topic: str) -> str:
    value = "".join(summary.split()).strip("，。,.：:；;")
    if value.startswith("学习") and "用途" not in value and 2 < len(value) <= 10:
        return value
    if value.startswith("学") and "用途" not in value and len(value) > 1:
        return f"学习{value[1:]}"[:10]
    topic_value = "".join(topic.split()).strip("，。,.：:；;") or "当前主题"
    return f"学习{topic_value}"[:10]


class LearningCardPayload(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    topic: str = Field(min_length=1, max_length=120)
    level: str = "beginner"
    markdown: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    next_topic: str = Field(default="", max_length=200)

    @field_validator("level")
    @classmethod
    def validate_level(cls, value: str) -> str:
        if value not in {"beginner", "intermediate", "advanced"}:
            return "beginner"
        return value

    @model_validator(mode="after")
    def normalize_summary(self) -> "LearningCardPayload":
        self.summary = normalize_learning_summary(self.summary, self.topic)
        return self


class QuizPayload(BaseModel):
    question: str = Field(min_length=1)
    options: list[str] = Field(min_length=4, max_length=4)
    correct_option_index: int = Field(ge=0, le=3)
    explanation: str = Field(min_length=1)


class InvalidLearningCardError(ValueError):
    pass


@dataclass
class StreamResult:
    raw_text: str
    chunks: list[str]


def active_messages(conversation: Conversation):
    return conversation.messages.filter(status=Message.Status.ACTIVE)


def build_learning_messages(conversation: Conversation, user_message: Message, action: str) -> list[dict[str, str]]:
    recent_messages = active_messages(conversation).order_by("created_at")
    card_summaries = conversation.learning_cards.filter(
        status=LearningCard.Status.ACTIVE,
    ).order_by("order_index", "created_at")

    return build_budgeted_context(
        system_prompt=LEARNING_CARD_SYSTEM_PROMPT,
        current_user_content=user_message.content,
        action=action,
        recent_messages=[
            {"role": item.role, "content": item.content}
            for item in recent_messages
        ],
        card_summaries=[
            {"title": item.title, "summary": item.summary}
            for item in card_summaries
        ],
    )


def build_quiz_messages(card: LearningCard) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": QUIZ_SYSTEM_PROMPT},
        {"role": "user", "content": card.markdown},
    ]


def stream_provider_text(messages: list[dict[str, str]]) -> Iterator[str]:
    yield from get_chat_provider().stream_chat(messages)


def parse_learning_card(raw_text: str, fallback_topic: str) -> LearningCardPayload:
    try:
        data = json.loads(repair_json(raw_text))
        return LearningCardPayload.model_validate(data)
    except (ValueError, ValidationError) as exc:
        raise InvalidLearningCardError("模型没有返回有效学习卡片 JSON") from exc


def parse_quiz(raw_text: str) -> QuizPayload:
    data = json.loads(repair_json(raw_text))
    return QuizPayload.model_validate(data)


@transaction.atomic
def save_learning_card(conversation: Conversation, user_message: Message, raw_text: str) -> LearningCard:
    payload = parse_learning_card(raw_text, user_message.content)
    next_index = (
        conversation.learning_cards.aggregate(value=Max("order_index"))["value"] or 0
    ) + 1
    message = Message.objects.create(
        conversation=conversation,
        role=Message.Role.ASSISTANT,
        message_type=Message.MessageType.LEARNING_CARD,
        content=payload.markdown,
        metadata={"next_topic": payload.next_topic},
    )
    card = LearningCard.objects.create(
        conversation=conversation,
        message=message,
        title=payload.title,
        topic=payload.topic,
        level=payload.level,
        markdown=payload.markdown,
        summary=payload.summary,
        next_topic=payload.next_topic,
        order_index=next_index,
    )
    if next_index == 1:
        # 第一张卡片生成后固定侧边栏摘要。后续继续学习不覆盖它，
        # 避免左侧列表随着每张卡片变化而跳动。
        conversation.title = payload.title
        if not conversation.summary:
            conversation.summary = payload.summary
            conversation.save(update_fields=["title", "summary", "updated_at"])
        else:
            conversation.save(update_fields=["title", "updated_at"])
    else:
        conversation.save(update_fields=["updated_at"])
    return card


@transaction.atomic
def save_quiz(card: LearningCard, raw_text: str) -> Quiz:
    payload = parse_quiz(raw_text)
    options = [
        {"label": chr(ord("A") + index), "text": text}
        for index, text in enumerate(payload.options)
    ]
    quiz = Quiz.objects.create(
        conversation=card.conversation,
        learning_card=card,
        question=payload.question,
        options=options,
        correct_option_index=payload.correct_option_index,
        explanation=payload.explanation,
    )
    Message.objects.create(
        conversation=card.conversation,
        role=Message.Role.ASSISTANT,
        message_type=Message.MessageType.QUIZ,
        content=payload.question,
        metadata={"quiz_id": str(quiz.id)},
    )
    return quiz


def answer_quiz(quiz: Quiz, selected_option_index: int) -> QuizAttempt:
    if selected_option_index < 0 or selected_option_index > 3:
        raise ValueError("selected_option_index must be between 0 and 3")
    return QuizAttempt.objects.create(
        quiz=quiz,
        selected_option_index=selected_option_index,
        is_correct=selected_option_index == quiz.correct_option_index,
    )
