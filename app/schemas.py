from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class RoomCreate(BaseModel):
    name: str
    capacity: int


class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    capacity: int


class ReservationCreate(BaseModel):
    room_id: int
    customer_name: str
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def check_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio")
        return self


class ReservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    customer_name: str
    start_time: datetime
    end_time: datetime
