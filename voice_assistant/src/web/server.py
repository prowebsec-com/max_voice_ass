from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.core.brain import Brain
from starlette.responses import FileResponse, JSONResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="web/public"), name="static")

class AskBody(BaseModel):
    text: str

brain = Brain()

@app.get("/")
def index():
    return FileResponse("web/public/index.html")

@app.get("/favicon.ico")
def favicon():
    return JSONResponse({}, status_code=204)

@app.post("/api/assist")
def assist(body: AskBody):
    reply = brain.think(body.text or "")
    if not reply or not reply.strip():
        reply = "I'm here and listening."
    return {"reply": reply}
