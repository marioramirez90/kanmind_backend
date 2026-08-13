from django.contrib.auth.models import User
from rest_framework import serializers


class UserCheckSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source="first_name")

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]