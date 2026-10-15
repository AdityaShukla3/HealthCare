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
    - POST /api/mappings/ : Assign a doctor to a patient
    - GET /api/mappings/  : Retrieve all patient-doctor mappings
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        mappings = PatientDoctorMapping.objects.select_related('patient', 'doctor').all()
        serializer = PatientDoctorMappingSerializer(mappings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PatientDoctorMappingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mapping = serializer.save()
        return Response(
            PatientDoctorMappingSerializer(mapping).data,
            status=status.HTTP_201_CREATED
        )


class MappingDetailView(APIView):
    """
    - GET /api/mappings/<patient_id>/ : Get all doctors assigned to a specific patient
    - DELETE /api/mappings/<id>/      : Remove a doctor from a patient (delete mapping)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        # Look for patient by ID
        patient = Patient.objects.filter(id=pk).first()
        if patient is not None:
            mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('patient', 'doctor')
            # If client requests doctors only: ?format=doctors
            if request.query_params.get('format') == 'doctors':
                doctors = [m.doctor for m in mappings]
                return Response(DoctorSerializer(doctors, many=True).data, status=status.HTTP_200_OK)

            serializer = PatientDoctorMappingSerializer(mappings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Fallback: check if pk is a mapping ID
        mapping = PatientDoctorMapping.objects.filter(id=pk).select_related('patient', 'doctor').first()
        if mapping is not None:
            serializer = PatientDoctorMappingSerializer(mapping)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"detail": f"No patient or mapping found with ID {pk}."},
            status=status.HTTP_404_NOT_FOUND
        )

    def delete(self, request, pk):
        mapping = PatientDoctorMapping.objects.filter(id=pk).first()
        if not mapping:
            return Response(
                {"detail": f"Mapping with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        mapping.delete()
        return Response(
            {"message": "Doctor assignment removed successfully."},
            status=status.HTTP_200_OK
        )
