from locust import HttpLocust, TaskSet, task

class UserBehavior(TaskSet):
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        """self.ask()"""

    def ask(self):
        self.client.get("/mlchat/answer?domain=schoolA&msg=hi")

    @task(2)
    def ask1(self):
        self.client.get("/mlchat/answer?domain=schoolA&msg=hi")

    @task(1)
    def ask2(self):
        self.client.get("/mlchat/answer?domain=schoolA&msg=hi")

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 1000
    max_wait = 2000
