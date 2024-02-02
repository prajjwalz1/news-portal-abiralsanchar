from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from authentication_app.decoraters import access_token_required
from django.contrib.auth.password_validation import validate_password
from authentication_app.serializers import SignupSerializer
from authentication_app.models import CustomUserModel


# Protected View Testing using Custom Mixins and Decorater
class FetchData(APIView):
    @access_token_required
    def get(self, request):
        return Response(
            {"success": True, "message": "Access Granted!"},
            status=status.HTTP_200_OK,
        )


# Logout View
class LogoutView(APIView):
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


# Only Admin or Staff user can create new Users
class SignupView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            try:
                validate_password(serializer.validated_data["password"])
            except Exception as e:
                return Response(
                    {"success": False, "error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                user_create = CustomUserModel.objects.create_user(
                    username=serializer.validated_data["username"],
                    first_name=serializer.validated_data["first_name"],
                    last_name=serializer.validated_data["last_name"],
                    email=serializer.validated_data["email"],
                    phone_number=serializer.validated_data["phone_number"],
                    password=serializer.validated_data["password"],
                )

                # Only validate the Profile_Image after other details are validated else,even if the user credentials are invalid, image will be saved on Server.
                if user_create:
                    profile_image = serializer.validated_data["profile_image"]
                    user_create.profile_image = profile_image
                    user_create.save()
                    return Response(
                        {
                            "success": True,
                            "message": "Staff Account Created Successfully",
                        },
                        status=status.HTTP_201_CREATED,
                    )

            except Exception as e:
                if (
                    "UNIQUE constraint failed: authentication_app_customusermodel.username"
                    in str(e)
                ):
                    return Response(
                        {"success": False, "error": "Username already taken"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    return Response(
                        {
                            "success": False,
                            "error": "An error occurred while creating the user",
                            "error_detail": str(e),
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        return Response(
            {"success": False, "error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# Decorator so only isStaff /superAdmin
