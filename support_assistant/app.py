from fastapi import FastAPI
from pydantic import BaseModel
from support_assistant.graph import ask
app = FastAPI(
    title="Zepto Support Assistant",
    description="Offline deterministic Zepto policy support service",
    version="1.0"
)
class AskRequest(BaseModel):
    query: str
class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: float
@app.get("/")
def root():
    return {
        "message": "Zepto Support Assistant is running"
    }
@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    response = ask(request.query)
    return response