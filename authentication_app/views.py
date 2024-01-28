from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from authentication_app.mixins import AccessTokenMixin
from authentication_app.decoraters import access_token_required


# Protected View Testing using Custom Mixins and Decorater
class FetchData(AccessTokenMixin, APIView):
    @access_token_required
    def get(self, request):
        return Response(
            {"success": True, "message": "Access Granted!"},
            status=status.HTTP_200_OK,
        )


# Logout View
class LogoutView(AccessTokenMixin, APIView):
    """
    This Function Checks BlackLists the Refresh_Token and Delete both cookies i.e. access_token & refresh_token
    """

    def post(self, request, *args, **kwargs):
        # Fetchign the refresh_token from COOKIE
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token == None:
            return Response(
                {"success:": False, "error": "User not Logged In!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            # Blacklist the refresh token
            RefreshToken(refresh_token).blacklist()

            # Clear cookies
            response = Response({"success": True, "message": "Logout Success"})
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response

        except Exception as e:
            return Response(
                {"success:": False, "error": f"Logout failed. {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


import time, threading
from django.conf import settings


# Login View
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    This Function Authenticates the User LOGIN and Creates 2 Cookies that stores access_token & refresh_token
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        # countdown() function is for testing the jwt access token expiry
        def countdown():
            for i in range(settings.ACCESS_TOKEN_LIFETIME + 1):
                print(i)
                time.sleep(1)

        countdown_thread = threading.Thread(target=countdown)
        countdown_thread.start()

        # Customize the response to set tokens in cookies
        if "access" and "refresh" in response.data:
            access_token = response.data["access"]
            refresh_token = response.data["refresh"]

            # Set the access token in a cookie
            response.set_cookie(
                "access_token", access_token, httponly=True, secure=True
            )

            # Set the refresh token in a cookie
            response.set_cookie(
                "refresh_token", refresh_token, httponly=True, secure=True
            )

        return response
