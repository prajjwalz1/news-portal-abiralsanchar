from newsportal.models import Article_Model, Category_Model
from newsportal.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from authentication_app.decoraters import access_token_required
from django.http import HttpResponse
from django.http import FileResponse

class Navbar_View(APIView):
    """
    Navbar Category - ID, Name, Slug
    Featured Articles
    Trending Articles
    Latest Articles
    """

    def get(self, request):
        # Empty List to Store all context data
        result = []

        navbar_category = self.navbar_category(request)
        trending_articles = self.trending_articles(request)
        latest_articles = self.latest_articles(request)
        featured_articles = self.featured_articles(request)

        result.append(navbar_category)
        result.append(trending_articles)
        result.append(latest_articles)
        result.append(featured_articles)

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
        try:
            # Fetching Specific Values for Better Optimization and Query Speed
            navbar_category = (
                Category_Model.objects.filter(is_on_navbar=True)
                .values("title", "slug")
                .order_by("-created_at")[:8]
            )
            serializer = Category_On_Navbar_Serializer(navbar_category, many=True)
            data = {
                "navbar_category_totalHits": len(serializer.data),
                "navbar_category": serializer.data,
            }
            return data
        except Exception as e:
            return Response(
                {"success": False, "error": f"{str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def trending_articles(self, request):
        """
        Get TRENDING Articles that are Not Featured with Its Respective Category and Author Data (Limit)
        """
        try:
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
        except Exception as e:
            return Response(
                {"success": False, "error": f"{str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def latest_articles(self, request):
        """
        Get LATEST Articles that are Not Featured with Its Respective Category and Author Data (Limit)
        """
        try:
            latest_article = (
                Article_Model.objects.order_by("-created_at")
                .exclude(is_featured=True)
                .select_related("category", "author")[:8]
            )
            serializer = Article_Serializer(latest_article, many=True)
            data = {
                "latest_articles_totalHits": len(serializer.data),
                "latest_articles": serializer.data,
            }
            return data
        except Exception as e:
            return Response(
                {"success": False, "error": f"{str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def featured_articles(self, request):
        """
        Get Latest FEATURED Articles with Its Respective Category Data (Limit)
        """
        try:
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
        except Exception as e:
            return Response(
                {"success": False, "error": f"{str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Homepage_View(APIView):
    """
    Categorized Articles i.e. 5 Articles per Category
    """

    def get(self, request):
        # Empty List to Store all context data
        result = []

        articles_categorized = self.articles_categorized(request)

        result.append(articles_categorized)

        return Response(
            {
                "success": True,
                "data": result,
            },
            status=status.HTTP_200_OK,
        )

    def articles_categorized(self, request):
        """
        5 Articles of Each Category that has Value Category.is_on_home = True
        """
        try:
            # Fetching 5 category that have is_on_home = True
            categories = Category_Model.objects.filter(is_on_home=True).order_by(
                "-created_at"
            )[:5]

            # This LIST stores 5 category and 5 respective articles per category
            category_article_list = []

            for category in categories:
                # Get 5 Articles of Category 'X'
                articles = Article_Model.objects.filter(category=category).order_by('-created_at')[:5]

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
        except Exception as e:
            return Response(
                {"success": False, "error": f"{str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


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
    Get ALL Articles using : '/article/?page=1' OR Get Single Article using : 'article/1/'
    """

    # Set pagination class for this view
    pagination_class = PageNumberPagination

    def get(self, request, pk=None, format=None):
        if pk is None:
            try:
                # Its a GET ALL Request so, Fetching all Articles
                all_article_query = Article_Model.objects.get_queryset().order_by(
                    "-created_at"
                )

                paginator = self.pagination_class()
                paginated_articles = paginator.paginate_queryset(
                    all_article_query, request
                )
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
        else:
            # Its a Single Article Get Request so , Fetching a single category by PK
            try:
                article = Article_Model.objects.get(pk=pk)
                serializer = Article_Serializer(article)
                return Response(
                    {
                        "success": True,
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response(
                    {"success": False, "error": f"{str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    """
    This Function Updates Article Model Object using PATCH
    """

    @access_token_required
    def patch(self, request, pk, format=None):
        try:
            article = Article_Model.objects.get(pk=pk)
            serializer = Article_Serializer(article, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": True,
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"success": False, "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Article_Model.DoesNotExist as e:
            return Response(
                {"success": False, "error": f"{str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    """
    This Function DELETE Article Model Object using PK
    """

    @access_token_required
    def delete(self, request, pk, format=None):
        try:
            article = Article_Model.objects.get(pk=pk)
            article.delete()
            return Response(
                {"success": True, "message": f"{article} deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": f"{str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    """
    Create new Article
    """

    @access_token_required
    def post(self, request):
        user_token_payload = getattr(request, "user_token_payload", False)
        user_id = user_token_payload["user_id"]
        request.data["author"] = user_id
        user_id = user_token_payload["user_id"]
        request.data["is_featured"] = True
        serializer = Article_Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED
        )


class Category_View(APIView):
    """
    Get ALL Category using : '/category/?page=1' OR Get Single Category using : 'category/1/'
    """

    # Set pagination class for this view
    pagination_class = PageNumberPagination

    def get(self, request, pk=None, format=None):
        if pk is None:
            try:
                # Its a GET ALL Request so, Fetching all categories
                all_category_query = Category_Model.objects.get_queryset().order_by(
                    "-created_at"
                )
                paginator = self.pagination_class()
                paginated_category = paginator.paginate_queryset(
                    all_category_query, request
                )
                serializer = Category_Serializer(paginated_category, many=True)

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
        else:
            # Its a Single Category Get Request so , Fetching a single category by PK
            try:
                category = Category_Model.objects.get(pk=pk)
                serializer = Category_Serializer(category)
                return Response(
                    {
                        "success": True,
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response(
                    {"success": False, "error": f"{str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    """
    This Function Updates Category Model Object using PATCH
    """

    @access_token_required
    def patch(self, request, pk, format=None):
        try:
            category = Category_Model.objects.get(pk=pk)
            serializer = Category_Serializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": True,
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"success": False, "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Category_Model.DoesNotExist as e:
            return Response(
                {"success": False, "error": f"{str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    """
    This Function DELETE Category Model Object using PK
    """

    @access_token_required
    def delete(self, request, pk, format=None):
        try:
            category = Category_Model.objects.get(pk=pk)
            category.delete()
            return Response(
                {"success": True, "message": f"{category} deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": f"{str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    """
    Create new Category for Article
    """

    @access_token_required
    def post(self, request):
        serializer = Category_Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED
        )



class News(APIView):
    def get(self, request):
        request_type = request.GET.get("request")
        news_id = request.GET.get("news_id")
        print(news_id, request_type)
        
        if not request_type or not news_id:
            return Response({"success": False, "message": "request_type and news_id are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {
            "request": request_type,
            "news_id": news_id
        }
        
        try:
            article = Article_Model.objects.get(id=news_id)
            image_path = article.image1.path  # Assuming image1 is an ImageField/FileField
        except Article_Model.DoesNotExist:
            return Response({"success": False, "message": "Article not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print(image_path)
        try:
            image_file = open(image_path, 'rb')
            response = FileResponse(image_file, content_type='image/jpeg')
            response['Content-Disposition'] = f'inline; filename="{article.image1.name}"'
            return response
        except Exception as e:
            return Response({"success": False, "message": f"Failed to open image file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
