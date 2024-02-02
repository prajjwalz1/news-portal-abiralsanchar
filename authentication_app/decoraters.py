from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from authentication_app.mixins import AccessTokenMixin
from authentication_app.models import CustomUserModel
import jwt
from django.conf import settings


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


# This Decorator validates if the requesting user is either staff/admin or normal user.
def staff_admin_required(view_func):
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
            access_token = request.COOKIES.get("access_token")
            if not access_token:
                return Response(
                    {"success:": False, "error": "ACCESS DENIED! User not Logged-In"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            try:
                decoded_access_token = jwt.decode(
                    access_token,
                    settings.SIMPLE_JWT_SECRET_KEY,
                    algorithms=[settings.SIMPLE_JWT_ALGORITHM],
                )
                user_id = decoded_access_token["user_id"]
                user_object = CustomUserModel.objects.get(pk=user_id)

                # If the user is not staff or superuser then Deny access
                if not (user_object.is_staff or user_object.is_superuser):
                    return Response(
                        {
                            "success": False,
                            "error": "ACCESS DENIED! You do not have required permission.",
                        },
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            except jwt.ExpiredSignatureError:
                return Response(
                    {"success": False, "error": "Access token has expired."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            except jwt.InvalidTokenError:
                return Response(
                    {"success": False, "error": "Invalid access token."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            # response = AccessTokenMixin.check_access_token(self, request)
            # if response:
            #     return response
            return view_func(self, request, *args, **kwargs)

    return wrapper
