from newsportal.models import Article_Model, Category_Model
from newsportal.serializers import Article_Serializer, Category_Serializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class Article_View(APIView):
    def get(self, request):
        all_article_query = Article_Model.objects.all()
        serializer = Article_Serializer(all_article_query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = Article_Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"data": serializer.data, "success": True}, status=status.HTTP_200_OK
        )


class Category_View(APIView):
    def post(self, request):
        serializer = Category_Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"data": serializer.data, "success": True}, status=status.HTTP_200_OK
        )
