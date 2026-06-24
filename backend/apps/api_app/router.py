import json
from uuid import UUID

from django.http import StreamingHttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import NinjaAPI
from ninja.errors import HttpError

from apps.api_app.schemas import (
    ConversationCreate,
    ConversationListItem,
    ConversationListResponse,
    ConversationOut,
    ConversationPatch,
    HealthResponse,
    LearnStreamIn,
    LearningCardOut,
    MessageCreate,
    MessageListResponse,
    MessageOut,
    MessagePatch,
    ProviderConfigPatch,
    ProviderStatusResponse,
    QuizAnswerIn,
    QuizAnswerOut,
    QuizOut,
    QuizStreamIn,
)
from apps.conversations.models import Conversation, Message
from apps.conversations.services import (
    archive_recent_user_message,
    can_delete_quiz,
    can_edit_message,
    can_regenerate_card,
)
from apps.learning.models import LearningCard, Quiz
from apps.learning.services import (
    answer_quiz,
    build_learning_messages,
    build_quiz_messages,
    save_learning_card,
    save_quiz,
    stream_provider_text,
)
from apps.providers.models import ProviderConfig, ProviderHealthCheck
from apps.providers.services import get_active_provider_config, run_provider_health_check

api = NinjaAPI(title="AI Learning Card API", version="0.1.0")


def sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def serialize_conversation(conversation: Conversation) -> ConversationOut:
    return ConversationOut(
        id=conversation.id,
        title=conversation.title,
        is_pinned=conversation.is_pinned,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


def serialize_message(message: Message) -> MessageOut:
    card = getattr(message, "learning_card", None)
    return MessageOut(
        id=message.id,
        role=message.role,
        message_type=message.message_type,
        content=message.content,
        metadata=message.metadata,
        is_editable=can_edit_message(message),
        can_regenerate_from_here=bool(card and can_regenerate_card(card)),
        learning_card_id=card.id if card else None,
        created_at=message.created_at,
    )


def serialize_card(card: LearningCard) -> LearningCardOut:
    return LearningCardOut(
        id=card.id,
        conversation_id=card.conversation_id,
        title=card.title,
        topic=card.topic,
        level=card.level,
        markdown=card.markdown,
        summary=card.summary,
        next_topic=card.next_topic,
        order_index=card.order_index,
        created_at=card.created_at,
    )


@api.get("/health", response=HealthResponse)
def health(request):
    return {"status": "ok", "version": "0.1.0"}


@api.get("/csrf")
def csrf(request):
    # Ninja 会把 dict 转成自己的响应对象，不能直接套 ensure_csrf_cookie。
    # 显式调用 get_token 会标记 CSRF cookie 需要写入，最终由 Django middleware 设置。
    get_token(request)
    return {"csrf": "ok"}


@api.get("/provider/status", response=ProviderStatusResponse)
def provider_status(request):
    config = get_active_provider_config()
    last_check = config.health_checks.first()
    return {
        "provider": config.name,
        "provider_type": config.provider_type,
        "model": config.model,
        "base_url": config.base_url,
        "status": last_check.status if last_check else ProviderHealthCheck.Status.CHECKING,
        "latency_ms": last_check.latency_ms if last_check else None,
        "checked_at": last_check.checked_at if last_check else None,
        "error": last_check.error_message if last_check and last_check.error_message else None,
    }


@api.post("/provider/health-check", response=ProviderStatusResponse)
def provider_health_check(request):
    check = run_provider_health_check()
    config = check.provider_config
    return {
        "provider": config.name,
        "provider_type": config.provider_type,
        "model": config.model,
        "base_url": config.base_url,
        "status": check.status,
        "latency_ms": check.latency_ms,
        "checked_at": check.checked_at,
        "error": check.error_message or None,
    }


@api.patch("/provider/config", response=ProviderStatusResponse)
def patch_provider_config(request, payload: ProviderConfigPatch):
    ProviderConfig.objects.filter(is_active=True).update(is_active=False)
    config = ProviderConfig.objects.create(
        name=payload.provider_type,
        provider_type=payload.provider_type,
        base_url=payload.base_url,
        model=payload.model,
        api_key=payload.api_key,
        is_active=True,
    )
    return {
        "provider": config.name,
        "provider_type": config.provider_type,
        "model": config.model,
        "base_url": config.base_url,
        "status": ProviderHealthCheck.Status.CHECKING,
        "latency_ms": None,
        "checked_at": None,
        "error": None,
    }


@api.get("/conversations", response=ConversationListResponse)
def list_conversations(request, include_archived: bool = False, limit: int = 50):
    qs = Conversation.objects.all()
    if not include_archived:
        qs = qs.filter(archived_at__isnull=True)
    items = []
    for conversation in qs[: min(limit, 100)]:
        last_message = conversation.messages.filter(status=Message.Status.ACTIVE).last()
        items.append(
            ConversationListItem(
                **serialize_conversation(conversation).dict(),
                last_message_preview=(last_message.content[:120] if last_message else ""),
            )
        )
    return {"items": items, "next_cursor": None}


@api.post("/conversations", response=ConversationOut)
def create_conversation(request, payload: ConversationCreate):
    return serialize_conversation(Conversation.objects.create(title=payload.title or "新对话"))


@api.get("/conversations/{conversation_id}", response=ConversationOut)
def get_conversation(request, conversation_id: UUID):
    return serialize_conversation(get_object_or_404(Conversation, id=conversation_id))


@api.patch("/conversations/{conversation_id}", response=ConversationOut)
def patch_conversation(request, conversation_id: UUID, payload: ConversationPatch):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    conversation.title = payload.title
    conversation.save(update_fields=["title", "updated_at"])
    return serialize_conversation(conversation)


@api.delete("/conversations/{conversation_id}")
def delete_conversation(request, conversation_id: UUID):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    conversation.archived_at = timezone.now()
    conversation.save(update_fields=["archived_at", "updated_at"])
    return {"deleted": True}


@api.post("/conversations/{conversation_id}/pin", response=ConversationOut)
def pin_conversation(request, conversation_id: UUID):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    conversation.is_pinned = True
    conversation.save(update_fields=["is_pinned", "updated_at"])
    return serialize_conversation(conversation)


@api.post("/conversations/{conversation_id}/unpin", response=ConversationOut)
def unpin_conversation(request, conversation_id: UUID):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    conversation.is_pinned = False
    conversation.save(update_fields=["is_pinned", "updated_at"])
    return serialize_conversation(conversation)


@api.get("/conversations/{conversation_id}/messages", response=MessageListResponse)
def list_messages(request, conversation_id: UUID, limit: int = 100):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    messages = conversation.messages.filter(status=Message.Status.ACTIVE)[: min(limit, 200)]
    return {"items": [serialize_message(message) for message in messages], "next_cursor": None}


@api.post("/conversations/{conversation_id}/messages", response=MessageOut)
def create_message(request, conversation_id: UUID, payload: MessageCreate):
    if not payload.content.strip():
        raise HttpError(422, "输入内容不能为空")
    conversation = get_object_or_404(Conversation, id=conversation_id)
    message = Message.objects.create(
        conversation=conversation,
        role=Message.Role.USER,
        message_type=Message.MessageType.PLAIN,
        content=payload.content.strip(),
    )
    conversation.save(update_fields=["updated_at"])
    return serialize_message(message)


@api.patch("/messages/{message_id}", response=MessageOut)
def patch_message(request, message_id: UUID, payload: MessagePatch):
    message = get_object_or_404(Message, id=message_id)
    if not can_edit_message(message):
        raise HttpError(409, "只能修改最近一轮用户输入")
    message.content = payload.content.strip()
    message.save(update_fields=["content", "updated_at"])
    return serialize_message(message)


@api.delete("/messages/{message_id}")
def delete_message(request, message_id: UUID):
    message = get_object_or_404(Message, id=message_id)
    try:
        archive_recent_user_message(message)
    except ValueError as exc:
        raise HttpError(409, str(exc)) from exc
    return {"deleted": True}


@api.post("/conversations/{conversation_id}/learn/stream")
def learn_stream(request, conversation_id: UUID, payload: LearnStreamIn):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    user_message = get_object_or_404(Message, id=payload.user_message_id, conversation=conversation)

    def events():
        raw_chunks: list[str] = []
        yield sse_event("card_start", {"temporary_id": str(user_message.id)})
        try:
            for delta in stream_provider_text(build_learning_messages(conversation, user_message, payload.action)):
                raw_chunks.append(delta)
                yield sse_event("card_delta", {"delta": delta})
            card = save_learning_card(conversation, user_message, "".join(raw_chunks))
            # 模型按约束返回 JSON，但用户界面应该展示 JSON 里的 markdown 字段。
            # 流式阶段先显示原始增量，保存成功后用 card_replace 把草稿替换为干净 Markdown。
            yield sse_event("card_replace", {"markdown": card.markdown, "next_topic": card.next_topic})
            yield sse_event("card_done", {"card_id": str(card.id), "message_id": str(card.message_id)})
        except Exception as exc:
            yield sse_event("error", {"code": "generation_failed", "message": str(exc)[:500]})

    return StreamingHttpResponse(events(), content_type="text/event-stream")


@api.get("/learning-cards/{card_id}", response=LearningCardOut)
def get_learning_card(request, card_id: UUID):
    return serialize_card(get_object_or_404(LearningCard, id=card_id))


@api.post("/learning-cards/{card_id}/regenerate")
def regenerate_learning_card(request, card_id: UUID):
    card = get_object_or_404(LearningCard, id=card_id)
    if not can_regenerate_card(card):
        raise HttpError(409, "只能重新生成最近一张学习卡片")
    card.status = LearningCard.Status.SUPERSEDED
    card.save(update_fields=["status"])
    user_message = card.conversation.messages.filter(role=Message.Role.USER).last()
    if not user_message:
        raise HttpError(409, "找不到可用于重新生成的用户输入")
    return learn_stream(request, card.conversation_id, LearnStreamIn(user_message_id=user_message.id, action="regenerate"))


@api.post("/conversations/{conversation_id}/quiz/stream")
def quiz_stream(request, conversation_id: UUID, payload: QuizStreamIn):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    card = get_object_or_404(LearningCard, id=payload.learning_card_id, conversation=conversation)

    def events():
        raw_chunks: list[str] = []
        yield sse_event("quiz_start", {"temporary_id": str(card.id)})
        try:
            for delta in stream_provider_text(build_quiz_messages(card)):
                raw_chunks.append(delta)
                yield sse_event("quiz_delta", {"delta": delta})
            quiz = save_quiz(card, "".join(raw_chunks))
            yield sse_event("quiz_done", {"quiz_id": str(quiz.id)})
        except Exception as exc:
            yield sse_event("error", {"code": "generation_failed", "message": str(exc)[:500]})

    return StreamingHttpResponse(events(), content_type="text/event-stream")


@api.get("/quizzes/{quiz_id}", response=QuizOut)
def get_quiz(request, quiz_id: UUID):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return {
        "id": quiz.id,
        "question": quiz.question,
        "options": quiz.options,
        "answered": quiz.attempts.exists(),
    }


@api.post("/quizzes/{quiz_id}/answer", response=QuizAnswerOut)
def submit_quiz_answer(request, quiz_id: UUID, payload: QuizAnswerIn):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    try:
        attempt = answer_quiz(quiz, payload.selected_option_index)
    except ValueError as exc:
        raise HttpError(422, str(exc)) from exc
    return {
        "is_correct": attempt.is_correct,
        "selected_option_index": attempt.selected_option_index,
        "correct_option_index": quiz.correct_option_index,
        "explanation": quiz.explanation,
    }


@api.delete("/quizzes/{quiz_id}")
def delete_quiz(request, quiz_id: UUID):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if not can_delete_quiz(quiz):
        raise HttpError(409, "只能删除最近一轮题目")
    quiz.status = Quiz.Status.ARCHIVED
    quiz.save(update_fields=["status"])
    return {"deleted": True}
