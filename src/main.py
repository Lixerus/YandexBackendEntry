from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.middleware import Middleware
import uvicorn
from .disk.router import router as disk_router
from .disk.exceptions import Error, DiskItemException
from contextlib import asynccontextmanager
from .database import create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # await delete_tables()
    await create_tables()
    yield

middlewares = [
    Middleware(TrustedHostMiddleware, allowed_hosts=['*']),
    Middleware(CORSMiddleware, allow_origins = ['*'], allow_methods = ['*'])
]

app = FastAPI(lifespan=lifespan, middleware=middlewares)
app.include_router(disk_router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(content=Error(code=400, message="Validation Failed").model_dump(), status_code=400)

@app.exception_handler(DiskItemException)
async def disk_element_exception_handler(request: Request, exc: DiskItemException):
    exc_code = exc.status_code
    msg = "Error occured"
    if exc_code == 400:
        msg = "Validation Failed"
    elif exc_code == 404:
        msg = "Item not found"
    return JSONResponse(content=Error(code=exc_code, message=msg).model_dump(),status_code=exc_code)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)