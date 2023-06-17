from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import User, Department, Task, TimeTracker, Comment


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


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "head")
    search_fields = ("name",)
    ordering = ("name",)

    class Meta:
        model = Department


class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "status",
        "department",
        "user_link",
        "quarter",
        "change_time_estimate",
        "correct_time_estimate",
        "otk_time_estimate",
        "category",
        "done",
    )
    list_filter = ("department", "status", "user", "quarter", "done")
    search_fields = ("name",)
    ordering = ("name", "department")

    class Meta:
        model = Task

    def user_link(self, obj):
        if obj.user:
            url = reverse("admin:api_user_change", args=[obj.user.id])
            link = f'<a href="{url}">{obj.user}</a>'
            return mark_safe(link)

    user_link.short_description = "Виконавець"


class TimeCheckerAdmin(admin.ModelAdmin):
    list_display = ("task", "status", "user_link", "start_time", "end_time", "hours")
    list_filter = ("task", "user", "status")
    search_fields = ("task", "user", "status")
    ordering = ("status", "task", "user")

    class Meta:
        model = TimeTracker

    def user_link(self, obj):
        url = reverse("admin:api_user_change", args=[obj.user.id])
        link = f'<a href="{url}">{obj.user}</a>'
        return mark_safe(link)

    user_link.short_description = "Виконавець"


class CommentAdmin(admin.ModelAdmin):
    list_display = ('body', 'task', 'user', 'created')
    list_filter = ('task', 'user', 'created')
    search_fields = ('body',)


admin.site.register(Department, DepartmentAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TimeTracker, TimeCheckerAdmin)
admin.site.register(Comment, CommentAdmin)
