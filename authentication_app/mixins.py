from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from django.conf import settings


class AccessTokenMixin:
    def check_access_token(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        access_token = request.COOKIES.get("access_token")
        user_token = request.COOKIES.get("user_token")
        print(refresh_token,access_token,user_token)

        # User Token is Required to Create,Update articles
        if not user_token:
            return Response(
                {"success:": False, "error": "ACCESS DENIED! User Token is Required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # If either of access/refresh token are not present then its a Guest User so, clear the cookie and Response with 'ACCESS DENIED'
        if not access_token or not refresh_token:
            response = Response(
                {"success:": False, "error": "ACCESS DENIED! User not Logged-In"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response

        # Its a Valid user which has been validate by custom middleware so, decode and verify the access token (OR new access token that got refreshed in middleware)
        try:
            jwt.decode(
                access_token,
                settings.SIMPLE_JWT_SECRET_KEY,
                algorithms=[settings.SIMPLE_JWT_ALGORITHM],
            )
            RefreshToken(refresh_token).check_blacklist()

        except jwt.ExpiredSignatureError:
            return Response(
                {
                    "success:": False,
                    "error": "ACCESS DENIED! Access token has Expired!",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        except jwt.InvalidTokenError as e:
            return Response(
                {
                    "success:": False,
                    "error": f"ACCESS DENIED! Invalid Access token: {str(e)}",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response(
                {
                    "success:": False,
                    "error": f"ACCESS DENIED! Invalid Token: { str(e)}",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Access Token is Valid, Return None
        return None
