from locust import HttpUser, task, between

class AirportServiceUser(HttpUser):
    host = "http://127.0.0.1:8001"
    wait_time = between(1, 3)

    @task(3)
    def list_airports(self):
        self.client.get("/airports", name="GET /airports")

    @task(1)
    def get_airport_by_id(self):
        self.client.get("/airports/1", name="GET /airports/id")

    @task(1)
    def get_airport_by_iata(self):
        self.client.get("/airports/iata/BOG", name="GET /airports/iata/BOG")