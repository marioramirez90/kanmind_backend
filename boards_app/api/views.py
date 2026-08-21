from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics, status, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from boards_app.models import Board
from .serializers import (
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
    UserCheckSerializer,
)


class EmailCheckView(APIView):
    """Checks if an email exists in the system and returns user info."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email")

        if not email:
            return Response(
                {"error": "Email parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
            serializer = UserCheckSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error": "Email not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class BoardListCreateView(generics.ListCreateAPIView):
    """Lists boards where user is owner or member, and creates new boards."""
    serializer_class = BoardListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def perform_create(self, serializer):
        board = serializer.save(owner=self.request.user)
        board.members.add(self.request.user)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieves, updates, and deletes board details (only owner can delete)."""
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "board_id"
    queryset = Board.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def get_object(self):
        board = super().get_object()
        user = self.request.user

        is_member = board.members.filter(id=user.id).exists()
        is_owner = board.owner == user

        if not (is_member or is_owner):
            raise PermissionDenied(
                "Verboten. Der Benutzer muss entweder Mitglied oder Eigentümer des Boards sein."
            )

        if self.request.method == "DELETE" and board.owner != user:
            raise PermissionDenied("Nur der Eigentümer kann das Board löschen.")

        return board

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)