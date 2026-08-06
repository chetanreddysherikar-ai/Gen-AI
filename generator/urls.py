from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.user_login, name="login"),
    path("request-otp/", views.request_otp, name="request_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("logout/", views.user_logout, name="logout"),
    
    # PDF Download, Reader & Text to Audio
    path("download-pdf/", views.download_pdf, name="download_pdf"),
    path("read-pdf/", views.read_pdf, name="read_pdf"),
    path("text-to-audio/", views.text_to_audio, name="text_to_audio"),
    
    # NEW: Google Maps Routing
    path("route/", views.map_route, name="map_route"),

    # --- Custom Admin Panel (full CRUD for staff/superusers) ---
    path("panel/", views.admin_dashboard, name="admin_dashboard"),
    path("panel/users/", views.admin_user_list, name="admin_users"),
    path("panel/users/add/", views.admin_user_add, name="admin_user_add"),
    path("panel/users/<int:user_id>/edit/", views.admin_user_edit, name="admin_user_edit"),
    path("panel/users/<int:user_id>/delete/", views.admin_user_delete, name="admin_user_delete"),
    path("panel/history/", views.admin_history_list, name="admin_history"),
    path("panel/history/<int:history_id>/", views.admin_history_detail, name="admin_history_detail"),
    path("panel/history/<int:history_id>/delete/", views.admin_history_delete, name="admin_history_delete"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)