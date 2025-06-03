from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import upload, parse, chunk, embed, chat
import os

app = FastAPI(title="Spec Assistant Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(upload.router)
app.include_router(parse.router)
app.include_router(chunk.router)
app.include_router(embed.router)
app.include_router(chat.router)

# Serve PDFs from /data
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
app.mount("/pdf", StaticFiles(directory=DATA_DIR), name="pdf")
