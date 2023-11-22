from typing import Sequence, Type
from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select
from db import get_session
from schemas import Car, CarInput, Trip, TripInput, CarOutput


router = APIRouter()


@router.get("/api/cars")
def get_cars(size: str | None = None, doors: int | None = None,
             session: Session = Depends(get_session)) -> Sequence[Car]:
    query = select(Car)
    if size:
        query = query.where(Car.size == size)
    if doors:
        query = query.where(Car.doors >= doors)
    return session.exec(query).all()


@router.get("/api/cars/{id}", response_model=Car)  # Display only car info without trips
# @app.get("/api/cars/{id}", response_model=CarOutput)  # To view Trips for each car
def car_by_id(id: int, session: Session = Depends(get_session)) -> Type[Car]:
    car = session.get(Car, id)
    if car:
        return car
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}.")


@router.post("/api/cars/", response_model=Car)
def add_car(car_input: CarInput, session: Session = Depends(get_session)) -> Car:
    new_car = Car.from_orm(car_input)
    session.add(new_car)
    session.commit()
    session.refresh(new_car)
    return new_car


@router.post("/api/cars/{car_id}/trips", response_model=Trip)
def add_trip(car_id: int, trip_input: TripInput, session: Session = Depends(get_session)) -> Trip:
    car = session.get(Car, car_id)
    if car:
        new_trip = Trip.from_orm(trip_input, update={"car_id": car_id})
        car.trips.append(new_trip)
        session.commit()
        session.refresh(new_trip)
        return new_trip
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={car_id}")


@router.delete("/api/cars/{id}", status_code=204)
def remove_car(id: int, session: Session = Depends(get_session)) -> None:
    car = session.get(Car, id)
    if car:
        session.delete(car)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"No Car with ID={id}")


@router.put("/api/cars/{id}", response_model=CarOutput)
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
