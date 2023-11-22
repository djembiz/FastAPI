import uvicorn
from fastapi import FastAPI
from db import engine
from sqlmodel import SQLModel
from routers import cars

app = FastAPI(title="Car Sharing")
app.include_router(cars.router)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    uvicorn.run("carsharing:app", reload=True)