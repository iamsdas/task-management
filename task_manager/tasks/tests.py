from datetime import datetime
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from tasks.tasks import mail_helper, send_mail_reminder

from .models import StatusHistory, Task, UserMetadata
from .views import GenericTaskView, SettingsForm, SettingsView, TaskCreateForm


class TasksViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="test_user", email="bruce@wayne.org", password="i_am_batman"
        )

    def test_unauthenticated_redirection_tasks_view(self):
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/user/login?next=/tasks/")

    def test_authenticated_response_tasks_view(self):
        request = self.factory.get("/tasks/")
        request.user = self.user
        response = GenericTaskView.as_view()(request)
        self.assertEqual(response.status_code, 200)


class TaskFormTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="test_user", email="bruce@wayne.org", password="i_am_batman"
        )

    def test_negative_priority(self):
        form = TaskCreateForm(
            data={
                "title": "a",
                "description": "a",
                "priority": -1,
                "user": self.user,
                "completed": False,
                "status": "CANCELLED",
            }
        )
        self.assertFalse(form.is_valid())

    def test_normal_task_creation(self):
        form = TaskCreateForm(
            data={
                "title": "a",
                "description": "a",
                "priority": 1,
                "user": self.user,
                "completed": False,
                "status": "CANCELLED",
            }
        )
        self.assertTrue(form.is_valid())


class SettingsFormTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="test_user", email="bruce@wayne.org", password="i_am_batman"
        )

    def test_invalid_time_prefference(self):
        form = SettingsForm(
            data={
                "preffered_mail_hour": 26,
                "previous_report_date": 0,
                "user": self.user,
            }
        )
        self.assertFalse(form.is_valid())

    def test_valid_time_prefference(self):
        form = SettingsForm(
            data={
                "preffered_mail_hour": 23,
                "previous_report_date": 0,
                "user": self.user,
            }
        )
        self.assertTrue(form.is_valid())


class StatusHistoryTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="test_user", email="bruce@wayne.org", password="i_am_batman"
        )

    def test_status_updation(self):
        a = Task.objects.create(
            title="a", description="abc", priority=1, user=self.user
        )
        a.status = "COMPLETED"
        a.save()
        a.status = "CANCELLED"
        a.save()
        self.assertEqual(StatusHistory.objects.filter(task_id=a.id).count(), 2)


class SendMailTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="test_user", email="bruce@wayne.org", password="i_am_batman"
        )

    def test_send_mail_user_metadata(self):
        self.assertEqual(
            UserMetadata.objects.get(user=self.user).previous_report_date, 0
        )
        mail_helper()
        self.assertEqual(
            UserMetadata.objects.get(user=self.user).previous_report_date,
            datetime.now().day,
        )
