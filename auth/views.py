from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from auth.mixins import AccessTokenMixin
from auth.decoraters import access_token_required


# Protected View Testing using Custom Mixins and Decorater
class FetchData(AccessTokenMixin, APIView):
    @access_token_required
    def get(self, request):
        return Response(
            {"success": True, "message": "Access Granted!"}, status=status.HTTP_200_OK
        )


# Logout View
class LogoutView(AccessTokenMixin, APIView):
    """
    This Function Checks BlackLists the Refresh_Token and Delete both cookies i.e. access_token & refresh_token
    """

    @access_token_required
    def post(self, request, *args, **kwargs):
        # Fetchign the refresh_token from COOKIE
        refresh_token = request.COOKIES.get("refresh_token")

        # Blacklist the refresh token
        RefreshToken(refresh_token).blacklist()

        # Create a response with a success message
        response = Response({"success": True, "message": "Logout Success"})

        # Delete the cookies
        response.delete_cookie("refresh_token")
        response.delete_cookie("access_token")

        return response


# Login View
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    This Function Authenticates the User LOGIN and Creates 2 Cookies that stores access_token & refresh_token
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

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
