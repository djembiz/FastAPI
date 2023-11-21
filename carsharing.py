from datetime import datetime
from typing import Optional, Sequence, Type
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import json
from schemas import CarInput, CarOutput, TripInput, TripOutput, Car, Trip
from sqlmodel import create_engine, SQLModel, Session, select

app = FastAPI(title="Car Sharing")

engine = create_engine(
    url="sqlite:///carsharing.db",
    connect_args={"check_same_thread": False},
    echo=True
)


def get_session():
    with Session(engine) as session:
        yield session


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.get("/api/cars")
def get_cars(size: str | None = None, doors: int | None = None,
             session: Session = Depends(get_session)) -> Sequence[Car]:
    query = select(Car)
    if size:
        query = query.where(Car.size == size)
    if doors:
        query = query.where(Car.doors >= doors)
    return session.exec(query).all()


@app.get("/api/cars/{id}", response_model=Car)
def car_by_id(id: int, session: Session = Depends(get_session)) -> Type[Car]:
    car = session.get(Car, id)
    if car:
        return car
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}.")


@app.post("/api/cars/", response_model=Car)
def add_car(car_input: CarInput, session: Session = Depends(get_session)) -> Car:
    new_car = Car.from_orm(car_input)
    session.add(new_car)
    session.commit()
    session.refresh(new_car)
    return new_car


@app.post("/api/cars/{car_id}/trips", response_model=Trip)
def add_trip(car_id: int, trip_input: TripInput, session: Session = Depends(get_session)) -> Trip:
    car = session.get(Car, car_id)
    if car:
        new_trip = Trip.from_orm(trip_input)
        car.trips.append(new_trip)
        session.commit()
        session.refresh(new_trip)
        return new_trip
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={car_id}")


@app.delete("/api/cars/{id}", status_code=204)
def remove_car(id: int, session: Session = Depends(get_session)) -> None:
    car = session.get(Car, id)
    if car:
        session.delete(car)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"No Car with ID={id}")


@app.put("/api/cars/{id}", response_model=CarOutput)
def change_car(id: int, new_data: CarOutput, session: Session = Depends(get_session)) -> Type[Car]:
    car = session.get(Car, id)
    if car:
        car.size = new_data.size
        car.doors = new_data.doors
        car.fuel = new_data.fuel
        car.transmission = new_data.transmission
        session.commit()
        return car
    else:
        raise HTTPException(status_code=404, detail=f"No car with id = {id}")


if __name__ == "__main__":
    uvicorn.run("carsharing:app", reload=True)