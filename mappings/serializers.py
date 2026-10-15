from rest_framework import serializers
from .models import PatientDoctorMapping
from patients.models import Patient
from doctors.models import Doctor
from patients.serializers import PatientSerializer
from doctors.serializers import DoctorSerializer


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        source='doctor',
        write_only=True
    )

    # Read-only nested representation
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = (
            'id',
            'patient_id',
            'doctor_id',
            'patient',
            'doctor',
            'assigned_date',
            'notes',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'patient', 'doctor', 'assigned_date', 'created_at', 'updated_at')

    def validate(self, attrs):
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')

        # Check for existing mapping
        if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError(
                {"detail": f"Dr. {doctor.name} is already assigned to patient {patient.name}."}
            )

        return attrs
