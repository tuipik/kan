from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from .views import (
    LoginView,
    LogoutView,
    ChangePasswordView,
    UserViewSet,
    DepartmentApiViewSet,
    TaskViewSet,
    CommentViewSet,
    TimeTrackerViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register(r"accounts", UserViewSet, basename="account")
router.register(r"departments", DepartmentApiViewSet, basename="department")
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"time_trackers", TimeTrackerViewSet, basename="time_tracker")
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = [
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),    # TODO: should be deleted
    path("accounts/login", LoginView.as_view(), name="login"),
    path("accounts/logout", LogoutView.as_view(), name="logout"),
    path(
        "accounts/change-password", ChangePasswordView.as_view(), name="change-password"
    ),
] + router.urls
