from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


class FetchData(APIView):
    def get(self, request):
        # Create Custom MIXIN to Check if Refresh/Access Token are Valid from COOKIES
        return Response({"success": True}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not available"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Blacklist the refresh token
            RefreshToken(refresh_token).blacklist()
            # Create a response with a success message
            response = Response({"success": True})

            # Delete the cookies
            response.delete_cookie("refresh_token")
            response.delete_cookie("access_token")

            return response
        except Exception as e:
            return Response({"detail": str(e)}, status=500)


# Login View
class CustomTokenObtainPairView(TokenObtainPairView):
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
