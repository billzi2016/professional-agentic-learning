from django.db import transaction

from apps.conversations.models import Conversation, Message
from apps.learning.models import LearningCard, Quiz


def latest_active_user_message(conversation: Conversation) -> Message | None:
    return (
        conversation.messages.filter(
            role=Message.Role.USER,
            status=Message.Status.ACTIVE,
        )
        .order_by("-created_at", "-id")
        .first()
    )


def latest_active_card(conversation: Conversation) -> LearningCard | None:
    return (
        conversation.learning_cards.filter(status=LearningCard.Status.ACTIVE)
        .order_by("-order_index", "-created_at")
        .first()
    )


def latest_active_quiz(conversation: Conversation) -> Quiz | None:
    return (
        conversation.quizzes.filter(status=Quiz.Status.ACTIVE)
        .order_by("-created_at", "-id")
        .first()
    )


def can_edit_message(message: Message) -> bool:
    if message.role != Message.Role.USER or message.status != Message.Status.ACTIVE:
        return False
    latest_user = latest_active_user_message(message.conversation)
    return bool(latest_user and latest_user.id == message.id)


def can_regenerate_card(card: LearningCard) -> bool:
    if card.status != LearningCard.Status.ACTIVE:
        return False
    latest_card = latest_active_card(card.conversation)
    if not latest_card or latest_card.id != card.id:
        return False
    # 如果最近卡片后面已经有 active 题目，重生成会让题目依据失效。
    return not card.quizzes.filter(status=Quiz.Status.ACTIVE).exists()


def can_delete_quiz(quiz: Quiz) -> bool:
    latest_quiz = latest_active_quiz(quiz.conversation)
    return bool(latest_quiz and latest_quiz.id == quiz.id)


@transaction.atomic
def archive_recent_user_message(message: Message) -> None:
    if not can_edit_message(message):
        raise ValueError("只能删除最近一轮用户输入")
    message.status = Message.Status.ARCHIVED
    message.save(update_fields=["status", "updated_at"])
    message.conversation.messages.filter(
        role=Message.Role.ASSISTANT,
        status=Message.Status.ACTIVE,
        created_at__gt=message.created_at,
    ).update(status=Message.Status.SUPERSEDED)
