from datetime import datetime
from typing import Optional
import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import json
from schemas import load_db, save_db, CarInput, CarOutput, TripInput, TripOutput

app = FastAPI(title="Car Sharing")

db = load_db()

@app.get("/")
def welcome(name):
    """Return a friendly Welcome page"""
    return {"message": f"Welcome,{name} to the Car Sharing Service!"}


@app.get("/api/cars")
def get_cars(size: Optional[str] = None, doors: Optional[int] = None) -> list:
    result = db
    if size:
        if doors:
            result = [car for car in db if (car.size == size and car.doors >= doors)]
    return result


@app.get("/api/cars/{id}")
def car_by_id(id: int):
    for car in db:
        if car.id == id:
            return car
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}.")


@app.post("/api/cars/", response_model=CarOutput)
def add_car(car: CarInput) -> CarOutput:
    new_car = CarOutput(size=car.size,
                        doors=car.doors, fuel=car.fuel,
                        transmission=car.transmission,
                        id=len(db)+1)
    db.append(new_car)
    save_db(db)
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

if __name__ == "__main__":
    uvicorn.run("carsharing:app",reload=True)
