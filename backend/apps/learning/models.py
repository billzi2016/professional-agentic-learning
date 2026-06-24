import uuid

from django.db import models


class LearningCard(models.Model):
    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"
        SUPERSEDED = "superseded", "Superseded"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        "conversations.Conversation",
        on_delete=models.CASCADE,
        related_name="learning_cards",
    )
    message = models.OneToOneField(
        "conversations.Message",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="learning_card",
    )
    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=120)
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER)
    markdown = models.TextField()
    summary = models.TextField(blank=True)
    order_index = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order_index", "created_at"]
        indexes = [
            models.Index(fields=["conversation", "status", "order_index"]),
        ]

    def __str__(self) -> str:
        return self.title


class Quiz(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"
        SUPERSEDED = "superseded", "Superseded"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        "conversations.Conversation",
        on_delete=models.CASCADE,
        related_name="quizzes",
    )
    learning_card = models.ForeignKey(
        LearningCard,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="quizzes",
    )
    question = models.TextField()
    options = models.JSONField()
    correct_option_index = models.PositiveSmallIntegerField()
    explanation = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [
            models.Index(fields=["conversation", "status", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.question[:60]


class QuizAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    selected_option_index = models.PositiveSmallIntegerField()
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self) -> str:
        return f"{self.quiz_id}: {self.selected_option_index}"
