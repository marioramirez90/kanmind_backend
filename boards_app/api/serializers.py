from django.contrib.auth.models import User
from rest_framework import serializers
from boards_app.models import Board
from tasks_app.models import Task


class UserCheckSerializer(serializers.ModelSerializer):
    """Serializes user basic info: id, email, and full name."""
    fullname = serializers.CharField(source="first_name")

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class BoardListSerializer(serializers.ModelSerializer):
    """Serializes board summary with member counts and task statistics."""
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


class TaskInBoardSerializer(serializers.ModelSerializer):
    """Serializes task details for display within a board."""
    assignee = UserCheckSerializer(read_only=True)
    reviewer = UserCheckSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        return obj.comments.count() if hasattr(obj, "comments") else 0


class BoardDetailSerializer(serializers.ModelSerializer):
    """Serializes complete board info including members and all tasks."""
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = UserCheckSerializer(many=True, read_only=True)
    tasks = TaskInBoardSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Updates board title and manages board member list."""
    owner_data = UserCheckSerializer(source="owner", read_only=True)
    members_data = UserCheckSerializer(source="members", many=True, read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = Board
        fields = ["id", "title", "owner_data", "members_data", "members"]

    def update(self, instance, validated_data):
        if "title" in validated_data:
            instance.title = validated_data["title"]
        if "members" in validated_data:
            instance.members.set(validated_data["members"])
        instance.save()
        return instance