import uvicorn
from agent import MyAgent
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


agent = MyAgent("thread_123")

class UserMessage(BaseModel):
    user_message: str


@app.get("/")
def test():
    return {"message": "Hello world"}


@app.post("/api/agent")
def callAgent(message: UserMessage):
    if not message:
        return {"Error": "message is required"}

    try:
        response = agent.execute(message.user_message)
        human = response["user_query"]
        ai = response["the_answer"]

        return {"user_message": human, "response": ai}
    except Exception as e:
        print(f"Terjadi error di call agent: {str(e)}")
        return {
            "user_message": message.user_message,
            "response": "Sepertinya telah terjadi error di server, mohon maaf atas ketidaknyamanannya.",
        }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
