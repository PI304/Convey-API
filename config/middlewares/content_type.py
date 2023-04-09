from django.utils.deprecation import MiddlewareMixin


class ContentTypeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path in ["/api/auth/login/app", "/api/auth/signup/app"]:
            request.META["CONTENT_TYPE"] = "application/octet-stream"
        return None
