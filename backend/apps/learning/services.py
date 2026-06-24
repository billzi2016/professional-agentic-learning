from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass

from django.db import transaction
from django.db.models import Max
from json_repair import repair_json
from pydantic import BaseModel, Field, ValidationError, field_validator

from apps.conversations.models import Conversation, Message
from apps.learning.context import build_budgeted_context
from apps.learning.models import LearningCard, Quiz, QuizAttempt
from apps.learning.prompts import LEARNING_CARD_SYSTEM_PROMPT, QUIZ_SYSTEM_PROMPT
from apps.providers.services import get_chat_provider


class LearningCardPayload(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    topic: str = Field(min_length=1, max_length=120)
    level: str = "beginner"
    markdown: str = Field(min_length=1)
    summary: str = Field(min_length=1)

    @field_validator("level")
    @classmethod
    def validate_level(cls, value: str) -> str:
        if value not in {"beginner", "intermediate", "advanced"}:
            return "beginner"
        return value


class QuizPayload(BaseModel):
    question: str = Field(min_length=1)
    options: list[str] = Field(min_length=4, max_length=4)
    correct_option_index: int = Field(ge=0, le=3)
    explanation: str = Field(min_length=1)


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
    except (ValueError, ValidationError):
        # 模型偶尔会违反 JSON 约束。第一版不做复杂重试队列，保留原文为 Markdown，
        # 但仍通过 schema 生成可保存的最小结构，避免接口直接失败。
        return LearningCardPayload(
            title=fallback_topic[:80] or "学习卡片",
            topic=fallback_topic[:120] or "general",
            level="beginner",
            markdown=raw_text.strip() or "模型没有返回有效内容。",
            summary=(raw_text.strip()[:300] or "模型没有返回有效摘要。"),
        )


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
    )
    card = LearningCard.objects.create(
        conversation=conversation,
        message=message,
        title=payload.title,
        topic=payload.topic,
        level=payload.level,
        markdown=payload.markdown,
        summary=payload.summary,
        order_index=next_index,
    )
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
