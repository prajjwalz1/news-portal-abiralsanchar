from django.urls import path
from newsportal.views import Article_View, Category_View


urlpatterns = [
    path("api/news/article/", Article_View.as_view()),
    path("api/news/category/", Category_View.as_view()),
]
