from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .models import Task
from .views import GenericTaskView


class AuthTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="test_user", email="bruce@wayne.org", password="i_am_batman"
        )

    def test_unauthenticated_redirection(self):
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/user/login?next=/tasks/")

    def test_authenticated_response(self):
        request = self.factory.get("/tasks/")
        request.user = self.user
        response = GenericTaskView.as_view()(request)
        self.assertEqual(response.status_code, 200)
