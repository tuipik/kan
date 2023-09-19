from django.contrib.auth import authenticate
from django.core.exceptions import BadRequest
from django_filters.rest_framework import DjangoFilterBackend
from drf_standardized_errors.handler import exception_handler
from rest_framework import status as http_status
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .CONSTANTS import (
    TASK_NAME_REGEX,
    TIME_TRACKER_STATUSES,
    YEAR_QUARTERS,
    TASK_SCALES,
)
from .filters import (
    UserFilter,
    TaskFilter,
    TimeTrackerFilter,
    CommentFilter,
    DepartmentFilter,
)
from .kan_permissions import (
    PermissionPolicyMixin,
    OwnerOrAdminOrReadOnly,
    TimeTrackerChangeIsAdminOrIsDepartmentHead,
)
from .models import User, Department, Task, Comment, TimeTracker, Status, BaseStatuses
from .serializers import (
    UserCreateSerializer,
    PasswordChangeSerializer,
    UserDetailSerializer,
    DepartmentSerializer,
    TaskSerializer,
    CommentSerializer,
    TimeTrackerSerializer,
    UserUpdateSerializer,
    DepartmentCreateSerializer,
    UserBaseSerializer,
    StatusSerializer,
)
from .utils import ResponseInfo


class ResponseModelViewSet(ModelViewSet):
    serializer_classes = {}
    default_serializer_class = None

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(ResponseModelViewSet, self).__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        response_data = super(ResponseModelViewSet, self).list(request, *args, **kwargs)
        data_list = self.data_to_list(response_data.data)
        self.response_format["data"] = data_list
        self.response_format["data_len"] = len(data_list)
        self.response_format["success"] = True
        if not response_data.data:
            self.response_format["message"] = "List empty"
        return Response(self.response_format)

    def create(self, request, *args, **kwargs):
        response_data = super(ResponseModelViewSet, self).create(
            request, *args, **kwargs
        )
        data_list = self.data_to_list(response_data.data)
        self.response_format["data"] = data_list
        self.response_format["data_len"] = len(data_list)
        self.response_format["success"] = True
        self.response_format["message"] = "Created"
        return Response(self.response_format)

    def retrieve(self, request, *args, **kwargs):
        response_data = super(ResponseModelViewSet, self).retrieve(
            request, *args, **kwargs
        )
        data_list = self.data_to_list(response_data.data)
        self.response_format["data"] = data_list
        self.response_format["data_len"] = len(data_list)
        self.response_format["success"] = True
        if not response_data.data:
            self.response_format["message"] = "Empty"
        return Response(self.response_format)

    def update(self, request, *args, **kwargs):
        response_data = super(ResponseModelViewSet, self).update(
            request, *args, **kwargs
        )
        data_list = self.data_to_list(response_data.data)
        self.response_format["data"] = data_list
        self.response_format["data_len"] = len(data_list)
        self.response_format["success"] = True
        self.response_format["message"] = "Updated"
        return Response(self.response_format)

    def destroy(self, request, *args, **kwargs):
        response_data = super(ResponseModelViewSet, self).destroy(
            request, *args, **kwargs
        )
        self.response_format["data"] = []
        self.response_format["data_len"] = 0
        self.response_format["success"] = True
        self.response_format["message"] = "Deleted"
        return Response(self.response_format)

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def get_exception_handler(self):
        return exception_handler

    @staticmethod
    def data_to_list(data):
        if data and not isinstance(data, list):
            return [
                data,
            ]
        return data


class UserViewSet(ResponseModelViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_classes = {
        "create": UserCreateSerializer,
        "update": UserUpdateSerializer,
        "partial_update": UserUpdateSerializer,
    }
    default_serializer_class = UserBaseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

    def get_queryset(self, *args, **kwargs):
        current_user = self.request.user
        if current_user.is_admin:
            return User.objects.all()
        else:
            return User.objects.filter(department_id=current_user.department.id)

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
        ]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]


