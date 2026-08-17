from django.urls import path
from .views import BoardDetailView, BoardListCreateView, EmailCheckView

urlpatterns = [
    path("email-check/", EmailCheckView.as_view(), name="email-check"),
    path("boards/", BoardListCreateView.as_view(), name="board-list-create"),
    path("boards/<int:pk>/", BoardDetailView.as_view(), name="board-detail"),
]