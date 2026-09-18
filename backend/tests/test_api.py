from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.repositories.document import get_document_by_id
from app.core.constants import DocumentStatus
import uuid

client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "DocuMind API is running"
    }
def test_register_user():
    email = f"pytest_{uuid.uuid4().hex[:8]}@example.com"

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == email
    assert "id" in data
def test_register_duplicate_user():
    response = client.post(
        "/auth/register",
        json={
            "email": "pytest_user@example.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 400
def test_login_user():
    response = client.post(
        "/auth/login",
        json={
            "email": "pytest_new_user_2026@example.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
def test_login_invalid_password():
    response = client.post(
        "/auth/login",
        json={
            "email": "pytest_new_user_2026@example.com",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401
def test_get_current_user():
    login_response = client.post(
        "/auth/login",
        json={
            "email": "pytest_new_user_2026@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "pytest_new_user_2026@example.com"
def test_get_current_user_without_token():
    response = client.get("/auth/me")

    assert response.status_code == 401
def test_get_other_users_document():
    login_response = client.post(
        "/auth/login",
        json={
            "email": "pytest_new_user_2026@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/documents/4",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 403
def test_get_my_documents():
    login_response = client.post(
        "/auth/login",
        json={
            "email": "pytest_new_user_2026@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/documents",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    for document in data:
        assert "id" in document
        assert "filename" in document
        assert "status" in document
def test_get_nonexistent_document():
    login_response = client.post(
        "/auth/login",
        json={
            "email": "pytest_new_user_2026@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/documents/999999",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 404
def test_get_my_conversations():
    login_response = client.post(
        "/auth/login",
        json={
            "email": "pytest_new_user_2026@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/conversations",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    for conversation in data:
        assert "id" in conversation
        assert "document_id" in conversation
        assert "title" in conversation
def test_get_conversation():
    login_response = client.post(
        "/auth/login",
        json={
            "email": "pytest_new_user_2026@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    conversations_response = client.get(
        "/conversations",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert conversations_response.status_code == 200

    conversations = conversations_response.json()

    if not conversations:
        return

    conversation_id = conversations[0]["id"]

    response = client.get(
        f"/conversations/{conversation_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == conversation_id
    assert "document_id" in data
    assert "title" in data
    assert "messages" in data
    assert isinstance(data["messages"], list)
def test_get_other_users_conversation():
    login_response = client.post(
        "/auth/login",
        json={
            "email": "pytest_new_user_2026@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.get(
        "/conversations/1",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    # Conversation 1 belongs to another user
    assert response.status_code == 403
def test_update_conversation_title():
    login_response = client.post(
        "/auth/login",
        json={
            "email": "pytest_new_user_2026@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    conversations_response = client.get(
        "/conversations",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert conversations_response.status_code == 200

    conversations = conversations_response.json()

    if not conversations:
        return

    conversation_id = conversations[0]["id"]

    response = client.patch(
        f"/conversations/{conversation_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Updated Test Conversation"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == conversation_id
    assert data["title"] == "Updated Test Conversation"
def test_delete_conversation():
    login_response = client.post(
        "/auth/login",
        json={
            "email": "pytest_new_user_2026@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    conversations_response = client.get(
        "/conversations",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert conversations_response.status_code == 200

    conversations = conversations_response.json()

    if not conversations:
        return

    conversation_id = conversations[0]["id"]

    delete_response = client.delete(
        f"/conversations/{conversation_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "message": "Conversation deleted successfully"
    }

    # Verify it no longer exists
    get_response = client.get(
        f"/conversations/{conversation_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert get_response.status_code == 404
def test_chat_with_document():
    login_response = client.post(
        "/auth/login",
        json={
            "email": "pytest_new_user_2026@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    documents_response = client.get(
        "/documents",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert documents_response.status_code == 200

    documents = documents_response.json()

    indexed_documents = [
        document
        for document in documents
        if document["status"] == "indexed"
    ]

    if not indexed_documents:
        return

    document = indexed_documents[0]

    response = client.post(
        "/chat",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "question": "What is this document about?",
            "document_id": document["id"],
            "top_k": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == document["id"]
    assert data["filename"] == document["filename"]
    assert data["question"] == "What is this document about?"
    assert data["answer"]
    assert data["conversation_id"] > 0
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0

    for source in data["sources"]:
        assert "page_number" in source
        assert "similarity" in source
        assert "rerank_score" in source
        assert "snippet" in source
def test_chat_with_other_users_document():
    login_response = client.post(
        "/auth/login",
        json={
            "email": "pytest_new_user_2026@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.post(
        "/chat",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "question": "What is this document about?",
            "document_id": 30,
            "top_k": 3,
        },
    )

    assert response.status_code == 403
def test_chat_with_nonexistent_document():
    login_response = client.post(
        "/auth/login",
        json={
            "email": "pytest_new_user_2026@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.post(
        "/chat",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "question": "What is this document about?",
            "document_id": 999999,
            "top_k": 3,
        },
    )

    assert response.status_code == 404
def test_get_document_status():
    login_response = client.post(
        "/auth/login",
        json={
            "email": "pytest_new_user_2026@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    documents_response = client.get(
        "/documents",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert documents_response.status_code == 200

    documents = documents_response.json()

    if not documents:
        return

    document = documents[0]

    response = client.get(
        f"/documents/{document['id']}/status",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == document["id"]
    assert data["filename"] == document["filename"]
    assert data["status"] == document["status"]
def test_chat_with_processing_document():
    login_response = client.post(
        "/auth/login",
        json={
            "email": "pytest_new_user_2026@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    documents_response = client.get(
        "/documents",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert documents_response.status_code == 200

    documents = documents_response.json()

    indexed_documents = [
        document
        for document in documents
        if document["status"] == DocumentStatus.INDEXED.value
    ]

    if not indexed_documents:
        return

    document_id = indexed_documents[0]["id"]

    db = SessionLocal()

    try:
        document = get_document_by_id(
            db=db,
            document_id=document_id,
        )

        assert document is not None

        document.status = DocumentStatus.PROCESSING.value
        db.commit()

        response = client.post(
            "/chat",
            headers={
                "Authorization": f"Bearer {token}"
            },
            json={
                "question": "What is this document about?",
                "document_id": document_id,
                "top_k": 3,
            },
        )

        assert response.status_code == 409

        data = response.json()

        assert data["detail"] == (
            "Document is not ready for chat. "
            "Current status: processing"
        )

    finally:
        document.status = DocumentStatus.INDEXED.value # type: ignore
        db.commit()
        db.close()
def test_chat_handles_llm_failure(monkeypatch):
    login_response = client.post(
        "/auth/login",
        json={
            "email": "pytest_new_user_2026@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    documents_response = client.get(
        "/documents",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert documents_response.status_code == 200

    documents = documents_response.json()

    indexed_documents = [
        document
        for document in documents
        if document["status"] == "indexed"
    ]

    if not indexed_documents:
        return

    document = indexed_documents[0]

    def mock_generate_answer(*args, **kwargs):
        raise RuntimeError("Simulated LLM failure")

    monkeypatch.setattr(
        "app.api.chat.generate_answer",
        mock_generate_answer,
    )

    response = client.post(
        "/chat",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "question": "What is this document about?",
            "document_id": document["id"],
            "top_k": 3,
        },
    )

    assert response.status_code == 500

    data = response.json()

    assert data["detail"] == "Failed to generate an answer"