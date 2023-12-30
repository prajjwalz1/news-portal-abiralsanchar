from newsportal.models import Article_Model, Category_Model
from newsportal.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination


class Individual_Category_Article(APIView):
    """
    Fetches LIMITED Articles of Certain Category with PAGINATION
    """

    # Set pagination class for this view
    pagination_class = PageNumberPagination

    def get(self, request, category_slug):
        try:
            category = Category_Model.objects.get(slug=category_slug)
            articles = Article_Model.objects.filter(category=category)

            # Use the pagination class to paginate the queryset
            paginator = self.pagination_class()
            paginated_articles = paginator.paginate_queryset(articles, request)

            serializer = Article_Serializer(paginated_articles, many=True)

            return Response(
                {
                    "success": True,
                    "totalHits": len(serializer.data),
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": f"{str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
