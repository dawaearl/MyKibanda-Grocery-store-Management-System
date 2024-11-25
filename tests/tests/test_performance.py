from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_products(self):
        self.client.get("/getProducts")
    
    @task
    def get_orders(self):
        self.client.get("/getAllOrders")