from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import BadRequest
from django_filters.rest_framework import DjangoFilterBackend
from drf_standardized_errors.handler import exception_handler
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

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
from .models import User, Department, Task, Comment, TimeTracker
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
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    serializer_classes = {
        "create": UserCreateSerializer,
        "update": UserUpdateSerializer,
        "partial_update": UserUpdateSerializer,
    }
    default_serializer_class = UserDetailSerializer
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
            login(request, user)
            user_serialized = UserDetailSerializer(user).data
            return Response(
                ResponseInfo(
                    success=True,
                    data=[user_serialized],
                    data_len=len([user_serialized]),
                    message="Login Success",
                ).response,
                status=status.HTTP_200_OK,
            )
        return Response(
            ResponseInfo(success=False, message="Invalid Credentials").response,
            status=status.HTTP_401_UNAUTHORIZED,
        )


class LogoutView(APIView):
    def post(self, request):
        try:
            user = request.user.get_username()
        except AttributeError:
            user = "Undefined"
        logout(request)
        return Response(
            ResponseInfo(success=True, message=f"{user} Logged out").response,
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            context={"request": request}, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response(
            ResponseInfo(success=True, message="Password changed").response,
            status=status.HTTP_200_OK,
        )


class DepartmentApiViewSet(PermissionPolicyMixin, ResponseModelViewSet):
    queryset = Department.objects.all()
    serializer_classes = {
        "create": DepartmentCreateSerializer,
    }
    default_serializer_class = DepartmentSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
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
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_classes = {}
    default_serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

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
            return Task.objects.filter(department_id=current_user.department.id)


class TimeTrackerViewSet(PermissionPolicyMixin, ResponseModelViewSet):
    queryset = TimeTracker.objects.all()
    authentication_classes = [SessionAuthentication, BasicAuthentication]
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
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, OwnerOrAdminOrReadOnly]
    serializer_classes = {}
    default_serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CommentFilter
