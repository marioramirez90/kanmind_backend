from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from ..models import Comment, Task
from .permissions import IsCommentAuthor, IsTaskBoardMember, IsTaskCreatorOrBoardOwner
from .serializers import CommentSerializer, TaskSerializer


class AssignedToMeTaskListView(generics.ListAPIView):
    """Lists all tasks assigned to the current user."""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class ReviewingTaskListView(generics.ListAPIView):
    """Lists all tasks where the current user is assigned as reviewer."""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


class TaskCreateView(generics.CreateAPIView):
    """Creates a new task on a board if user is a board member or owner."""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.validated_data["board"]
        user = request.user
        is_member = board.members.filter(id=user.id).exists()
        is_owner = board.owner == user
        if not (is_member or is_owner):
            return Response(
                {"detail": "Verboten. Der Benutzer muss Mitglied des Boards sein, um eine Task zu erstellen."},
                status=status.HTTP_403_FORBIDDEN,
            )
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieves, updates, and deletes tasks (only creator or board owner can delete)."""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_url_kwarg = "task_id"

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [permissions.IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return [permissions.IsAuthenticated(), IsTaskBoardMember()]

    def update(self, request, *args, **kwargs):
        if "board" in request.data:
            return Response(
                {"detail": "Das Ändern des Boards ist nicht erlaubt."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)


class CommentListCreateView(generics.ListCreateAPIView):
    """Lists comments on a task and creates new comments for board members."""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_task(self):
        task = get_object_or_404(Task, id=self.kwargs["task_id"])
        user = self.request.user
        board = task.board
        is_member = board.members.filter(id=user.id).exists()
        is_owner = board.owner == user
        if not (is_member or is_owner):
            raise PermissionDenied("Verboten. Der Benutzer muss Mitglied des Boards sein, zu dem die Task gehört.")
        return task

    def get_queryset(self):
        task = self.get_task()
        return task.comments.all().order_by("created_at")

    def perform_create(self, serializer):
        task = self.get_task()
        serializer.save(author=self.request.user, task=task)


class CommentDestroyView(generics.DestroyAPIView):
    """Deletes a comment (only the author can delete their own comments)."""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentAuthor]

    def get_object(self):
        obj = get_object_or_404(
            Comment,
            id=self.kwargs["comment_id"],
            task_id=self.kwargs["task_id"],
        )
        self.check_object_permissions(self.request, obj)
        return obj