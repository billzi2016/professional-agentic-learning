import uuid

from django.db import models


class ProviderConfig(models.Model):
    class ProviderType(models.TextChoices):
        OLLAMA = "ollama", "Ollama"
        OPENROUTER = "openrouter", "OpenRouter"
        OPENAI_COMPATIBLE = "openai_compatible", "OpenAI Compatible"
        VLLM = "vllm", "vLLM"
        SGLANG = "sglang", "SGLang"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=80, default="ollama")
    provider_type = models.CharField(
        max_length=40,
        choices=ProviderType.choices,
        default=ProviderType.OLLAMA,
    )
    base_url = models.URLField(default="http://127.0.0.1:11434/v1")
    model = models.CharField(max_length=160, default="gpt-oss:120b")
    api_key = models.CharField(max_length=500, blank=True, default="ollama")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_active", "-updated_at"]

    def __str__(self) -> str:
        return f"{self.provider_type}:{self.model}"


class ProviderHealthCheck(models.Model):
    class Status(models.TextChoices):
        HEALTHY = "healthy", "Healthy"
        UNHEALTHY = "unhealthy", "Unhealthy"
        CHECKING = "checking", "Checking"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider_config = models.ForeignKey(
        ProviderConfig,
        on_delete=models.CASCADE,
        related_name="health_checks",
    )
    status = models.CharField(max_length=20, choices=Status.choices)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True, default="")
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-checked_at"]

    def __str__(self) -> str:
        return f"{self.provider_config_id}: {self.status}"
