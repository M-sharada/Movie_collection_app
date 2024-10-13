from django.utils.deprecation import MiddlewareMixin

class RequestCounterMiddleware(MiddlewareMixin):
    request_count = 0

    def process_request(self, request):
        RequestCounterMiddleware.request_count += 1

    @staticmethod
    def get_request_count():
        return RequestCounterMiddleware.request_count

    @staticmethod
    def reset_request_count():
        RequestCounterMiddleware.request_count = 0
