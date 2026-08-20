from rest_framework import serializers
from django.contrib.auth.models import User
from tasks_app.models import Task, Comment


class UserSimpleSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    def get_fullname(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name if full_name else obj.username


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSimpleSerializer(read_only=True)
    reviewer = UserSimpleSerializer(read_only=True)

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assignee",
        write_only=True,
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="reviewer",
        write_only=True,
        required=False,
        allow_null=True,
    )

    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "assignee_id",
            "reviewer_id",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        return obj.comments.count() if hasattr(obj, "comments") else 0

    def validate(self, attrs):
        board = attrs.get("board", getattr(self.instance, "board", None))

        if board:
            board_users = set(board.members.values_list("id", flat=True))
            board_users.add(board.owner.id)

            assignee = attrs.get("assignee", getattr(self.instance, "assignee", None))
            if assignee and assignee.id not in board_users:
                raise serializers.ValidationError(
                    {"assignee_id": "Der Bearbeiter muss Mitglied des Boards sein."}
                )

            reviewer = attrs.get("reviewer", getattr(self.instance, "reviewer", None))
            if reviewer and reviewer.id not in board_users:
                raise serializers.ValidationError(
                    {"reviewer_id": "Der Reviewer muss Mitglied des Boards sein."}
                )

        return attrs


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    content = serializers.CharField(source="text")

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]

    def get_author(self, obj):
        full_name = f"{obj.author.first_name} {obj.author.last_name}".strip()
        return full_name if full_name else obj.author.username