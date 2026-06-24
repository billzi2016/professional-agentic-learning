import pytest
from django.test import Client

from apps.conversations.models import Conversation


@pytest.mark.django_db
def test_health_api_is_available():
    client = Client()
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.django_db
def test_write_api_requires_csrf_token():
    conversation = Conversation.objects.create(title="SQL 学习")
    client = Client(enforce_csrf_checks=True)

    response = client.post(
        f"/api/conversations/{conversation.id}/messages",
        data={"content": "开始学习 SQL"},
        content_type="application/json",
    )

    assert response.status_code == 403
