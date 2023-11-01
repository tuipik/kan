from datetime import datetime

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
    Status,
)


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ["id", "name", "translation"]


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
            user = User.objects.get_or_none(pk=user_id)
            if not user.department or not user.department_id == self.instance.id:
                raise serializers.ValidationError(
                    {
                        "head": "Щоб бути керівником відділу, користувач має бути членом відділу"
                    }
                )
        super().save()


class CommentSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(
        read_only=True, format=settings.REST_FRAMEWORK["DATETIME_FORMAT"]
    )
    updated = serializers.DateTimeField(
        read_only=True, format=settings.REST_FRAMEWORK["DATETIME_FORMAT"]
    )

    class Meta:
        model = Comment
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = UserBaseSerializer(instance.user).data
        return representation


class UserBaseSerializer(serializers.ModelSerializer):
    department_obj = DepartmentSerializer(source="department", read_only=True)
    is_head_department = serializers.BooleanField(default=False, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "department",
            "department_obj",
            "is_admin",
            "role",
            "is_head_department",
        ]


class UserDetailSerializer(UserBaseSerializer):
    pass


class UserUpdateSerializer(UserBaseSerializer):
    pass


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
            # "role"
        ]
        extra_kwargs = {"password": {"write_only": True, "label": "Пароль"}}

    def save(self):
        user = User(
            username=self.validated_data["username"],
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data["last_name"],
            department=self.validated_data.get("department", None),
            role=self.validated_data.get("role", None),
        )
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]
        if password != password2:
            raise serializers.ValidationError({"password": "Паролі не співпадають."})
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
                {"password": "Нові паролі не співпадають."}
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
            "task_department",
        ]
        read_only_fields = ("hours",)


class InvolvedUsersSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(read_only=True)
    department_name = serializers.CharField(source="department", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "department",
            "department_name",
            "role",
        ]


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), allow_null=True, many=False, label="Відповідальний"
    )
    user_obj = UserBaseSerializer(source="user", read_only=True)
    involved_users = serializers.ManyRelatedField(
        child_relation=InvolvedUsersSerializer(source="user", read_only=True),
        read_only=True,
    )
    department_obj = DepartmentSerializer(source="department", read_only=True)
    quarter_display_value = serializers.CharField(
        source="get_quarter_display", read_only=True
    )
    status_obj = StatusSerializer(source="status", read_only=True)
    scale_display_value = serializers.CharField(
        source="get_scale_display", read_only=True
    )
    editing_time_done = serializers.IntegerField(read_only=True)
    correcting_time_done = serializers.IntegerField(read_only=True)
    tc_time_done = serializers.IntegerField(read_only=True)
    created = serializers.DateTimeField(
        read_only=True, format=settings.REST_FRAMEWORK["DATETIME_FORMAT"]
    )
    updated = serializers.DateTimeField(
        read_only=True, format=settings.REST_FRAMEWORK["DATETIME_FORMAT"]
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "name",
            "editing_time_estimate",
            "editing_time_done",
            "correcting_time_estimate",
            "correcting_time_done",
            "tc_time_estimate",
            "tc_time_done",
            "status",
            "status_obj",
            "scale",
            "scale_display_value",
            "quarter",
            "quarter_display_value",
            "year",
            "category",
            "user",
            "user_obj",
            "involved_users",
            "department",
            "department_obj",
            "done",
            "created",
            "updated",
        ]

    def check_user_has_only_one_task_in_progress(self):
        status = self.validated_data.get("status")
        if (
            (user := self.validated_data.get("user"))
            and status
            and status.id in Status.STATUSES_PROGRESS_IDS()
        ):
            tasks_in_progress = user.user_tasks.filter(
                status__in=Status.STATUSES_PROGRESS_IDS()
            )
            if tasks_in_progress.count() > 0 and any(
                [task != self.instance for task in tasks_in_progress]
            ):
                raise ValidationError(
                    {
                        "user": f"У користувача {user.username} вже є активна задача {tasks_in_progress[0].name}"
                    }
                )

    def _check_user_for_progress_status(self):
        stat = self.validated_data.get("status")
        if (
            stat
            and (stat.id in Status.STATUSES_PROGRESS_IDS())
            and not self.validated_data.get("user")
        ):
            if not self.instance.user:
                raise ValidationError(
                    {
                        "user": f"Для переводу задачі в статус '{stat.name}' має бути вказаний виконавець"
                    }
                )

    def _check_user_is_department_member_of_task_department(self):
        user = self.validated_data.get("user")
        department = self.validated_data.get("department")

        if (
            department
            and self.instance
            and department.id != self.instance.department_id
            and not self.context.get("request").user.is_admin
            or self.context.get("request").user.id != self.instance.department.head.id
        ):
            raise ValidationError(
                {
                    "department": "Відділ може змінити тільки адміністратор або керівник відділу для якого створено задачу"
                }
            )
        if user and department:
            if user.department_id != department.id:
                raise ValidationError(
                    {
                        "department": "Виконавцем можна призначити тільки користувача з відділу для якого створено задачу"
                    }
                )

        if user and self.instance and not department:
            if user.department_id != self.instance.department_id:
                raise ValidationError(
                    {
                        "department": "Виконавцем можна призначити тільки користувача з відділу для якого створено задачу"
                    }
                )

        if (
            not user
            and "user" not in self.validated_data
            and self.instance
            and department
        ):
            if self.instance.user:
                if self.instance.user.department_id != department.id:
                    raise ValidationError(
                        {
                            "user": "Не можна змінити відділ і залишити відповідальним користувача з іншого відділу"
                        }
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
                if key == "status":
                    text = Status.objects.get_or_none(id=value.id).translation
                elif key == "user" and value:
                    text = f"{value.last_name} {value.first_name}"
                else:
                    text = value
                change_list.append(f"{self.fields.fields.get(key).label} - {text}")
            data["log_text"] = f'Внесено зміни: {", ".join(change_list)}'
            data["is_log"] = True
        return data

    def save(self, **kwargs):
        comment_data = self._create_log_data()
        self.check_user_has_only_one_task_in_progress()
        self._check_user_is_department_member_of_task_department()

        if year := self.validated_data.get("year"):
            Task.check_year_is_correct(year=year)

        if task_name := self.validated_data.get("name"):
            task_scale = self.validated_data.get("scale") or self.instance.scale
            Task.check_name_correspond_to_scale_rule(task_name, task_scale)

        if not self.instance:
            super().save()
            self.instance.start_time_tracker()
            self.instance.create_log_comment(**comment_data)
            return self.instance

        if validated_status := self.validated_data.get("status"):
            if (
                self.instance.status.id == Status.STATUS_DONE_ID()
                and validated_status.id != Status.STATUS_DONE_ID()
                and (
                    self.context.get("request").user.is_admin
                    or self.context.get("request").user.id
                    == self.instance.department.head.id
                )
            ):
                self.instance.done = None
                super().save()
                self.instance.start_time_tracker()
                self.instance.create_log_comment(**comment_data)
                return self.instance

            time_tracker = self.instance.task_time_trackers.get(
                task__id=self.instance.id, status=TimeTrackerStatuses.IN_PROGRESS
            )
            if validated_status.id != time_tracker.task_status:
                self._check_user_for_progress_status()
                time_tracker.change_status_done()
                super().save()
                if validated_status.id != Status.STATUS_DONE_ID():
                    self.instance.start_time_tracker()
                else:
                    self.instance.done = datetime.now()
                    super().save()
                self.instance.create_log_comment(**comment_data)
                return self.instance

        super().save()
        self.instance.create_log_comment(**comment_data)
        return self.instance
