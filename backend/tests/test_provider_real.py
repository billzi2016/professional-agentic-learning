import pytest

from apps.providers.models import ProviderHealthCheck
from apps.providers.services import get_chat_provider, run_provider_health_check


@pytest.mark.django_db
def test_real_provider_health_check():
    check = run_provider_health_check()

    assert check.status == ProviderHealthCheck.Status.HEALTHY
    assert check.latency_ms is not None
    assert check.error_message == ""


@pytest.mark.django_db
def test_real_provider_stream_chat_returns_content():
    provider = get_chat_provider()
    chunks = []

    # 这里故意实测当前 env 指向的 provider，不做 mock。
    # 如果 Ollama/OpenRouter/vLLM/SGLang 没启动，测试应该失败，方便尽早暴露环境问题。
    for delta in provider.stream_chat(
        [
            {"role": "system", "content": "只输出 JSON。"},
            {"role": "user", "content": "输出 {\"ok\": true}，不要解释。"},
        ]
    ):
        chunks.append(delta)
        if len("".join(chunks)) >= 8:
            break

    assert "".join(chunks).strip()
