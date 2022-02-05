from django.contrib.auth.models import User
from django_filters.rest_framework import (
    CharFilter,
    ChoiceFilter,
    DjangoFilterBackend,
    FilterSet,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from tasks.models import STATUS_CHOICES, StatusHistory, Task


class TaskFilter(FilterSet):
    title = CharFilter(lookup_expr="icontains")
    status = ChoiceFilter(choices=STATUS_CHOICES)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]


class TaskSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ["title", "description", "user"]


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, deleted=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StatusHistorySerializer(ModelSerializer):
    class Meta:
        model = StatusHistory
        fields = ["old_status", "new_status", "updation_date"]


class StatusHistoryView(ListAPIView):
    queryset = StatusHistory.objects.all()
    serializer_class = StatusHistorySerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ["updation_date", "new_status"]

    def get_queryset(self):
        id = self.kwargs["id"]
        return StatusHistory.objects.filter(task_id=id)
