from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from patients.models import Patient
from doctors.models import Doctor
from .models import PatientDoctorMapping

User = get_user_model()


class MappingAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name='Test Staff',
            email='staff@healthcare.com',
            password='Password123'
        )
        self.patient = Patient.objects.create(
            name='Alice Smith',
            date_of_birth='1995-03-20',
            gender='Female',
            contact_number='+1555123456',
            created_by=self.user
        )
        self.doctor = Doctor.objects.create(
            name='Stephen Strange',
            specialization='Neurosurgeon',
            contact_number='+1555654321',
            email='strange@marvel.com',
            years_of_experience=15
        )
        self.client.force_authenticate(user=self.user)
        self.mapping_list_url = reverse('mapping-list-create')

    def test_assign_doctor_to_patient(self):
        payload = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'notes': 'Neurological consultation needed.'
        }
        response = self.client.post(self.mapping_list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['patient']['id'], self.patient.id)
        self.assertEqual(response.data['doctor']['id'], self.doctor.id)
        self.assertTrue(PatientDoctorMapping.objects.filter(patient=self.patient, doctor=self.doctor).exists())

    def test_duplicate_assignment_fails(self):
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor)
        payload = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
        }
        response = self.client.post(self.mapping_list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_mappings(self):
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor)
        response = self.client.get(self.mapping_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_doctors_assigned_to_specific_patient(self):
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor)
        url = reverse('mapping-detail-delete', kwargs={'pk': self.patient.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['doctor']['id'], self.doctor.id)

    def test_remove_doctor_from_patient(self):
        mapping = PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor)
        delete_url = reverse('mapping-detail-delete', kwargs={'pk': mapping.id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(PatientDoctorMapping.objects.filter(id=mapping.id).exists())

    def test_user_cannot_assign_doctor_to_another_users_patient(self):
        other_user = User.objects.create_user(
            name='Other Staff',
            email='other@healthcare.com',
            password='Password123'
        )
        self.client.force_authenticate(user=other_user)

        payload = {
            'patient_id': self.patient.id,  # Owned by self.user, NOT other_user
            'doctor_id': self.doctor.id,
        }
        response = self.client.post(self.mapping_list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('patient_id', response.data)
        self.assertFalse(PatientDoctorMapping.objects.filter(patient=self.patient, doctor=self.doctor).exists())

    def test_user_cannot_view_another_users_mappings(self):
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor)
        other_user = User.objects.create_user(
            name='Other Staff',
            email='other@healthcare.com',
            password='Password123'
        )
        self.client.force_authenticate(user=other_user)

        # GET /api/mappings/ must NOT return other user's mappings
        response = self.client.get(self.mapping_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_user_cannot_view_or_delete_another_users_mapping_by_id(self):
        mapping = PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor)
        other_user = User.objects.create_user(
            name='Other Staff',
            email='other@healthcare.com',
            password='Password123'
        )
        self.client.force_authenticate(user=other_user)

        # GET /api/mappings/<patient_id>/ returns 404 for another user's patient
        get_url = reverse('mapping-detail-delete', kwargs={'pk': self.patient.id})
        get_response = self.client.get(get_url)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

        # DELETE /api/mappings/<mapping_id>/ returns 404 for another user's mapping
        del_url = reverse('mapping-detail-delete', kwargs={'pk': mapping.id})
        del_response = self.client.delete(del_url)
        self.assertEqual(del_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(PatientDoctorMapping.objects.filter(id=mapping.id).exists())

    def test_get_mappings_by_id_is_strictly_patient_id(self):
        # Create mapping where mapping.id != patient.id
        mapping = PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor)
        # Query an ID that matches the mapping ID, but no patient exists with this ID
        non_existent_patient_id = 9999
        url = reverse('mapping-detail-delete', kwargs={'pk': non_existent_patient_id})
        response = self.client.get(url)
        # Must return 404 because GET strictly treats pk as patient_id
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
