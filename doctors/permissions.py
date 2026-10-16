from rest_framework import permissions


class IsDoctorCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission for Doctors:
    - Any authenticated user can read doctors (GET, HEAD, OPTIONS) as per
      the assignment requirement ("GET /api/doctors/ - Retrieve all doctors").
    - Only the user who created the doctor (or staff/superuser) can update or delete it.
    - If created_by is None (e.g. system seed data), any authenticated user can view,
      but only staff/superusers can modify or delete.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions (PUT, PATCH, DELETE) require ownership or staff/superuser
        if request.user and (request.user.is_staff or request.user.is_superuser):
            return True

        # If created_by is None, non-staff users cannot mutate system records
        if obj.created_by is None:
            return False

        return obj.created_by == request.user
