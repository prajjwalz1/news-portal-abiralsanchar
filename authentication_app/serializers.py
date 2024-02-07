from rest_framework import serializers
from authentication_app.models import CustomUserModel
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


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


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context["user"]
        if not check_password(value, user.password):
            raise serializers.ValidationError("Incorrect old password")
        return value

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value

    def save(self, **kwargs):
        user = self.context["user"]
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()
        return user