class LoginView(APIView):
    def post(self, request):
        if "username" not in request.data or "password" not in request.data:
            raise BadRequest("Credentials missing")
        username = request.data["username"]
        password = request.data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            user_serialized = UserDetailSerializer(user).data
            token = RefreshToken.for_user(user)
            user_serialized["tokens"] = {
                "access": str(token.access_token),
                "refresh": str(token),
            }
            return Response(
                ResponseInfo(
                    success=True,
                    data=[user_serialized],
                    data_len=len([user_serialized]),
                    message="Login Success",
                ).response,
                status=http_status.HTTP_200_OK,
            )
        return Response(
            ResponseInfo(success=False, message="Invalid Credentials").response,
            status=http_status.HTTP_401_UNAUTHORIZED,
        )


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data["refresh"]
        try:
            refresh_token = RefreshToken(refresh_token)
            user = User.objects.get(id=refresh_token.payload["user_id"])
        except AttributeError:
            user = "Undefined"
        refresh_token.blacklist()
        return Response(
            ResponseInfo(success=True, message=f"{user.username} Logged out").response,
            status=http_status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            context={"request": request}, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response(
            ResponseInfo(success=True, message="Password changed").response,
            status=http_status.HTTP_200_OK,
        )


class DepartmentApiViewSet(PermissionPolicyMixin, ResponseModelViewSet):
    queryset = Department.objects.all()
    serializer_classes = {
        "create": DepartmentCreateSerializer,
    }
    default_serializer_class = DepartmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [
        IsAuthenticated,
    ]
    permission_classes_per_method = {
        "create": [
            IsAdminUser,
        ],
        "update": [
            IsAdminUser,
        ],
        "partial_update": [
            IsAdminUser,
        ],
        "destroy": [
            IsAdminUser,
        ],
    }
    filter_backends = [DjangoFilterBackend]
    filterset_class = DepartmentFilter


class TaskViewSet(ResponseModelViewSet):
    queryset = Task.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [
        IsAuthenticated,
        # IsAdminUser
    ]
    serializer_classes = {}
    default_serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

    def create(self, request, *args, **kwargs):
        if (dep := self.request.data.get("department")) and not self.request.data.get(
            "primary_department"
        ):
            self.request.data.update({"primary_department": dep})

        self.request.data.update(
            {"status": Status.objects.get(name=BaseStatuses.WAITING.name).id}
        )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if stat_id := self.request.data.get("status"):
            department = Department.objects.filter(statuses=stat_id)
            if department.count() == 1:
                request.data.update({"department": department[0].id})
            else:
                instance = self.get_object()
                request.data.update({"department": instance.primary_department_id})
        return super().update(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
            "update",
            "partial_update",
        ]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self, *args, **kwargs):
        current_user = self.request.user
        if current_user.is_admin or current_user.department.is_verifier:
            return Task.objects.all()
        else:
            return Task.objects.filter(
                primary_department_id=current_user.primary_department.id
            )


class TimeTrackerViewSet(PermissionPolicyMixin, ResponseModelViewSet):
    queryset = TimeTracker.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    permission_classes_per_method = {
        "create": [
            IsAdminUser,
        ],
        "update": [
            TimeTrackerChangeIsAdminOrIsDepartmentHead,
        ],
        "partial_update": [
            TimeTrackerChangeIsAdminOrIsDepartmentHead,
        ],
        "destroy": [
            IsAdminUser,
        ],
    }

    serializer_classes = {}
    default_serializer_class = TimeTrackerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TimeTrackerFilter


class CommentViewSet(ResponseModelViewSet):
    queryset = Comment.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, OwnerOrAdminOrReadOnly]
    serializer_classes = {}
    default_serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CommentFilter


class DefaultsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        constants = {
            "STATUSES": [StatusSerializer(stat).data for stat in Status.objects.all()],
            "STATUSES_PROGRESS_IDS": sorted(Status.STATUSES_PROGRESS_IDS()),
            "STATUSES_IDLE_IDS": sorted(Status.STATUSES_IDLE_IDS()),
            "STATUS_DONE_ID": Status.STATUS_DONE_ID(),
            "TASK_NAME_REGEX": TASK_NAME_REGEX,
            "TASK_SCALES": TASK_SCALES,
            "TIME_TRACKER_STATUSES": TIME_TRACKER_STATUSES,
            "YEAR_QUARTERS": YEAR_QUARTERS,
        }
        return Response(
            ResponseInfo(
                success=True,
                data=[
                    constants,
                ],
            ).response,
            status=http_status.HTTP_200_OK,
        )
