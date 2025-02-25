from fastapi.testclient import TestClient
from main import app, datasets
import pytest

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_datasets():
    datasets.clear()


def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "Dataset Manager" in response.text


def test_create_dataset():
    response = client.post("/create-dataset")
    assert response.status_code == 200
    assert "Dataset 1" in response.text
    assert len(datasets) == 1


def test_get_datasets():
    client.post("/create-dataset")
    client.post("/create-dataset")
    response = client.get("/get-datasets")
    assert response.status_code == 200
    assert "Dataset 1" in response.text
    assert "Dataset 2" in response.text


def test_select_dataset():
    create_response = client.post("/create-dataset")
    dataset_id = datasets[0].id
    response = client.get(f"/select-dataset/{dataset_id}")
    assert response.status_code == 200
    assert datasets[0].name in response.text


def test_select_nonexistent_dataset():
    response = client.get("/select-dataset/nonexistent-id")
    assert response.status_code == 404
    assert "Dataset not found" in response.text


def test_add_message_row():
    response = client.post("/add-message-row")
    assert response.status_code == 200
    assert "message-row" in response.text


def test_save_to_dataset():
    client.post("/create-dataset")
    dataset_id = datasets[0].id
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]
    response = client.post(f"/save-to-dataset/{dataset_id}", json=messages)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    assert len(datasets[0].messages) == 2


def test_save_to_nonexistent_dataset():
    response = client.post("/save-to-dataset/nonexistent-id", json=[])
    assert response.status_code == 200
    assert response.json() == {"status": "error", "message": "Dataset not found"}
