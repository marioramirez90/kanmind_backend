from django.urls import path
from .views import (
    AssignedToMeTaskListView,
    CommentDestroyView,
    CommentListCreateView,
    ReviewingTaskListView,
    TaskCreateView,
    TaskDetailView,
)

urlpatterns = [
    path("tasks/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/assigned-to-me/", AssignedToMeTaskListView.as_view(), name="tasks-assigned-to-me"),
    path("tasks/reviewing/", ReviewingTaskListView.as_view(), name="tasks-reviewing"),
    path("tasks/<int:task_id>/", TaskDetailView.as_view(), name="task-detail"),
    path("tasks/<int:task_id>/comments/", CommentListCreateView.as_view(), name="task-comments"),
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        CommentDestroyView.as_view(),
        name="comment-detail",
    ),
]