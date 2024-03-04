from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from authentication_app.decoraters import access_token_required, staff_admin_required
from django.contrib.auth.password_validation import validate_password
from authentication_app.serializers import (
    SignupSerializer,
    CustomUserSerializer,
    PasswordChangeSerializer,
)
from authentication_app.models import CustomUserModel
import jwt
from django.conf import settings
from django.views.decorators.cache import cache_control


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

        if not refresh_token:
            return Response(
                {"success:": False, "error": "User not Logged In!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            # Clear cookies
            response = Response({"success": True, "message": "Logout Success"})
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            response.delete_cookie("user_token")
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
        if "access" in response.data and "refresh" in response.data:
            access_token = response.data["access"]
            refresh_token = response.data["refresh"]
            try:
                decoded_access_token = jwt.decode(
                    access_token,
                    settings.SIMPLE_JWT_SECRET_KEY,
                    algorithms=[settings.SIMPLE_JWT_ALGORITHM],
                )
                user_id = decoded_access_token["user_id"]
                user_object = CustomUserModel.objects.get(pk=user_id)

                # Remove acccess/refresh tokenfrom the Default Response
                response.data = {}
                user_role = "normal"
                # If the user is superuser then Add that detail in Resposne
                if user_object.is_superuser:
                    response.data["is_superuser"] = True
                    user_role = "superuser"

                # If the user is staff then Add that detail in Resposne
                elif user_object.is_staff:
                    response.data["is_staff"] = True
                    user_role = "staff"

                # User Cookie JWT
                user_token = jwt.encode(
                    {
                        "user_id": user_id,
                        "first_name": user_object.first_name,
                        "last_name": user_object.last_name,
                        "user_role": user_role,
                    },
                    settings.SIMPLE_JWT_SECRET_KEY,
                    algorithm=settings.SIMPLE_JWT_ALGORITHM,
                )
                response.set_cookie("user_token", user_token, httponly=True, secure=False)
                response.set_cookie("access_token", access_token, httponly=True, secure=False)
                response.set_cookie("refresh_token", refresh_token, httponly=True, secure=False)
            
            except Exception as e:
                return Response(
                    {"success": False, "error": f"Login Failed! {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

           
            response.data["success"] = True
            response.data["message"] = "Login Successful"
            print(response.data)
            return response
        else:
            return response
            

class SignupView(APIView):
    """
    Only Superuser or Staff user can use this VIEW.
    """

    @staff_admin_required
    def post(self, request):
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
                profile_image = serializer.validated_data["profile_image"]

                if profile_image:
                    # Only after Profile Image is present create the Model
                    CustomUserModel.objects.create_user(
                        username=serializer.validated_data["username"],
                        first_name=serializer.validated_data["first_name"],
                        last_name=serializer.validated_data["last_name"],
                        email=serializer.validated_data["email"],
                        phone_number=serializer.validated_data["phone_number"],
                        password=serializer.validated_data["password"],
                        profile_image=profile_image,
                    )

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
                elif "profile_image" in str(e):
                    return Response(
                        {"success": False, "error": "Profile Image is required."},
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


class UserView(APIView):
    """
    This Function fetches the user object model
    """

    def get_user(self, request):
        try:
            # Fetching the user_payload from middleware directly
            user_token_payload = getattr(request, "user_token_payload", False)
            user_id = user_token_payload["user_id"]
            return CustomUserModel.objects.get(pk=user_id)
        except Exception as e:
            if "CustomUserModel matching query does not exist." in str(e):
                return Response(
                    {"success": False, "error": "user doesn't exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                return Response(
                    {"success": False, "error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    # This View Fetches the User Data
    @access_token_required
    def get(self, request, format=None):
        user = self.get_user(request)
        serializer = CustomUserSerializer(user)
        return Response(
            {"success": True, "message": serializer.data}, status=status.HTTP_200_OK
        )

    # This function updates the user profile
    @access_token_required
    def patch(self, request, format=None):
        password = request.data.get("password", None)
        id = request.data.get("id", None)

        # we wont allow the user to update password/id from this Patch method.
        # For updating password we have seperate API
        if password or id:
            return Response(
                {
                    "success": False,
                    "error": "REQUEST DENIED!",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = self.get_user(request)
        serializer = CustomUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"success": False, "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PasswordChangeView(UserView, APIView):
    """
    API to update the user password.
    request body :
    {
    "old_password":"...",
    "new_password":"..."
    }
    """

    @access_token_required
    def patch(self, request, format=None):
        user = self.get_user(request)
        serializer = PasswordChangeSerializer(data=request.data, context={"user": user})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Password changed successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"success": False, "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
