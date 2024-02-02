from rest_framework import serializers


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    email = serializers.EmailField(max_length=255)
    phone_number = serializers.CharField(max_length=10)
    profile_image = serializers.ImageField(required=False)
    password = serializers.CharField(write_only=True)
    # write_only insure's when the object is being serialized,it wont get selected
