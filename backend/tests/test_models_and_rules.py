import pytest

from apps.conversations.models import Conversation, Message
from apps.conversations.services import can_edit_message
from apps.learning.models import LearningCard


@pytest.mark.django_db
def test_only_latest_user_message_is_editable():
    conversation = Conversation.objects.create(title="SQL 学习")
    first = Message.objects.create(
        conversation=conversation,
        role=Message.Role.USER,
        content="开始学习 SQL",
    )
    Message.objects.create(
        conversation=conversation,
        role=Message.Role.ASSISTANT,
        message_type=Message.MessageType.LEARNING_CARD,
        content="第一张卡片",
    )
    latest = Message.objects.create(
        conversation=conversation,
        role=Message.Role.USER,
        content="继续",
    )

    assert can_edit_message(first) is False
    assert can_edit_message(latest) is True


@pytest.mark.django_db
def test_learning_card_uses_orm_relations():
    conversation = Conversation.objects.create(title="SQL 学习")
    message = Message.objects.create(
        conversation=conversation,
        role=Message.Role.ASSISTANT,
        message_type=Message.MessageType.LEARNING_CARD,
        content="## SELECT",
    )
    card = LearningCard.objects.create(
        conversation=conversation,
        message=message,
        title="SELECT 基础",
        topic="SQL",
        markdown="## SELECT\n用于查询数据。",
        summary="学习 SELECT 的查询作用。",
        order_index=1,
    )

    assert conversation.learning_cards.get() == card
    assert message.learning_card == card
