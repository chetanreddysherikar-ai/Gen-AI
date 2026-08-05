from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import SearchHistory, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


class UserAdmin(BaseUserAdmin):
    """Extends the default Django User admin to also manage the linked profile."""

    inlines = (UserProfileInline,)
    list_display = (
        "username", "email", "get_full_name_display",
        "is_staff", "is_active", "date_joined",
    )
    list_filter = ("is_staff", "is_superuser", "is_active")

    def get_full_name_display(self, obj):
        return getattr(obj, "userprofile", None) and obj.userprofile.full_name or "—"
    get_full_name_display.short_description = "Full Name"


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "topic", "created_at")
    list_filter = ("created_at",)
    search_fields = ("topic", "user__username")
    date_hierarchy = "created_at"


# Re-register User with the profile inline attached.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.site_header = "AI Text Generator — Admin"
admin.site.site_title = "AI Text Generator Admin"
admin.site.index_title = "Site Administration"
