from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from authentication_app.mixins import AccessTokenMixin


# This Decorater wraps the Protected Views
# Only Users with Valid access_token are further continued
def access_token_required(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        isSessionExpired = getattr(request, "isSessionExpired", False)
        if isSessionExpired:
            # Refresh/Access Token has Expired or Invalid || Access Token was Invalid so,end the SESSION
            response = Response(
                {"message": "Session Expired! Login Again to Continue..."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response
        else:
            """
            This Function is executed because of either reasons :
            -All the Tokens are all Valid
            -Its a Guest user trying to access the Protected Views so Validate that using Access/Refresh Token in Custom Mixins. We dont validate Guest user on Middleware so,we have add another authentication layer on Custom Mixins.
            """
            response = AccessTokenMixin.check_access_token(self, request)
            if response:
                return response
            return view_func(self, request, *args, **kwargs)

    return wrapper
