from locust import HttpUser, task, between

class ItineraryServiceUser(HttpUser):
    host = "http://127.0.0.1:8002"
    wait_time = between(1, 3)

    @task(3)
    def list_itineraries(self):
        self.client.get("/itineraries", name="GET /itineraries")

    @task(1)
    def get_itinerary_by_id(self):
        self.client.get("/itineraries/1", name="GET /itineraries/id")