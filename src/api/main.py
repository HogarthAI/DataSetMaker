from typing import List
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from uuid import uuid4
from pydantic import BaseModel

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="src/frontend/static"), name="static")

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


@app.post("/save-to-dataset/{dataset_id}")
async def save_to_dataset(request: Request, dataset_id: str):
    data = await request.json()
    messages = [Message(**msg) for msg in data]
    dataset = next((d for d in datasets if d.id == dataset_id), None)
    if dataset:
        dataset.messages = messages
        return {"status": "success"}
    return {"status": "error", "message": "Dataset not found"}
