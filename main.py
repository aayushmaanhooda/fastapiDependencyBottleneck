from fastapi import FastAPI

app = FastAPI(title="Dependency Bottleneck Test")

@app.get("/")
def root():
    return {
        "message" : "I am root"
    }

@app.get("/health")
def root():
    return {
        "message" : "Server is healthy"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, relaod=True)
