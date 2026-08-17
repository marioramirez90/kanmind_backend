from django.contrib.auth.models import User
from rest_framework import serializers
from boards_app.models import Board


class UserCheckSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source="first_name")

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class BoardListSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False, write_only=True
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
            "members",
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count() if hasattr(obj, "tasks") else 0

    def get_tasks_to_do_count(self, obj):
        if hasattr(obj, "tasks"):
            return obj.tasks.filter(status="to-do").count()
        return 0

    def get_tasks_high_prio_count(self, obj):
        if hasattr(obj, "tasks"):
            return obj.tasks.filter(priority="high").count()
        return 0

    def create(self, validated_data):
        members_data = validated_data.pop("members", [])
        
        board = Board.objects.create(**validated_data)
        
        if members_data:
            board.members.set(members_data)
            
        return board


class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = UserCheckSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "created_at"]