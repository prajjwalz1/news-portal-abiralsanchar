from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
import jwt
from django.conf import settings

"""
This Middleware is used to validate + refresh the the Access/Refresh Token 

How it Works : 
First we check if RefreshToken/AccessToken cookie are available or not.
If Available ,means the user is logged in then,
-check if RefreshToken is valid or not . 
-If its not valid then Just end the SESSION and clear all the cookie
-If its valid then proceed to check if AccessToken is Expired or is valid/invalid.
-If AccessToken is Expired then we create new access token from the refresh token and also setup cookie for new access token.
-If AccessToken is not valid Just end the SESSION and clear all the cookie.

If Cookie are not available then its a Guest user so continue with the request.
If the user is Guest then, we will secure our Views with custom MIXINS

Note : In either case if Access/Refresh token are invalid we pass the isSessionExpired=True and then our custom decorator clears the Cookie and sends the Response to user 'Session Expired , Login to continue....'
"""


class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        access_token = request.COOKIES.get("access_token")
        user_token = request.COOKIES.get("user_token")

        if user_token:
            try:
                user_token_payload = jwt.decode(
                    user_token,
                    settings.SIMPLE_JWT_SECRET_KEY,
                    algorithms=[settings.SIMPLE_JWT_ALGORITHM],
                )

                # user_token is valid, now pass the payload data to request, if the request passes the decorator then in view we extract the user_id from payload and use that for creating article i.e. article.Author = user_id
                request.user_token_payload = user_token_payload
                response = self.get_response(request)
                return response
            except Exception as e:
                # user_token is Invalid! End the Session
                request.isSessionExpired = True
                response = self.get_response(request)
                return response

        if access_token and refresh_token:
            # First we try to check if REFRESH TOKEN is valid or not,if its INVALID then EXPIRE the SESSION
            try:
                jwt.decode(
                    refresh_token,
                    settings.SIMPLE_JWT_SECRET_KEY,
                    algorithms=[settings.SIMPLE_JWT_ALGORITHM],
                )
                RefreshToken(refresh_token).check_blacklist()

                # Refresh token is valid , Check access_token now
                try:
                    jwt.decode(
                        access_token,
                        settings.SIMPLE_JWT_SECRET_KEY,
                        algorithms=[settings.SIMPLE_JWT_ALGORITHM],
                    )

                except jwt.ExpiredSignatureError:
                    # Access token has expired, generate new access_token and continue the request
                    refresh = RefreshToken(refresh_token)
                    new_access_token = str(refresh.access_token)

                    # Overriding the expired access_token with new access_token
                    request.COOKIES["access_token"] = new_access_token

                    response = self.get_response(request)

                    # Set the new access_token cookie
                    response.set_cookie(
                        "access_token", new_access_token, httponly=True, secure=False
                    )
                    return response

                except Exception as e:
                    # access token is Invalid! End the Session
                    request.isSessionExpired = True
                    response = self.get_response(request)
                    return response

            except Exception as e:
                # Refresh token is Expired,Blacklisted,Invalid! End the Session
                request.isSessionExpired = True
                response = self.get_response(request)
                return response

        response = self.get_response(request)
        return response
