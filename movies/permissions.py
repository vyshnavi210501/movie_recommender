from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Admins, Superadmins, Staff, and Superusers can create/update/delete
    - Normal users can only read (GET)
    """

    def has_permission(self, request, view):
        # Allow GET requests for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow if user is authenticated and either:
        # - superuser
        # - staff
        # - belongs to Admin or Superadmin group
        if request.user and request.user.is_authenticated:
            return (
                request.user.is_superuser
                or request.user.is_staff
                or request.user.groups.filter(name__in=["Admin", "Superadmin"]).exists()
            )

        return False
