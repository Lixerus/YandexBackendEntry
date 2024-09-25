from fastapi import FastAPI, Depends
import uvicorn
from tasks.router import router as tasks_router
from disk.router import router as disk_router

from contextlib import asynccontextmanager

from database import create_tables, delete_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Startup")
    await delete_tables()
    print("Deleted tables")
    await create_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(tasks_router)
app.include_router(disk_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)