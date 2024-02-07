from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from authentication_app.views import (
    FetchData,
    CustomTokenObtainPairView,
    LogoutView,
    SignupView,
    UserView,
    PasswordChangeView,
)

urlpatterns = [
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/logout/", LogoutView.as_view()),
    path("api/signup/", SignupView.as_view()),
    path("api/user/", UserView.as_view()),
    path("api/user/change-password/", PasswordChangeView.as_view()),
    path("api/data/", FetchData.as_view()),
]
