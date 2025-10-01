from fastapi import FastAPI

app = FastAPI(title="Async Job Queue Demo")


@app.get("/")
def read_root():
    return {"status": "ok"}
