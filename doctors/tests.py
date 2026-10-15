from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Doctor

User = get_user_model()


class DoctorAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name='Test Admin',
            email='admin@example.com',
            password='Password123'
        )
        self.doctor_data = {
            'name': 'Gregory House',
            'specialization': 'Diagnostic Medicine',
            'contact_number': '+1987654321',
            'email': 'house@princetonplainsboro.org',
            'years_of_experience': 20,
            'hospital_affiliation': 'Princeton-Plainsboro Teaching Hospital',
        }
        self.doctor_list_url = reverse('doctor-list')

    def test_unauthenticated_access_denied(self):
        response = self.client.get(self.doctor_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_doctor_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.doctor_list_url, self.doctor_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Gregory House')

    def test_get_all_doctors(self):
        Doctor.objects.create(**self.doctor_data)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.doctor_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_and_delete_doctor(self):
        doctor = Doctor.objects.create(**self.doctor_data)
        self.client.force_authenticate(user=self.user)
        detail_url = reverse('doctor-detail', kwargs={'pk': doctor.id})

        # Update
        updated_payload = self.doctor_data.copy()
        updated_payload['years_of_experience'] = 21
        response = self.client.put(detail_url, updated_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['years_of_experience'], 21)

        # Delete
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Doctor.objects.filter(id=doctor.id).exists())
