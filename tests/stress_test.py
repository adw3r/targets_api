from locust import HttpUser, task


class QuickstartUser(HttpUser):
    host = "http://127.0.0.1:8181"

    @task
    def test_get_target(self):
        self.client.get("/targets/pobcasn23?method=pop")
