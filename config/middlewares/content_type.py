class ContentTypeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)

        return response

    def process_request(self, request):
        if request.path in ["/api/auth/login/app", "/api/auth/signup/app"]:
            request.META["CONTENT_TYPE"] = "application/octet-stream"
        return None
