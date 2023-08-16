from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from kanban import settings
from .models import (
    User,
    Department,
    Task,
    Comment,
    TimeTracker,
    TimeTrackerStatuses,
    TaskStatuses,
)
from .utils import TASK_STATUSES_PROGRESS


class DepartmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "is_verifier"]


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "head", "is_verifier"]

    def save(self):
        if user_id := self.initial_data.get("head"):
            user = User.objects.get(pk=user_id)
            if not user.department or not user.department_id == self.instance.id:
                raise serializers.ValidationError(
                    {
                        "head": "To be the head of department user should be the member of department"
                    }
                )
        super().save()


class CommentSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(read_only=True, format=settings.REST_FRAMEWORK['DATETIME_FORMAT'])
    updated = serializers.DateTimeField(read_only=True, format=settings.REST_FRAMEWORK['DATETIME_FORMAT'])
    class Meta:
        model = Comment
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = UserBaseSerializer(instance.user).data
        return representation


class UserBaseSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), allow_null=True, many=False, label="Відділ"
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "department",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if isinstance(instance, User):
            representation["department"] = DepartmentSerializer(
                instance.department
            ).data
        return representation


class UserDetailSerializer(UserBaseSerializer):
    comments = CommentSerializer(source="user_comments", allow_null=True, many=True)

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + [
            "is_admin",
            "comments",
        ]


class UserUpdateSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + [
            "is_admin",
        ]


class UserCreateSerializer(UserBaseSerializer):
    password2 = serializers.CharField(
        style={"input_type": "password"}, write_only=True, label="Підтвердження пароля"
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), allow_null=True, many=False, label="Відділ"
    )

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + [
            "password",
            "password2",
        ]
        extra_kwargs = {"password": {"write_only": True, "label": "Пароль"}}

    def save(self):
        user = User(
            username=self.validated_data["username"],
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data["last_name"],
            department=self.validated_data.get("department", None),
        )
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]
        if password != password2:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        user.set_password(password)
        user.save()
        return user


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        style={"input_type": "password"}, required=True
    )
    new_password = serializers.CharField(
        style={"input_type": "password"}, required=True
    )
    new_password_2 = serializers.CharField(
        style={"input_type": "password"}, required=True
    )

    def validate_current_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError({"current_password": "Не вірний пароль"})
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_2"]:
            raise serializers.ValidationError(
                {"password": "New passwords do not match"}
            )
        return attrs


class TimeTrackerSerializer(serializers.ModelSerializer):
    status_display_value = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = TimeTracker
        fields = [
            "id",
            "task",
            "user",
            "status",
            "status_display_value",
            "start_time",
            "end_time",
            "hours",
            "task_status",
        ]
        read_only_fields = ("start_time", "hours")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = UserBaseSerializer(instance.user).data
        return representation


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), allow_null=True, many=False, label="Відповідальний"
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), allow_null=True, many=False, label="Відділ"
    )
    quarter_display_value = serializers.CharField(
        source="get_quarter_display", read_only=True
    )
    status_display_value = serializers.CharField(
        source="get_status_display", read_only=True
    )
    comments = CommentSerializer(source="task_comments", many=True, read_only=True)
    time_trackers = TimeTrackerSerializer(
        source="time_tracker_tasks", many=True, read_only=True
    )
    change_time_done = serializers.IntegerField(read_only=True)
    correct_time_done = serializers.IntegerField(read_only=True)
    otk_time_done = serializers.IntegerField(read_only=True)
    created = serializers.DateTimeField(read_only=True, format=settings.REST_FRAMEWORK['DATETIME_FORMAT'])
    updated = serializers.DateTimeField(read_only=True, format=settings.REST_FRAMEWORK['DATETIME_FORMAT'])

    class Meta:
        model = Task
        fields = [
            "id",
            "name",
            "change_time_estimate",
            "change_time_done",
            "correct_time_estimate",
            "correct_time_done",
            "otk_time_estimate",
            "otk_time_done",
            "status",
            "status_display_value",
            "time_trackers",
            "quarter",
            "quarter_display_value",
            "category",
            "user",
            "department",
            "done",
            "comments",
            "created",
            "updated",
        ]

    def check_user_has_only_one_task_in_progress(self):
        if (user := self.validated_data.get("user")) and self.validated_data.get(
            "status"
        ) in TASK_STATUSES_PROGRESS:
            tasks_in_progress = user.task_users.filter(
                status__in=TASK_STATUSES_PROGRESS
            )
            if tasks_in_progress:
                raise ValidationError(
                    f"У користувача {user.username} вже є активна задача {tasks_in_progress[0].name}"
                )

    def _check_user_for_progress_status(self):
        if self.validated_data.get(
            "status"
        ) in TASK_STATUSES_PROGRESS and not self.validated_data.get("user"):
            raise ValidationError(
                "Для переводу задачі в статус 'В роботі' має бути вказаний виконавець"
            )

    def _create_log_data(self):
        data = {
            "log_user": self.context["request"].user,
            "log_text": "",
            "is_log": False,
        }
        if self.context["request"].method == "POST":
            data[
                "log_text"
            ] = f'Створено задачу для {self.validated_data.get("name", "")}'
            data["is_log"] = True
        elif self.context["request"].method in ["PUT", "PATCH"]:
            change_list = []
            for key, value in self.validated_data.items():
                change_list.append(
                    f'{self.fields.fields.get(key).label} - {TaskStatuses[value].label if key == "status" else value}'
                )
            data["log_text"] = f'Внесено зміни: {", ".join(change_list)}'
            data["is_log"] = True
        return data

    def save(self, **kwargs):
        comment_data = self._create_log_data()
        self.check_user_has_only_one_task_in_progress()
        if not self.instance:
            super().save()
            self.instance.start_time_tracker()
            self.instance.create_log_comment(**comment_data)
            return self.instance

        if validated_status := self.validated_data.get("status"):
            time_tracker = self.instance.time_tracker_tasks.get(
                task__id=self.instance.id, status=TimeTrackerStatuses.IN_PROGRESS
            )
            if validated_status != time_tracker.task_status:
                self._check_user_for_progress_status()
                time_tracker.change_status_done()
                super().save()
                self.instance.start_time_tracker()
                self.instance.create_log_comment(**comment_data)
                return self.instance

        super().save()
        self.instance.create_log_comment(**comment_data)
        return self.instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = UserBaseSerializer(instance.user).data
        representation["department"] = DepartmentSerializer(instance.department).data
        return representation
