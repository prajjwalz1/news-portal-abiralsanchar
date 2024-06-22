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


"""
These Two Serializers BELOW are used to combine 5Articles Per Category to display on Homepage where 5 latest category are selected based on is_on_home=True"""


class Category_Article_Serializer(serializers.Serializer):
    category_id = serializers.IntegerField()  # 1 Category
    articles = Article_Serializer(many=True)  # 5 Articles so, many = True


class Combined_Category_Article_Serializer(serializers.Serializer):
    # Bundle Up (1:5) Category:Article and return value 'category_article_data'
    category_article_data = Category_Article_Serializer(many=True)


# class Thumbnailserialzier(serializers.Serizlier):
#     news_id=serializers.charfield(null=False)
#     request=serializers.charfield(null=False)

class Thumbnailserialzier(serializers.ModelSerializer):
    class Meta:
        model=Article_Model
        fields=["image1"]