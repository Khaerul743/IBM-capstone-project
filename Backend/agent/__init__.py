from agent.workflow import Agent


class MyAgent:
    def __init__(self, thread_id: str):
        self.agent = Agent()
        self.thread_id = thread_id

    def execute(self, user_query: str):
        if not user_query:
            raise RuntimeError("User query is required")
        return self.agent.run({"user_query": user_query}, self.thread_id)
