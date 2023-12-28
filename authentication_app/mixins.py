from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class AccessTokenMixin:
    def check_access_token(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "User not Logged in... refresh_token not available"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            RefreshToken(refresh_token).check_blacklist()
        except Exception as e:
            return Response(
                {"error": f"Invalid refresh_token! {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # The access token is valid, Access Granted to Protected Views
        return None
