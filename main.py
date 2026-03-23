from contextlib import asynccontextmanager
from fastapi import FastAPI
from ocr_service import video_service  # Import your singleton instance


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    # 1. This tells the service to spawn its "Manager Thread"
    # 2. This also initializes your Thread and Process Pools
    video_service.start_manager()

    print("Background services are now running.")

    yield  # The server stays here while it's "Online" and handling requests

    # --- SHUTDOWN ---
    # 1. This stops the manager loop
    # 2. This tells the pools to stop accepting new work
    # 3. This waits for active OCR processes to finish before closing
    video_service.shutdown()
    print("Background services shut down cleanly.")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
