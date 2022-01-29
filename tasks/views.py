from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponseRedirect
from django.views.generic import ListView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from tasks.models import Task


class AuthorizedTaskManager(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user).order_by(
            "priority"
        )


class GenericTaskView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks.html"
    context_object_name = "tasks"

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
    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 1:
            raise ValidationError("Title not cleaned")
        return title.capitalize()

    class Meta:
        model = Task
        fields = ["title", "description", "completed", "priority"]


class GenericTaskFormView(AuthorizedTaskManager):
    form_class = TaskCreateForm
    template_name = "task_form.html"
    success_url = "/tasks"

    def priority_update_helper(self, priority: int):
        task_obj = self.get_queryset().filter(priority=priority)
        if task_obj.exists():
            self.priority_update_helper(priority + 1)
            task_obj.update(priority=priority + 1)

    def fix_priority(self, priority: int, id: int):
        task = self.get_queryset().filter(priority=priority, id=id)
        if not task.exists():
            self.priority_update_helper(priority)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.fix_priority(self.object.priority, self.object.id)
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


class UserCreateView(CreateView):
    form_class = UserCreationForm
    template_name = "user_create.html"
    success_url = "/user/login"
