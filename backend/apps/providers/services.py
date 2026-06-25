from __future__ import annotations

import time
from collections.abc import Iterator
from dataclasses import dataclass

from django.conf import settings
from openai import OpenAI

from apps.providers.models import ProviderConfig, ProviderHealthCheck


@dataclass(frozen=True)
class ProviderHealthResult:
    status: str
    latency_ms: int | None = None
    error: str | None = None


def get_active_provider_config() -> ProviderConfig:
    config = ProviderConfig.objects.filter(is_active=True).first()
    if config:
        return config

    # 第一次启动时从 env 落一份默认配置到数据库，避免前端状态接口无数据。
    return ProviderConfig.objects.create(
        name=settings.AI_PROVIDER,
        provider_type=settings.AI_PROVIDER,
        base_url=settings.AI_BASE_URL,
        model=settings.AI_MODEL,
        api_key=settings.AI_API_KEY,
        is_active=True,
    )


class OpenAICompatibleProvider:
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.client = OpenAI(
            base_url=config.base_url,
            api_key=config.api_key or "EMPTY",
        )

    def stream_chat(self, messages: list[dict[str, str]]) -> Iterator[str]:
        stream = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            stream=True,
            temperature=settings.AI_GENERATION_TEMPERATURE,
            # 学习卡片必须“一次学一点”。这里给模型输出加上硬上限，
            # 避免它把完整课程一次性展开。
            max_tokens=settings.AI_GENERATION_MAX_TOKENS,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def health_check(self) -> ProviderHealthResult:
        started_at = time.monotonic()
        try:
            self.client.models.list()
        except Exception as exc:  # pragma: no cover - depends on local provider.
            return ProviderHealthResult(
                status=ProviderHealthCheck.Status.UNHEALTHY,
                error=str(exc)[:500],
            )

        return ProviderHealthResult(
            status=ProviderHealthCheck.Status.HEALTHY,
            latency_ms=int((time.monotonic() - started_at) * 1000),
        )


def get_chat_provider(config: ProviderConfig | None = None) -> OpenAICompatibleProvider:
    # Ollama、OpenRouter、vLLM、SGLang 都优先走 OpenAI-compatible。
    # 这样 provider 差异集中在 base_url/model/api_key，不把 HTTP 细节散落到业务代码里。
    return OpenAICompatibleProvider(config or get_active_provider_config())


def run_provider_health_check(config: ProviderConfig | None = None) -> ProviderHealthCheck:
    provider_config = config or get_active_provider_config()
    result = get_chat_provider(provider_config).health_check()
    return ProviderHealthCheck.objects.create(
        provider_config=provider_config,
        status=result.status,
        latency_ms=result.latency_ms,
        error_message=result.error or "",
    )
