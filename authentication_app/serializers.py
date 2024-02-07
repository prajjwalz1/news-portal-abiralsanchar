from rest_framework import serializers
from authentication_app.models import CustomUserModel
from django.contrib.auth.hashers import check_password


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    email = serializers.EmailField(max_length=255)
    phone_number = serializers.CharField(max_length=10)
    profile_image = serializers.ImageField(required=False)
    password = serializers.CharField(write_only=True)
    # write_only insure's when the object is being serialized,it wont get selected


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserModel
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "profile_image",
        ]
        extra_kwargs = {
            "username": {"required": False},
            "first_name": {"required": False},
            "last_name": {"required": False},
            "email": {"required": False},
            "phone_number": {"required": False},
            "profile_image": {"required": False},
        }

    # Validate the Length of Phone number to be not less than 10, more than 10 will be auto validated as the model has max_digits =10
    def validate_phone_number(self, value):
        phone_number_str = str(value)
        if len(phone_number_str) != 10:
            raise serializers.ValidationError("Phone number must be 10 digits long.")
        return value
