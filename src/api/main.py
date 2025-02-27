import json

from typing import List
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from uuid import uuid4
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

chat = ChatOpenAI(temperature=0.7)
app = FastAPI()

# Templates
templates = Jinja2Templates(directory="src/frontend/templates")

# In-memory storage (replace with a database in a real application)
datasets = []
messages = {}


class Message(BaseModel):
    role: str
    content: str


class Dataset(BaseModel):
    id: str
    name: str
    messages: List[Message] = []


# In-memory storage
datasets: List[Dataset] = []


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/create-dataset")
async def create_dataset(request: Request):
    dataset_id = str(uuid4())
    dataset_name = f"Dataset {len(datasets) + 1}"
    new_dataset = Dataset(id=dataset_id, name=dataset_name, messages=[])
    datasets.append(new_dataset)
    return templates.TemplateResponse(
        "dataset_item.html", {"request": request, "dataset": new_dataset}
    )


@app.get("/get-datasets")
async def get_datasets(request: Request):
    return templates.TemplateResponse(
        "datasets_list.html", {"request": request, "datasets": datasets}
    )


@app.get("/select-dataset/{dataset_id}", response_class=HTMLResponse)
async def select_dataset(request: Request, dataset_id: str):
    dataset = next((d for d in datasets if d.id == dataset_id), None)
    if dataset:
        return templates.TemplateResponse(
            "dataset_view.html", {"request": request, "dataset": dataset}
        )
    return HTMLResponse("Dataset not found", status_code=404)


@app.post("/add-message-row")
async def add_message_row(request: Request):
    return templates.TemplateResponse("message_row.html", {"request": request})


@app.post("/get-ai-response/{dataset_id}")
async def get_ai_response(request: Request, dataset_id: str):
    # Get new messages from request
    data = await request.json()
    new_messages = [Message(**msg) for msg in data]

    try:
        # Find the dataset
        dataset = next((d for d in datasets if d.id == dataset_id), None)
        if not dataset:
            return HTMLResponse("Dataset not found", status_code=404)

        # Combine existing messages with new messages
        all_messages = dataset.messages + new_messages

        # Prepare messages for LangChain
        langchain_messages = []
        for msg in all_messages:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                langchain_messages.append(SystemMessage(content=msg.content))

        # Call ChatGPT API using LangChain
        ai_response = chat(langchain_messages)

        # Get AI response
        ai_message = Message(role="assistant", content=ai_response.content)

        # Add AI message to the list of all messages
        all_messages.append(ai_message)

        # Update dataset with all messages
        dataset.messages = all_messages

        # Return updated messages template
        return templates.TemplateResponse(
            "messages_list.html", {"request": request, "messages": all_messages}
        )

    except Exception as e:
        return HTMLResponse(f"Error: {str(e)}", status_code=500)


@app.post("/save-to-dataset/{dataset_id}")
async def save_to_dataset(request: Request, dataset_id: str):
    data = await request.json()
    messages = [Message(**msg) for msg in data]

    dataset = next((d for d in datasets if d.id == dataset_id), None)
    if dataset:
        dataset.messages = dataset.messages + messages

        # Save to JSONL file
        save_to_jsonl(dataset)

        return JSONResponse(
            content={"status": "success", "message": "Dataset saved successfully"}
        )

    return JSONResponse(
        content={"status": "error", "message": "Dataset not found"}, status_code=404
    )


def save_to_jsonl(dataset: Dataset):
    jsonl_data = {
        "messages": [
            {"role": msg.role, "content": msg.content} for msg in dataset.messages
        ]
    }

    filename = f"dataset_{dataset.name}.jsonl"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(jsonl_data, f, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving dataset to JSONL: {str(e)}")
