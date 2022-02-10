import time
from django.contrib.auth.models import User
from django.core.mail import send_mail
from tasks.models import Task
from datetime import timedelta
from celery.decorators import periodic_task
from task_manager.celery import app


@periodic_task(run_every=timedelta(seconds=10))
def send_mail_reminder():
    print("starting to process the mails")
    for user in User.objects.all():
        pending_qs = Task.objects.filter(user=user, completed=False, deleted=False)
        email_content = f"You have {pending_qs.count()} pending tasks"
        send_mail(
            "Pending Tasks from task manager",
            email_content,
            "taks@taskmanager.org",
            [user.email],
        )
        print(f"Completed processing for user {user.id}")


@app.task
def test_backgroud_jobs():
    print("This is from the background")
    for i in range(10):
        time.sleep(1)
        print(i)
