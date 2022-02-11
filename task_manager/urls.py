from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from tasks import views
from tasks.apiviews import TaskViewSet, StatusHistoryView
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register("api/tasks", TaskViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tasks/", views.GenericTaskView.as_view()),
    path("create_task/", views.GenericCreateTaskView.as_view()),
    path("user/signup/", views.UserCreateView.as_view()),
    path("user/login/", views.UserLoginView.as_view()),
    path("user/logout/", LogoutView.as_view()),
    path("update_task/<pk>", views.GenericTaskUpdateView.as_view()),
    path("detail_task/<pk>", views.GenericTaskDetailView.as_view()),
    path("delete_task/<pk>", views.GenericTaskDeleteView.as_view()),
    path("complete_task/<pk>/", views.MarkTaskCompleteView.as_view()),
    path("api/history/<id>", StatusHistoryView.as_view()),
    path("settings/<pk>", views.SettingsView.as_view()),
    path("__reload__/", include("django_browser_reload.urls")),
] + router.urls
