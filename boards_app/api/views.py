from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserCheckSerializer


class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

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