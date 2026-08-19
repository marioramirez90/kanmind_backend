from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from tasks_app.models import Task
from .serializers import TaskSerializer


class AssignedToMeTaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class ReviewingTaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


class TaskCreateView(generics.CreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        board = serializer.validated_data.get("board")
        user = self.request.user

        is_member = board.members.filter(id=user.id).exists()
        is_owner = board.owner == user

        if not (is_member or is_owner):
            raise PermissionDenied("Du musst Mitglied des Boards sein, um eine Task zu erstellen.")

        serializer.save()


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "task_id"

    def get_object(self):
        task = super().get_object()
        user = self.request.user
        board = task.board

        is_member = board.members.filter(id=user.id).exists()
        is_owner = board.owner == user

        if self.request.method in ["PATCH", "PUT"]:
            if not (is_member or is_owner):
                raise PermissionDenied("Nur Board-Mitglieder dürfen diese Task bearbeiten.")

        if self.request.method == "DELETE":
            if not is_owner:
                raise PermissionDenied("Nur der Board-Eigentümer darf die Task löschen.")

        return task

    def update(self, request, *args, **kwargs):
        if "board" in request.data:
            return Response(
                {"detail": "Das Ändern des Boards ist nicht erlaubt."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)