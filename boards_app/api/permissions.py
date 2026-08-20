from rest_framework import permissions


class IsBoardOwner(permissions.BasePermission):
    """Checks if the user is the owner of a board."""
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsBoardMemberOrOwner(permissions.BasePermission):
    """Checks if the user is a member or owner of a board."""
    def has_object_permission(self, request, view, obj):
        is_member = obj.members.filter(id=request.user.id).exists()
        is_owner = obj.owner == request.user
        return is_member or is_owner