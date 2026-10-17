from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import threading

app = FastAPI()

# Global routing table
ROUTING_TABLE = {'A': 9001}

class Route(BaseModel):
    channel: str
    port: int

@app.post("/add_route")
async def add_route(route: Route):
    ROUTING_TABLE[route.channel] = route.port
    return {"message": f"Channel {route.channel} mapped to {route.port}"}

@app.get("/routes")
async def get_routes():
    return ROUTING_TABLE

# You can run the existing asyncio server in a background thread 
# or integrate it directly into FastAPI's startup event.
