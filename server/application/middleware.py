from werkzeug.wrappers import Request, Response


class middleware():

    def __init__(self, app):
        self.app = app


    def __call__(self, environment, start_response):
        request = Request(environment)

        print("Stuck in the middle with you")

        return self.app(environment, start_response)
