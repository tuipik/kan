from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    LoginView,
    LogoutView,
    ChangePasswordView,
    UserViewSet,
    DepartmentApiViewSet,
    TaskViewSet,
    CommentViewSet,
    TimeTrackerViewSet, DefaultsView,
)

router = DefaultRouter(trailing_slash=False)
router.register(r"accounts", UserViewSet, basename="account")
router.register(r"departments", DepartmentApiViewSet, basename="department")
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"time_trackers", TimeTrackerViewSet, basename="time_tracker")
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = [
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("accounts/login", LoginView.as_view(), name="login"),
    path("accounts/logout", LogoutView.as_view(), name="logout"),
    path(
        "accounts/change-password", ChangePasswordView.as_view(), name="change-password"
    ),
    path("token/create/", TokenObtainPairView.as_view(), name="token_create"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("defaults/", DefaultsView.as_view(), name="defaults"),
] + router.urls
