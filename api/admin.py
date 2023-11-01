from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import User, Department, Task, TimeTracker, Comment


class AdditionForeignField:
    def user_name(self, obj):
        if obj.user:
            return f'{obj.user.first_name} {obj.user.last_name}'

    user_name.short_description = "Виконавець"

    def head_name(self, obj):
        if obj.head:
            return f'{obj.head.first_name} {obj.head.last_name}'

    head_name.short_description = "Керівник відділу"

    def status_name(self, obj):
        return obj.status.translation

    status_name.short_description = 'Статус'

    def task_status_name(self, obj):
        return obj.task_status.translation

    task_status_name.short_description = 'Статус задачі'

    def department_name(self, obj):
        return obj.department.name

    department_name.short_description = 'Відділ'

    def task_name(self, obj):
        return obj.task.name

    task_name.short_description = 'Задача'


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "department")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "department",
            "is_active",
            "is_admin",
        )

    def clean_password(self):
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        "username",
        "first_name",
        "last_name",
        "department",
        "is_active",
        "role",
        "is_admin",
    )
    list_filter = ("department", "is_active")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "department",
                    "is_active",
                )
            },
        ),
        ("Permissions", {"fields": ("is_admin",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "department",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    search_fields = ("username", "first_name", "last_name")
    ordering = ("username",)
    filter_horizontal = ()


class DepartmentAdmin(admin.ModelAdmin, AdditionForeignField):
    list_display = ("name", "head_name", "is_verifier")
    search_fields = ("name",)
    ordering = ("name",)

    class Meta:
        model = Department


class TaskAdmin(admin.ModelAdmin, AdditionForeignField):
    list_display = (
        "name",
        "status_name",
        "scale",
        "department_name",
        "user_name",
        "quarter",
        "editing_time_estimate",
        "correcting_time_estimate",
        "tc_time_estimate",
        "category",
        "year",
        "done",
    )
    list_filter = ("department", "status", "user", "quarter", "done")
    search_fields = ("name",)
    ordering = ("name", "department")

    class Meta:
        model = Task


class TimeTrackerAdmin(admin.ModelAdmin, AdditionForeignField):
    list_display = ("task_name", "status", "user_link", "start_time", "end_time", "hours", "task_status_name", "task_department")
    list_filter = ("task", "user", "status", "task_status")
    search_fields = ("task", "user", "status")
    ordering = ("status", "task", "user", "task_status")

    class Meta:
        model = TimeTracker

    def user_link(self, obj):
        url = reverse("admin:api_user_change", args=[obj.user.id])
        link = f'<a href="{url}">{obj.user}</a>'
        return mark_safe(link)

    user_link.short_description = "Виконавець"


class CommentAdmin(admin.ModelAdmin, AdditionForeignField):
    list_display = ('body', 'task', 'user', 'created')
    list_filter = ('task', 'user', 'created')
    search_fields = ('body',)


admin.site.register(Department, DepartmentAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TimeTracker, TimeTrackerAdmin)
admin.site.register(Comment, CommentAdmin)
