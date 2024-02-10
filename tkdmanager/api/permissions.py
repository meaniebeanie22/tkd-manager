from rest_framework import permissions

class APIAllowed(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.groups.filter(name='APIAllowed').exists()
    