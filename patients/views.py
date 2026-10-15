from rest_framework import viewsets, permissions
from .models import Patient
from .serializers import PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Patients.
    - POST /api/patients/ : Add a new patient (Authenticated users only)
    - GET /api/patients/ : Retrieve all patients created by the authenticated user
    - GET /api/patients/<id>/ : Get details of a specific patient
    - PUT /api/patients/<id>/ : Update patient details
    - DELETE /api/patients/<id>/ : Delete a patient record
    """
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
