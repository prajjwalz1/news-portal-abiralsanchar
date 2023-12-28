from functools import wraps


# This Decorater wraps the Protected Views
# Only Users with Valid access_token are further continued
def access_token_required(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        response = self.check_access_token(request)
        if response:
            return response
        return view_func(self, request, *args, **kwargs)

    return wrapper
