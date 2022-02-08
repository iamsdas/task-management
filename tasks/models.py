from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("IN_PROGRESS", "IN_PROGRESS"),
    ("COMPLETED", "COMPLETED"),
    ("CANCELLED", "CANCELLED"),
)


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    priority = models.IntegerField()
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title


class StatusHistory(models.Model):
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE)
    old_status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    new_status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    updation_date = models.DateTimeField(auto_now=True)


@receiver(pre_save, sender=Task)
def update_status_history(sender, instance, **kwargs):
    if not instance._state.adding:
        print(instance)
        old_task = Task.objects.get(pk=instance.pk)
        old_status = old_task.status
        new_status = instance.status
        if old_status != new_status:
            StatusHistory.objects.create(
                task_id=instance, old_status=old_status, new_status=new_status
            )
