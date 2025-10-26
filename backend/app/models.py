from pydantic import BaseModel
from typing import Optional

class BusUpdate(BaseModel):
    id: str
    lat: float
    lon: float
    route: Optional[str] = None
    speed: Optional[float] = None  # km/h
    timestamp: int
    is_ghost: bool = False
