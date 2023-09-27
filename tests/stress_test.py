from locust import HttpUser, task


class QuickstartUser(HttpUser):
    host = "http://10.107.8.10:8181"

    @task
    def test_get_target(self):
        self.client.get("/targets/pobcasn23?method=pop")
