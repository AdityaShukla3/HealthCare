from rest_framework import viewsets, permissions, filters
from .models import Doctor
from .serializers import DoctorSerializer
from .permissions import IsDoctorCreatorOrReadOnly


class DoctorViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Doctors.
    - POST /api/doctors/ : Add a new doctor (Authenticated users only)
    - GET /api/doctors/ : Retrieve all doctors
    - GET /api/doctors/<id>/ : Get details of a specific doctor
    - PUT /api/doctors/<id>/ : Update doctor details (Creator or staff only)
    - DELETE /api/doctors/<id>/ : Delete a doctor record (Creator or staff only)
    """
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctorCreatorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'specialization', 'email']
    ordering_fields = ['name', 'years_of_experience', 'created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
