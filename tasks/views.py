from django.http import HttpResponseRedirect
from django.shortcuts import render

pending_tasks = []
completed_tasks = []


def pending_tasks_view(request):
    return render(request, "tasks.html", {"tasks": pending_tasks})


def all_tasks_view(request):
    tasks = pending_tasks + completed_tasks
    return render(request, "tasks_list.html", {"tasks": tasks})


def completed_tasks_view(request):
    return render(request, "tasks_list.html", {"tasks": completed_tasks})


def add_task_view(request):
    pending_tasks.append(request.GET.get("task"))
    return HttpResponseRedirect("/tasks")


def delete_task_view(request, index):
    if index <= len(pending_tasks):
        pending_tasks.pop(index - 1)
    return HttpResponseRedirect("/tasks")


def mark_complete_task_view(request, index):
    if index <= len(pending_tasks):
        new_task = pending_tasks.pop(index - 1)
        completed_tasks.append(new_task)
    return HttpResponseRedirect("/tasks")
