from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import PatientDoctorMapping
from .serializers import PatientDoctorMappingSerializer
from patients.models import Patient
from doctors.models import Doctor
from doctors.serializers import DoctorSerializer


class MappingListCreateView(APIView):
    """
    - POST /api/mappings/ : Assign a doctor to a patient (User must own the patient)
    - GET /api/mappings/  : Retrieve patient-doctor mappings for patients created by the authenticated user
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        mappings = PatientDoctorMapping.objects.filter(
            patient__created_by=request.user
        ).select_related('patient', 'doctor')
        serializer = PatientDoctorMappingSerializer(mappings, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PatientDoctorMappingSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        mapping = serializer.save()
        return Response(
            PatientDoctorMappingSerializer(mapping, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class MappingDetailView(APIView):
    """
    - GET /api/mappings/<patient_id>/ : Get all doctors assigned to a specific patient owned by request.user
    - DELETE /api/mappings/<id>/      : Remove a doctor from a patient (delete mapping owned by request.user)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        # Treat pk strictly and deterministically as patient_id, scoped to authenticated user
        patient = Patient.objects.filter(id=pk, created_by=request.user).first()
        if patient is None:
            return Response(
                {"detail": f"Patient with ID {pk} not found or you do not have permission to view their assignments."},
                status=status.HTTP_404_NOT_FOUND
            )

        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('patient', 'doctor')
        # If client requests doctors only: ?format=doctors
        if request.query_params.get('format') == 'doctors':
            doctors = [m.doctor for m in mappings]
            return Response(DoctorSerializer(doctors, many=True).data, status=status.HTTP_200_OK)

        serializer = PatientDoctorMappingSerializer(mappings, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        # Treat pk strictly as mapping ID, scoped to patient owned by authenticated user
        mapping = PatientDoctorMapping.objects.filter(
            id=pk,
            patient__created_by=request.user
        ).first()

        if not mapping:
            return Response(
                {"detail": f"Mapping with ID {pk} not found or you do not have permission to remove it."},
                status=status.HTTP_404_NOT_FOUND
            )

        mapping.delete()
        return Response(
            {"message": "Doctor assignment removed successfully."},
            status=status.HTTP_200_OK
        )
