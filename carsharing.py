from datetime import datetime
from typing import Optional, Sequence
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import json
from schemas import load_db, save_db, CarInput, CarOutput, TripInput, TripOutput, Car
from sqlmodel import create_engine, SQLModel, Session, select

app = FastAPI(title="Car Sharing")

db = load_db()


engine = create_engine(
    url="sqlite:///carsharing.db",
    connect_args={"check_same_thread": False},
    echo=True
)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.get("/")
def welcome(name):
    """Return a friendly Welcome page"""
    return {"message": f"Welcome,{name} to the Car Sharing Service!"}


@app.get("/api/cars")
def get_cars(size: str | None = None, doors: int | None = None) -> Sequence[Car]:
    with Session(engine) as session:
        query = select(Car)
        if size:
            query = query.where(Car.size == size)
        if doors:
            query = query.where(Car.doors >= doors)
        return session.exec(query).all()


@app.get("/api/cars/{id}")
def car_by_id(id: int):
    for car in db:
        if car.id == id:
            return car
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}.")


@app.post("/api/cars/", response_model=Car)
def add_car(car_input: CarInput) -> Car:
    with Session(engine) as session:
        new_car = Car.from_orm(car_input)
        session.add(new_car)
        session.commit()
        session.refresh(new_car)
        return new_car


@app.post("/api/cars/{car_id}/trips", response_model=TripOutput)
def add_trip(car_id: int, trip: TripInput) -> TripOutput:
    matches = [car for car in db if car.id == car_id]
    if matches:
        car = matches[0]
        new_trip = TripOutput(id=len(car.trips)+1,
                              start=trip.start,
                              end=trip.end,
                              description=trip.description)
        car.trips.append(new_trip)
        save_db(db)
        return new_trip
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={car_id}")


@app.delete("/api/cars/{id}", status_code=204)
def remove_car(id: int) -> None:
    matches = [car for car in db if car.id == id]
    if matches:
        car = matches[0]
        db.remove(car)
        save_db(db)
    else:
        raise HTTPException(status_code=404, detail=f"No Car with ID={id}")

@app.put("/api/cars/{id}", response_model=CarOutput)
def change_car(id: int, new_data: CarOutput) -> CarOutput:
    matches = [car for car in db if car.id == id]
    if matches:
        car = matches[0]
        car.size=new_data.size
        car.doors=new_data.doors
        car.fuel=new_data.fuel
        car.transmission=new_data.transmission
        save_db(db)
        return car
    else:
        raise HTTPException(status_code=404, detail=f"No car with id = {id}")


@app.get("/date")
def date():
    """Return the date and time"""
    return {"date": datetime.now()}
