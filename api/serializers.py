from rest_framework import serializers

from .models import User, Department, Task, Comment, TimeTracker


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "head"]

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
    class Meta:
        model = Comment
        fields = "__all__"


class UserBaseSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), allow_null=True, many=False, label="Відділ"
    )
    comments = CommentSerializer(source="user_comments", allow_null=True, many=True)

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
            "task",
            "user",
            "status",
            "status_display_value",
            "start_time",
            "end_time",
            "hours",
        ]
        read_only_fields = ("start_time",)


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

    class Meta:
        model = Task
        fields = [
            "id",
            "name",
            "change_time_estimate",
            "correct_time_estimate",
            "otk_time_estimate",
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
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = UserDetailSerializer(instance.user).data
        representation["department"] = DepartmentSerializer(instance.department).data
        return representation
