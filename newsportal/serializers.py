from rest_framework import serializers
from newsportal.models import Article_Model, Category_Model


class Article_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Article_Model
        fields = "__all__"


class Category_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Category_Model
        fields = "__all__"


# This Serializer is Created to only send Titlte and Slug in Response instead of whole data
class Category_On_Navbar_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Category_Model
        fields = ["title", "slug"]
