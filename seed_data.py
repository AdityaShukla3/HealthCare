import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from patients.models import Patient
from doctors.models import Doctor
from mappings.models import PatientDoctorMapping

User = get_user_model()


def seed():
    print("Seeding database...")

    # Create admin and test users
    admin_user, _ = User.objects.get_or_create(
        email="admin@healthcare.com",
        defaults={
            "name": "Hospital Administrator",
            "is_staff": True,
            "is_superuser": True
        }
    )
    admin_user.set_password("Admin@123456")
    admin_user.save()

    demo_user, _ = User.objects.get_or_create(
        email="doctor.staff@healthcare.com",
        defaults={
            "name": "Medical Staff Officer",
            "is_staff": True
        }
    )
    demo_user.is_staff = True
    demo_user.set_password("Staff@123456")
    demo_user.save()

    print(f"Users created: {admin_user.email}, {demo_user.email}")

    # Create Doctors
    doctors_data = [
        {
            "name": "Sarah Connor",
            "specialization": "Cardiology",
            "contact_number": "+1234567801",
            "email": "sarah.connor@hospital.org",
            "years_of_experience": 12,
            "hospital_affiliation": "Metropolitan Heart Institute"
        },
        {
            "name": "Alexander Fleming",
            "specialization": "Infectious Diseases",
            "contact_number": "+1234567802",
            "email": "alex.fleming@hospital.org",
            "years_of_experience": 18,
            "hospital_affiliation": "Central General Hospital"
        },
        {
            "name": "Lisa Cuddy",
            "specialization": "Endocrinology",
            "contact_number": "+1234567803",
            "email": "lisa.cuddy@hospital.org",
            "years_of_experience": 15,
            "hospital_affiliation": "Princeton-Plainsboro"
        },
    ]

    doctors = []
    for d in doctors_data:
        doc, _ = Doctor.objects.get_or_create(email=d["email"], defaults={**d, "created_by": demo_user})
        doc.created_by = demo_user
        doc.save()
        doctors.append(doc)
    print(f"Created {len(doctors)} doctors.")

    # Create Patients
    patients_data = [
        {
            "name": "Robert Downey",
            "date_of_birth": "1980-04-04",
            "gender": "Male",
            "contact_number": "+1987654301",
            "email": "robert.d@example.com",
            "address": "10880 Malibu Point, CA",
            "medical_history": "Mild hypertension, annual cardiac checkup recommended.",
            "created_by": demo_user
        },
        {
            "name": "Emma Watson",
            "date_of_birth": "1992-07-21",
            "gender": "Female",
            "contact_number": "+1987654302",
            "email": "emma.w@example.com",
            "address": "4 Privet Drive, Little Whinging",
            "medical_history": "No chronic conditions. Seasonal pollen allergy.",
            "created_by": demo_user
        }
    ]

    patients = []
    for p in patients_data:
        pat, _ = Patient.objects.get_or_create(
            name=p["name"],
            created_by=p["created_by"],
            defaults=p
        )
        patients.append(pat)
    print(f"Created {len(patients)} patients.")

    # Create Mappings
    if patients and doctors:
        mapping, created = PatientDoctorMapping.objects.get_or_create(
            patient=patients[0],
            doctor=doctors[0],
            defaults={"notes": "Assigned for annual cardiac review."}
        )
        print(f"Created mapping: {patients[0].name} <-> Dr. {doctors[0].name} (Created={created})")

    print("\nDatabase seeded successfully!")
    print("Demo User Credentials:")
    print("Email: doctor.staff@healthcare.com")
    print("Password: Staff@123456")
    print("\nAdmin User Credentials:")
    print("Email: admin@healthcare.com")
    print("Password: Admin@123456")


if __name__ == "__main__":
    seed()
