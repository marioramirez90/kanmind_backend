from rest_framework import permissions


class IsBoardOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsBoardMemberOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        is_member = obj.members.filter(id=request.user.id).exists()
        is_owner = obj.owner == request.user
        return is_member or is_owner