from rest_framework import serializers
from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.email')

    class Meta:
        model = Doctor
        fields = (
            'id',
            'name',
            'specialization',
            'contact_number',
            'email',
            'years_of_experience',
            'hospital_affiliation',
            'created_by',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def validate_contact_number(self, value):
        cleaned = value.strip().replace(' ', '').replace('-', '')
        if not cleaned.replace('+', '').isdigit() or len(cleaned) < 7:
            raise serializers.ValidationError("Please provide a valid contact phone number.")
        return value

    def validate_years_of_experience(self, value):
        if value < 0 or value > 70:
            raise serializers.ValidationError("Years of experience must be between 0 and 70.")
        return value
