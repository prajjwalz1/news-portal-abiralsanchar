from newsportal.models import Article_Model, Category_Model
from newsportal.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination

"""
Article 
-CRUD 
-5Featured (Priority - 2)
-5Trending (Priority - 3)
-5Latest (Priority - 4)

Category
-is_on_nav -> Limit 5 + Latest (Priority - 1)
-is_on_home -> Limit 5 Articles Per Category (Priority - 5)

Individual Category -> Limit 10 + Filtered Pagination
"""


class Article_View(APIView):
    # Get all Articles
    def get(self, request):
        all_article_query = Article_Model.objects.all()
        serializer = Article_Serializer(all_article_query, many=True)
        return Response(
            {
                "success": True,
                "totalHits": len(all_article_query),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # Create new Article
    def post(self, request):
        serializer = Article_Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )


class Article_Featured_View(APIView):
    # Get Latest Featured Articles (Limit)
    def get(self, request):
        featured_article = (
            Article_Model.objects.filter(is_featured=True)
            .order_by("-created_at")
            .select_related("category", "author")[:5]
        )
        serializer = Article_Serializer(featured_article, many=True)
        return Response(
            {
                "success": True,
                "totalHits": len(featured_article),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class Article_Latest_View(APIView):
    # Get Latest Articles that are Not Featured (Limit)
    def get(self, request):
        latest_article = (
            Article_Model.objects.order_by("-created_at")
            .exclude(is_featured=True)
            .select_related("category", "author")[:5]
        )
        serializer = Article_Serializer(latest_article, many=True)
        return Response(
            {
                "success": True,
                "totalHits": len(latest_article),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class Article_Trending_View(APIView):
    # Get Trending Articles that are Not Featured (Limit)
    def get(self, request):
        trending_article = (
            Article_Model.objects.order_by("-created_at")
            .filter(is_trending=True)
            .exclude(is_featured=True)
            .select_related("category", "author")[:5]
        )
        serializer = Article_Serializer(trending_article, many=True)
        return Response(
            {
                "success": True,
                "totalHits": len(trending_article),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class Article_Categorized_Homepage(APIView):
    """
    5 Articles of Each Category that has Value Category.is_on_home = True
    """

    def get(self, request):
        # Fetching 5 category that have is_on_home = True
        categories = Category_Model.objects.filter(is_on_home=True).order_by(
            "-created_at"
        )[:5]

        # This LIST stores 5 category and 5 respective articles per category
        category_article_list = []

        for category in categories:
            # Get 5 Articles of Category 'X'
            articles = Article_Model.objects.filter(category=category)[:5]

            # Serializing 5 article model instances  | '.data' = serializer.data
            serialized_articles = Article_Serializer(articles, many=True).data

            # Now we bundle up Category 'X' with 5 respective articles and append to List
            category_data = {
                "category_id": category.title,  # Can also send category PK i.e. 'id'
                "articles": serialized_articles,
            }
            category_article_list.append(category_data)

        context = {
            "category_article_data": category_article_list,
        }

        # Serialize the context
        serializer = Combined_Category_Article_Serializer(data=context)
        serializer.is_valid(raise_exception=True)

        return Response(
            {
                "success": True,
                "totalHits": len(category_article_list),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class Category_On_Navbar_View(APIView):
    # Get Latest Category to Showcase on NAVBAR i.e. is_on_navbar =True (Limit)
    def get(self, request):
        # Fetching Specific Values for Better Optimization and Query Speed
        navbar_category = (
            Category_Model.objects.filter(is_on_navbar=True)
            .values("title", "slug")
            .order_by("-created_at")[:5]
        )
        serializer = Category_On_Navbar_Serializer(navbar_category, many=True)
        return Response(
            {
                "success": True,
                "totalHits": len(navbar_category),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class Category_View(APIView):
    # Create new Category for Article
    def post(self, request):
        serializer = Category_Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )


class Individual_Category_Article(APIView):
    """
    Fetches LIMITED(10) Articles of Certain Category with PAGINATION
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
