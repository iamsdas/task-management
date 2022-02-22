from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponseRedirect
from django.views.generic import ListView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from task_manager.tasks.models import Task, UserMetadata

User = get_user_model()


class AuthorizedTaskManager(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user).order_by(
            "priority"
        )


class GenericTaskView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks.html"
    context_object_name = "tasks"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        obj, _ = UserMetadata.objects.get_or_create(user=self.request.user)
        context["settings_id"] = obj.pk
        return context

    def get_queryset(self):
        tasks = Task.objects.filter(deleted=False, user=self.request.user)
        task_type = self.request.GET.get("type")
        search_term = self.request.GET.get("search")

        if task_type == "completed":
            tasks = tasks.filter(completed=True)
        elif task_type in (None, "pending"):
            tasks = tasks.filter(completed=False)
        if search_term:
            tasks = tasks.filter(title__icontains=search_term)

        return tasks.order_by("priority")


class TaskCreateForm(ModelForm):
    def clean_priority(self):
        priority = self.cleaned_data["priority"]
        if priority <= 0:
            raise ValidationError("Priority must be greater than 0")
        return priority

    class Meta:
        model = Task
        fields = ["title", "description", "completed", "status", "priority"]


class GenericTaskFormView(AuthorizedTaskManager):
    form_class = TaskCreateForm
    template_name = "task_form.html"
    success_url = "/tasks"

    def fix_priority(self, priority: int, id: int, completed: bool):
        with transaction.atomic():
            tasks = self.get_queryset().filter(completed=False).select_for_update()
            if completed or tasks.filter(id=id, priority=priority).exists():
                return

            tasks = tasks.exclude(id=id)
            update_queries = []

            while True:
                try:
                    task = tasks.get(priority=priority)
                    priority += 1
                    task.priority += 1
                    update_queries.append(task)
                except ObjectDoesNotExist:
                    break

            Task.objects.bulk_update(update_queries, ["priority"])

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.fix_priority(self.object.priority, self.object.id, self.object.completed)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class GenericCreateTaskView(GenericTaskFormView, CreateView):
    pass


class GenericTaskUpdateView(GenericTaskFormView, UpdateView):
    pass


class GenericTaskDetailView(AuthorizedTaskManager, DetailView):
    model = Task
    template_name = "task_detail.html"


class GenericTaskDeleteView(AuthorizedTaskManager, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/tasks"


class MarkTaskCompleteView(AuthorizedTaskManager, View):
    def get(self, request: HttpRequest, pk: int):
        task_obj = self.get_queryset().filter(id=pk)
        if task_obj.exists():
            task_obj.update(completed=True)
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))


class UserLoginView(LoginView):
    template_name = "user_login.html"


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)


class UserCreateView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "user_create.html"
    success_url = "/user/login"


class SettingsForm(ModelForm):
    def clean_preffered_mail_hour(self):
        time = self.cleaned_data["preffered_mail_hour"]
        if time < 0 or time > 23:
            raise ValidationError("Invalid Hour")
        return time

    class Meta:
        model = UserMetadata
        fields = ["preffered_mail_hour"]


class SettingsView(UpdateView, LoginRequiredMixin):
    form_class = SettingsForm
    success_url = "/tasks"
    template_name = "settings.html"

    def get_queryset(self):
        return UserMetadata.objects.filter(user=self.request.user)
