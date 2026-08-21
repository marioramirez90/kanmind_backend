from rest_framework import permissions


class IsTaskBoardMember(permissions.BasePermission):
    """Checks if the user is a member or owner of the task's board."""
    def has_object_permission(self, request, view, obj):
        board = obj.board
        is_member = board.members.filter(id=request.user.id).exists()
        is_owner = board.owner == request.user
        return is_member or is_owner


class IsTaskBoardOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.board.owner == request.user


class IsTaskCreatorOrBoardOwner(permissions.BasePermission):
    """Checks if the user is the task creator or the board owner."""
    def has_object_permission(self, request, view, obj):
        is_author = obj.author == request.user
        is_owner = obj.board.owner == request.user
        return is_author or is_owner


class IsCommentAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user