from django.urls import path
from .views import AssignedToMeTaskListView, ReviewingTaskListView

urlpatterns = [
    path("tasks/assigned-to-me/", AssignedToMeTaskListView.as_view(), name="tasks-assigned-to-me"),
    path("tasks/reviewing/", ReviewingTaskListView.as_view(), name="tasks-reviewing"),
]