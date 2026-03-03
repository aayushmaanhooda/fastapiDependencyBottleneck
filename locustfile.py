import random
import string
from locust import HttpUser, task, between


def rand_str(n=8) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=n))


class TodoUser(HttpUser):
    # Each simulated user waits 0.1–0.5s between requests
    wait_time = between(0.1, 0.5)

    @task(3)
    def list_todos(self):
        self.client.get("/todos")

    @task(1)
    def create_todo(self):
        self.client.post(
            "/todos",
            json={"task": f"task-{rand_str()}", "description": f"desc-{rand_str()}"},
        )
