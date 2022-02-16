from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .models import StatusHistory, Task
from .views import GenericTaskView


class AuthTest(TestCase):
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
