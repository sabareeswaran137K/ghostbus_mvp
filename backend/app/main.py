import asyncio
import json
import random
import time
from typing import List, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# --- FastAPI App ---
app = FastAPI(title="GhostBus India", version="1.0.0")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Connection Manager for WebSockets ---
class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: Any):
        data = json.dumps(message)
        for ws in self.active:
            try:
                await ws.send_text(data)
            except Exception:
                self.disconnect(ws)

manager = ConnectionManager()

# --- State coordinates (capitals or main cities) ---
state_coords = {
    "Karnataka": (12.9716, 77.5946),   # Bengaluru
    "Maharashtra": (19.0760, 72.8777), # Mumbai
    "Tamil Nadu": (13.0827, 80.2707),  # Chennai
    "Delhi": (28.7041, 77.1025),       # Delhi
    "West Bengal": (22.5726, 88.3639), # Kolkata
    "Kerala": (8.5241, 76.9366),       # Thiruvananthapuram
    "Gujarat": (23.0225, 72.5714),     # Ahmedabad
    "Punjab": (31.1471, 75.3412),      # Ludhiana
    "Rajasthan": (26.9124, 75.7873),   # Jaipur
    "Bihar": (25.5941, 85.1376),       # Patna,
}

# --- Generate buses (5 per state) ---
fake_buses = []
bus_counter = 100

for state, (lat, lon) in state_coords.items():
    for i in range(5):  # 5 buses per state
        bus = {
            "id": f"B{bus_counter}",
            "lat": lat + random.uniform(-0.05, 0.05),
            "lon": lon + random.uniform(-0.05, 0.05),
            "route": f"{state[:3].upper()}-R{i+1}",
            "speed": round(random.uniform(0, 50), 1),
            "timestamp": int(time.time()),
        }
        fake_buses.append(bus)
        bus_counter += 1

# --- Background Simulator ---
async def simulator_loop():
    while True:
        now = int(time.time())
        for bus in fake_buses:
            # Random small movement around city
            bus["lat"] += random.uniform(-0.01, 0.01)
            bus["lon"] += random.uniform(-0.01, 0.01)

            # Random speed: sometimes bus stops completely
            if random.random() < 0.2:  # 20% chance to stop
                bus["speed"] = 0
            else:
                bus["speed"] = round(random.uniform(5, 50), 1)

            bus["timestamp"] = now
            bus["is_ghost"] = bus["speed"] < 1

            # Send live update
            await manager.broadcast({"type": "bus.update", "data": bus})

        await asyncio.sleep(3)

@app.on_event("startup")
async def startup():
    asyncio.create_task(simulator_loop())

# --- Routes ---
@app.get("/")
async def root():
    return {"message": "🚍 GhostBus India Backend is running!"}

@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/buses")
async def get_buses():
    return {"buses": [bus.copy() for bus in fake_buses]}

@app.get("/buses/{bus_id}")
async def get_bus(bus_id: str):
    for bus in fake_buses:
        if bus["id"] == bus_id:
            return bus.copy()
    return {"error": "Bus not found"}

# --- WebSocket ---
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
