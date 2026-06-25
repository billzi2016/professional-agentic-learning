from datetime import datetime
from uuid import UUID

from ninja import Schema


class ErrorDetail(Schema):
    code: str
    message: str
    details: dict = {}


class ErrorResponse(Schema):
    error: ErrorDetail


class HealthResponse(Schema):
    status: str
    version: str


class ProviderStatusResponse(Schema):
    provider: str
    provider_type: str
    model: str
    base_url: str
    status: str
    latency_ms: int | None = None
    checked_at: datetime | None = None
    error: str | None = None


class ProviderConfigPatch(Schema):
    provider_type: str
    base_url: str
    model: str
    api_key: str = ""


class ConversationCreate(Schema):
    title: str = "新对话"


class ConversationPatch(Schema):
    title: str | None = None
    summary: str | None = None


class ConversationOut(Schema):
    id: UUID
    title: str
    summary: str
    is_pinned: bool
    created_at: datetime
    updated_at: datetime


class ConversationListItem(ConversationOut):
    pass


class ConversationListResponse(Schema):
    items: list[ConversationListItem]
    next_cursor: str | None = None


class MessageCreate(Schema):
    content: str


class MessagePatch(Schema):
    content: str


class MessageOut(Schema):
    id: UUID
    role: str
    message_type: str
    content: str
    is_editable: bool
    can_regenerate_from_here: bool
    learning_card_id: UUID | None = None
    metadata: dict = {}
    created_at: datetime


class MessageListResponse(Schema):
    items: list[MessageOut]
    next_cursor: str | None = None


class LearnStreamIn(Schema):
    user_message_id: UUID | None = None
    action: str = "start"
    learning_card_id: UUID | None = None


class QuizStreamIn(Schema):
    learning_card_id: UUID


class LearningCardOut(Schema):
    id: UUID
    conversation_id: UUID
    title: str
    topic: str
    level: str
    markdown: str
    summary: str
    next_topic: str
    order_index: int
    created_at: datetime


class QuizOut(Schema):
    id: UUID
    question: str
    options: list[dict]
    answered: bool


class QuizAnswerIn(Schema):
    selected_option_index: int


class QuizAnswerOut(Schema):
    is_correct: bool
    selected_option_index: int
    correct_option_index: int
    explanation: str
