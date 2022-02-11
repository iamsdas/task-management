from celery.schedules import crontab
from django.contrib.auth.models import User
from django.core.mail import send_mail
from task_manager.celery import app

from tasks.models import STATUS_CHOICES, Task, UserSetting


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    for user in User.objects.all():
        settings, _ = UserSetting.objects.get_or_create(user=user)
        sender.add_periodic_task(
            crontab(hour=settings.preffered_mail_hour),
            send_mail_reminder.s(user.id),
        )


@app.task
def send_mail_reminder(user):
    print(f"starting to process mail for user {user}")

    email_content = "Task Status Report:\n"
    for choice in STATUS_CHOICES:
        pending_qs = Task.objects.filter(user=user, status=choice[0], deleted=False)
        email_content += f"- {pending_qs.count()} tasks which are {choice[0]}\n"

    send_mail(
        "Task Status Report",
        email_content,
        "tasks@taskmanager.org",
        [user.email],
        fail_silently=False,
    )
    print(f"Completed processing for user {user}")
