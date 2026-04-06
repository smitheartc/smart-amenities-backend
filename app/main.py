import json
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.services.terminal_d_graph_service import AirportMapService
from app.api.routes import map  # Your router import
from app.models.models import Base   # Adjust import path as needed based on where Models.py lives
from app.core.database import engine

def start():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

BASE_DIR = Path(__file__).resolve().parent.parent
MOCK_DATA_PATH = BASE_DIR / "data" / "mock_airport_nodes.json"

@asynccontextmanager
async def lifespan(app: FastAPI):

    Base.metadata.create_all(bind=engine)


    # 1. Load the data
    with open(MOCK_DATA_PATH, "r") as file:
        airport_data = json.load(file)
        
    # 2. Attach the service to the FastAPI app state!
    app.state.map_service = AirportMapService(airport_data)
    
    yield 
    
    # 3. Clean up
    app.state.map_service = None

app = FastAPI(lifespan=lifespan)

# Include your router AFTER the app is created
app.include_router(map.router, tags=["Airport Map"])