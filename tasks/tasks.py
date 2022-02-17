from datetime import datetime

from celery.schedules import crontab
from django.core.mail import send_mail
from task_manager.celery import app

from tasks.models import STATUS_CHOICES, Task, UserMetadata


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour="*", minute=0),
        mail_helper.s(),
    )


@app.task(bind=True)
def mail_helper(self):
    date = datetime.now()
    for user_data in UserMetadata.objects.exclude(previous_report_date=date.day).filter(
        preffered_mail_hour__lte=date.hour
    ):
        try:
            send_mail_reminder(user_data.user)
            user_data.previous_report_date = date.day
            user_data.save()
        except:
            self.retry(countdown=10)


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
