from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def save(self):
        pw = self.validated_data["password"]
        repeated_pw = self.validated_data["repeated_password"]

        if pw != repeated_pw:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        email = self.validated_data["email"]
        fullname = self.validated_data["fullname"]

        account = User(
            email=email,
            username=email,
            first_name=fullname
        )
        account.set_password(pw)
        account.save()

        token, _ = Token.objects.get_or_create(user=account)
        account.token = token.key
        
        return account