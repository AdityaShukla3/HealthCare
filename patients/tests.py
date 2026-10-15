from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Patient

User = get_user_model()


class PatientAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            name='User One',
            email='user1@example.com',
            password='Password123'
        )
        self.user2 = User.objects.create_user(
            name='User Two',
            email='user2@example.com',
            password='Password123'
        )

        self.patient_data = {
            'name': 'John Doe',
            'date_of_birth': '1990-05-15',
            'gender': 'Male',
            'contact_number': '+1234567890',
            'email': 'johndoe@example.com',
            'address': '123 Main St, Springfield',
            'medical_history': 'No known allergies',
        }

        self.patient_list_url = reverse('patient-list')

    def test_unauthenticated_access_denied(self):
        response = self.client.get(self.patient_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_patient_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.patient_list_url, self.patient_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'John Doe')
        self.assertEqual(response.data['created_by'], self.user1.id)

    def test_get_patients_scoped_to_creator(self):
        # Create one patient for user1, one for user2
        Patient.objects.create(created_by=self.user1, **self.patient_data)
        patient2_data = self.patient_data.copy()
        patient2_data['name'] = 'Jane Doe'
        Patient.objects.create(created_by=self.user2, **patient2_data)

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.patient_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see user1's patient
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'John Doe')

    def test_update_and_delete_patient(self):
        self.client.force_authenticate(user=self.user1)
        patient = Patient.objects.create(created_by=self.user1, **self.patient_data)
        detail_url = reverse('patient-detail', kwargs={'pk': patient.id})

        # Update
        update_data = self.patient_data.copy()
        update_data['name'] = 'Johnathan Doe'
        response = self.client.put(detail_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Johnathan Doe')

        # Delete
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.filter(id=patient.id).exists())
