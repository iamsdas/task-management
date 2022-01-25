from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from tasks.models import Task


class AuthorizedTaskManager(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user)


class GenericTaskView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks.html"
    context_object_name = "tasks"
    paginate_by = 5

    def get_queryset(self):
        search_term = self.request.GET.get("search")
        tasks = Task.objects.filter(
            deleted=False, completed=False, user=self.request.user
        )
        if search_term:
            tasks = tasks.filter(title__icontains=search_term)
        return tasks


class TaskCreateForm(ModelForm):
    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 10:
            raise ValidationError("Title not cleaned")
        return title.upper()

    class Meta:
        model = Task
        fields = ["title", "description", "completed"]


class GenericCreateTaskView(CreateView):
    form_class = TaskCreateForm
    template_name = "task_create.html"
    success_url = "/tasks"

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class GenericTaskUpdateView(AuthorizedTaskManager, UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_update.html"
    success_url = "/tasks"


class GenericTaskDetailView(AuthorizedTaskManager, DetailView):
    model = Task
    template_name = "task_detail.html"


class GenericTaskDeleteView(AuthorizedTaskManager, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/tasks"


class UserLoginView(LoginView):
    template_name = "user_login.html"


class UserCreateView(CreateView):
    form_class = UserCreationForm
    template_name = "user_create.html"
    success_url = "/login"


def completed_tasks_view(request: HttpRequest):
    tasks = Task.objects.filter(deleted=False, completed=True)
    return render(request, "tasks_list.html", {"completed_tasks": tasks})


def all_tasks_view(request: HttpRequest):
    completed_tasks = Task.objects.filter(deleted=False, completed=True)
    pending_tasks = Task.objects.filter(deleted=False, completed=False)
    return render(
        request,
        "tasks_list.html",
        {"pending_tasks": pending_tasks, "completed_tasks": completed_tasks},
    )


def complete_task_view(request: HttpRequest, index: int):
    Task.objects.filter(id=index).update(completed=True)
    return HttpResponseRedirect("/tasks")
