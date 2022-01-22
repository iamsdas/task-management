from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from tasks.models import Task


def tasks_view(request: HttpRequest):
    search_term = request.GET.get("search")
    tasks = Task.objects.filter(deleted=False, completed=False)
    if search_term:
        tasks = tasks.filter(title__icontains=search_term)
    return render(request, "tasks.html", {"tasks": tasks})


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


def add_task_view(request: HttpRequest):
    task_val = request.GET.get("task")
    task_obj = Task(title=task_val)
    task_obj.save()
    return HttpResponseRedirect("/tasks")


def delete_task_view(request: HttpRequest, index: int):
    Task.objects.filter(id=index).update(deleted=True)
    return HttpResponseRedirect("/tasks")


def complete_task_view(request: HttpRequest, index: int):
    Task.objects.filter(id=index).update(completed=True)
    return HttpResponseRedirect("/tasks")
