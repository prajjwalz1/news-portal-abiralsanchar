from django.urls import path
from newsportal.views import *


urlpatterns = [
    path("api/v1/news/article/", Article_View.as_view()),
    path("api/v1/news/category/", Category_View.as_view()),
    path("api/v1/news/homepage/", Homepage_View.as_view()),
    path(
        "api/v1/news/category/<str:category_slug>/",
        Individual_Category_Article_View.as_view(),
    ),
]


"""    
Below are the Loosely Couple REST API URL's that are not in used anymore!
path("api/v1/news/article/", Article_View.as_view()),
path("api/v1/news/category/", Category_View.as_view()),
path("api/v1/news/category/navbar/", Category_On_Navbar_View.as_view()),
path("api/v1/news/article/categorized/", Article_Categorized_Homepage.as_view()),
path("api/v1/news/article/featured/", Article_Featured_View.as_view()),
path("api/v1/news/article/latest/", Article_Latest_View.as_view()),
path("api/v1/news/article/trending/", Article_Trending_View.as_view()),
path("api/v1/news/category/<str:category_slug>/",Individual_Category_Article.as_view())
"""
