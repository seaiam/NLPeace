from django.contrib.auth.models import User

class AnonymousProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.is_anonymous:
            request.user.username = request.user.profile.anonymous_username

        response = self.get_response(request)

        return response