from newsportal.models import Article_Model, Category_Model
from newsportal.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination


class Homepage_View(APIView):

    """
    Navbar Category - ID, Name, Slug
    Featured Articles
    Trending Articles
    Latest Articles
    Categorized Articles i.e. 5 Articles per Category
    """

    def get(self, request):
        # Empty List to Store all context data
        result = []

        navbar_category = self.navbar_category(request)
        featured_articles = self.featured_articles(request)
        trending_articles = self.trending_articles(request)
        latest_articles = self.latest_articles(request)
        articles_categorized = self.articles_categorized(request)

        result.append(navbar_category)
        result.append(featured_articles)
        result.append(trending_articles)
        result.append(latest_articles)
        result.append(articles_categorized)

        return Response(
            {
                "success": True,
                "data": result,
            },
            status=status.HTTP_200_OK,
        )

    def navbar_category(self, request):
        """
        Get Latest Category to Showcase on NAVBAR i.e. is_on_navbar =True (Limit)
        """
        # Fetching Specific Values for Better Optimization and Query Speed
        navbar_category = (
            Category_Model.objects.filter(is_on_navbar=True)
            .values("title", "slug")
            .order_by("-created_at")[:5]
        )
        serializer = Category_On_Navbar_Serializer(navbar_category, many=True)
        data = {
            "navbar_category_totalHits": len(serializer.data),
            "navbar_category": serializer.data,
        }
        return data

    def featured_articles(self, request):
        """
        Get Latest FEATURED Articles with Its Respective Category Data (Limit)
        """
        featured_article = (
            Article_Model.objects.filter(is_featured=True)
            .order_by("-created_at")
            .select_related("category", "author")[:5]
        )
        serializer = Article_Serializer(featured_article, many=True)
        data = {
            "featured_articles_totalHits": len(serializer.data),
            "featured_articles": serializer.data,
        }
        return data

    def trending_articles(self, request):
        """
        Get TRENDING Articles that are Not Featured with Its Respective Category and Author Data (Limit)
        """
        trending_article = (
            Article_Model.objects.order_by("-created_at")
            .filter(is_trending=True)
            .exclude(is_featured=True)
            .select_related("category", "author")[:5]
        )
        serializer = Article_Serializer(trending_article, many=True)
        data = {
            "trending_articles_totalHits": len(serializer.data),
            "trending_articles": serializer.data,
        }
        return data

    def latest_articles(self, request):
        """
        Get LATEST Articles that are Not Featured with Its Respective Category and Author Data (Limit)
        """
        latest_article = (
            Article_Model.objects.order_by("-created_at")
            .exclude(is_featured=True)
            .select_related("category", "author")[:5]
        )
        serializer = Article_Serializer(latest_article, many=True)
        data = {
            "latest_articles_totalHits": len(serializer.data),
            "latest_articles": serializer.data,
        }
        return data

    def articles_categorized(self, request):
        """
        5 Articles of Each Category that has Value Category.is_on_home = True
        """

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
                "category_title": category.title,  # Can also send category PK i.e. 'id'
                "articles": serialized_articles,
            }
            category_article_list.append(category_data)

        context = {
            "category_article_data": category_article_list,
        }

        # Serialize the context
        serializer = Combined_Category_Article_Serializer(data=context)
        serializer.is_valid()

        data = {
            "articles_categorized_totalHits": len(serializer.data),
            "articles_categorized": serializer.data,
        }
        return data


class Individual_Category_Article_View(APIView):
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


class Article_View(APIView):
    """
    Create new Article
    """

    def post(self, request):
        serializer = Article_Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )


class Category_View(APIView):
    """
    Create new Category for Article
    """

    def post(self, request):
        serializer = Category_Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )
