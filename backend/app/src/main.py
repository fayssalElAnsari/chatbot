from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import setup_app
from src.routers import chat, root

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Setup app configurations
setup_app(app)

# Include routers
app.include_router(chat.router)
app.include_router(root.router)

def get_app():
    return app
