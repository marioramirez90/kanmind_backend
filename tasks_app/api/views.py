from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ..models import Comment, Task
from .permissions import IsCommentAuthor, IsTaskBoardMember, IsTaskBoardOwner
from .serializers import CommentSerializer, TaskSerializer


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
        serializer.save()


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_url_kwarg = "task_id"

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [permissions.IsAuthenticated(), IsTaskBoardOwner()]
        return [permissions.IsAuthenticated(), IsTaskBoardMember()]

    def update(self, request, *args, **kwargs):
        if "board" in request.data:
            return Response(
                {"detail": "Das Ändern des Boards ist nicht erlaubt."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_task(self):
        return get_object_or_404(Task, id=self.kwargs["task_id"])

    def get_queryset(self):
        task = self.get_task()
        return task.comments.all().order_by("created_at")

    def perform_create(self, serializer):
        task = self.get_task()
        serializer.save(author=self.request.user, task=task)


class CommentDestroyView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentAuthor]

    def get_object(self):
        return get_object_or_404(
            Comment,
            id=self.kwargs["comment_id"],
            task_id=self.kwargs["task_id"],
        )