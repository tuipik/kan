from datetime import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.serializers.map_sheet_serializers import MapSheetSerializer
from kanban import settings
from api.models import (
    User,
    Department,
    Task,
    Comment,
    TimeTracker,
    Statuses,
)
from api.choices import UserRoles, TimeTrackerStatuses

from api.user_validation.department_validator import DepartmentValidator


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


class TaskSerializer(serializers.ModelSerializer):

    MAP_SHEET_REQUIRED_FIELDS = ("scale", "name", "year")

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), default=None, allow_null=True, many=False, label="Відповідальний"
    )
    user_obj = UserBaseSerializer(source="user", read_only=True)
    department_obj = DepartmentSerializer(source="department", read_only=True)
    quarter_display_value = serializers.CharField(
        source="get_quarter_display", read_only=True
    )
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
    map_sheet = MapSheetSerializer(default=None, allow_null=True, read_only=True)

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
            "map_sheet",
        ]

    def _check_department_not_verifier(self):
        department = self.validated_data.get("department")
        if department and department.is_verifier:
            raise ValidationError(
                {"department": "Задача не може належати перевіряючему відділу."}
            )

    def check_user_has_only_one_task_in_progress(self):
        status = self.validated_data.get("status")
        user = self.validated_data.get("user") or (
            self.instance.user if self.instance else None
        )
        if user and status and status in Statuses.STATUSES_PROGRESS():
            tasks_in_progress = user.user_tasks.filter(
                status__in=Statuses.STATUSES_PROGRESS()
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
            and (stat in Statuses.STATUSES_PROGRESS())
            and not self.validated_data.get("user")
        ):
            if not self.instance.user or self.context.get('request').user != self.instance.user:
                raise ValidationError(
                    {
                        "user": f"Для переводу задачі в статус '{Statuses[stat].label}' має бути вказаний виконавець"
                    }
                )

    def _check_user_is_department_member_of_task_department(self):
        task = self.instance
        user = self.validated_data.get("user") or (
            task.user if task and task.user and task.user.role != UserRoles.VERIFIER.value else None
        )
        department = self.validated_data.get("department", None)
        status = self.validated_data.get("status") or (task.status if task else None)
        request_user = getattr(self.context.get("request", {}), "user", None)

        validation_strategy_data = [self.validated_data, task, request_user, status]
        department_validator = DepartmentValidator(*validation_strategy_data)

        if (
            department_validator.is_vd_department_and_task_department_different()
            and department_validator.not_admin_or_not_head()
        ):
            raise ValidationError(
                {
                    "department": "Відділ може змінити тільки адміністратор або керівник відділу для якого створено задачу"
                }
            )
        if user and department and user.department_id != department.id:
            raise ValidationError(
                {
                    "department": "Виконавцем можна призначити тільки користувача з відділу для якого створено задачу"
                }
            )

        if user and task and not department:
            if status != Statuses.DONE.value and user.department_id != task.department_id and (
                #user.role not in [UserRoles.CORRECTOR.value, UserRoles.VERIFIER.value]
                user.role == UserRoles.EDITOR.value
                or department_validator.validate_corrector_status()
                or department_validator.validate_verifier_status()
            ):
                raise ValidationError(
                    {
                        "department": "Виконавцем можна призначити тільки користувача з відділу для якого створено задачу"
                    }
                )

        if not user and task and department:
            if task.user and task.user.department_id != department.id:
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
            data["log_text"] = (
                f'Створено задачу для {self.validated_data.get("name", "")}'
            )
            data["is_log"] = True
        elif self.context["request"].method in ["PUT", "PATCH"]:
            change_list = []
            for key, value in self.validated_data.items():
                if key == "status":
                    text = value
                elif key == "user" and value:
                    text = f"{value.last_name} {value.first_name}"
                else:
                    text = value
                change_list.append(f"{self.fields.fields.get(key).label} - {text}")
            data["log_text"] = f'Внесено зміни: {", ".join(change_list)}'
            data["is_log"] = True
        return data

    def _save_map_sheet(self):
        map_sheet_data = {}

        for field in self.MAP_SHEET_REQUIRED_FIELDS:
            if validated_field := self.validated_data.get(field):
                map_sheet_data[field] = validated_field

        map_sheet_serializer = MapSheetSerializer(
            data=map_sheet_data, instance=getattr(self.instance, 'map_sheet', None), partial=True
        )
        map_sheet_serializer.is_valid(raise_exception=True)
        return map_sheet_serializer.save()

    def save(self, **kwargs):
        comment_data = self._create_log_data()
        self.check_user_has_only_one_task_in_progress()
        self._check_user_is_department_member_of_task_department()
        self._check_department_not_verifier()

        if year := self.validated_data.get("year"):
            Task.check_year_is_correct(year=year)

        if task_name := self.validated_data.get("name"):
            task_scale = self.validated_data.get("scale") or self.instance.scale
            Task.check_name_correspond_to_scale_rule(task_name, task_scale)

        map_sheet = None
        if any(field in self.validated_data.keys() for field in self.MAP_SHEET_REQUIRED_FIELDS):
            map_sheet = self._save_map_sheet()

        if not self.instance:
            map_sheet_kwargs = {}
            if map_sheet:
                map_sheet_kwargs["map_sheet"] = map_sheet
            super().save(**map_sheet_kwargs)
            self.instance.start_time_tracker()
            self.instance.create_log_comment(**comment_data)
            return self.instance

        if map_sheet:
            self.instance.map_sheet = map_sheet

        time_tracker = self.instance.task_time_trackers.get_or_none(
            task__id=self.instance.id, status=TimeTrackerStatuses.IN_PROGRESS
        )
        if validated_status := self.validated_data.get("status"):
            if (
                self.instance.status == Statuses.DONE.value
                and validated_status != Statuses.DONE.value
                and (
                    self.context.get("request").user.is_admin
                    or self.context.get("request").user.id
                    == self.instance.department.head.id
                )
            ):
                self.instance.done = None
                if "user" not in self.validated_data:
                    self.instance.update_user_in_queue_status(status=validated_status)
                super().save(**kwargs)
                self.instance.start_time_tracker()
                self.instance.create_log_comment(**comment_data)
                return self.instance

            if validated_status != time_tracker.task_status:
                self._check_user_for_progress_status()
                time_tracker.change_status_done()
                super().save(**kwargs)
                if validated_status != Statuses.DONE.value:
                    if "user" not in self.validated_data:
                        self.instance.update_user_in_queue_status(
                            status=validated_status
                        )
                    self.instance.start_time_tracker()
                else:
                    self.instance.done = datetime.now()
                    self.instance.user = None
                    super().save(**kwargs)
                self.instance.create_log_comment(**comment_data)
                return self.instance
        if self.validated_data.get("user") and not validated_status:
            self._check_user_for_progress_status()
            time_tracker.change_status_done()
            super().save(**kwargs)
            self.instance.start_time_tracker()
            self.instance.create_log_comment(**comment_data)
            return self.instance

        super().save(**kwargs)
        self.instance.create_log_comment(**comment_data)
        return self.instance
