import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from db import engine
from sqlmodel import SQLModel
from routers import cars, web
from routers.cars import BadTripException

#  app = FastAPI(title="Car Sharing")
app = FastAPI(title="Car Sharing")
app.include_router(web.router)
app.include_router(cars.router)

app.include_router(cars.router)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.exception_handler(BadTripException)
async def unicorn_exception_handler(request: Request, exc: BadTripException):
    return JSONResponse(status_code=HTTP_422_UNPROCESSABLE_ENTITY, content={"message": "Bad Trip"})




if __name__ == "__main__":
    uvicorn.run("carsharing:app", reload=True)