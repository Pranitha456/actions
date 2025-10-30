from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import random

app = FastAPI(title="Clinic Appointment API", version="3.0.0")

# ----------------------------------------------------
# Mock Data Stores
# ----------------------------------------------------
specialities = {
    "Cardiology": ["Dr. Rajesh Kumar", "Dr. Meena Sharma"],
    "Dermatology": ["Dr. Priya Nair", "Dr. Amit Verma"],
    "Neurology": ["Dr. R. Srinivasan", "Dr. Kavitha Devi"],
}

patients = []  # store patient registrations
booked_appointments = []  # store confirmed bookings

# ----------------------------------------------------
# Models
# ----------------------------------------------------
class PatientInfo(BaseModel):
    name: str
    age: int
    email: EmailStr


class SlotRequest(BaseModel):
    speciality: str
    doctor: str


class AppointmentConfirm(BaseModel):
    name: str
    doctor: str
    date: str
    time: str
    amount: float


# ----------------------------------------------------
# 1️⃣ Validate Patient
# ----------------------------------------------------
@app.post("/validate-patient/")
def validate_patient(data: PatientInfo):
    for patient in patients:
        if (
            patient["name"].lower() == data.name.lower()
            and patient["age"] == data.age
            and patient["email"].lower() == data.email.lower()
        ):
            return {
                "status": "success",
                "message": f"Patient {data.name} validated successfully ✅"
            }

    return {
        "status": "error",
        "message": "Patient not found. Please register first."
    }


# ----------------------------------------------------
# 2️⃣ Register Patient
# ----------------------------------------------------
@app.post("/register-patient/")
def register_patient(data: PatientInfo):
    for patient in patients:
        if (
            patient["name"].lower() == data.name.lower()
            and patient["email"].lower() == data.email.lower()
        ):
            return {
                "status": "error",
                "message": "Patient already registered."
            }

    patients.append({
        "name": data.name,
        "age": data.age,
        "email": data.email
    })

    return {
        "status": "success",
        "message": f"Patient {data.name} registered successfully ✅"
    }

@app.post("/get-available-slots/")
def get_slots(data: SlotRequest):
    print("🔥 Using NEW slot format function!")  # <-- Debug confirmation

    if data.speciality not in specialities:
        return {"status": "error", "message": "Invalid speciality"}
    if data.doctor not in specialities[data.speciality]:
        return {"status": "error", "message": "Doctor not available in this speciality"}

    today = datetime.now()
    slots = []

    for _ in range(3):
        days_ahead = random.randint(1, 7)
        hour = random.choice([9, 10, 11, 14, 15, 16])
        slot_date = (today + timedelta(days=days_ahead)).strftime("%d/%m/%Y")
        slot_time = f"{hour}:00"
        slots.append(f"{slot_date} {slot_time}")

    formatted_slots = ", ".join(slots)

    return {
        "status": "success",
        "doctor": data.doctor,
        "speciality": data.speciality,
        "available_slots": formatted_slots
    }

# ----------------------------------------------------
# 4️⃣ Confirm Appointment & Prevent Duplicate
# ----------------------------------------------------
@app.post("/confirm-appointment/")
def confirm_appointment(data: AppointmentConfirm):
    for booking in booked_appointments:
        if (
            booking["name"].lower() == data.name.lower()
            and booking["doctor"].lower() == data.doctor.lower()
            and booking["date"] == data.date
            and booking["time"] == data.time
        ):
            return {
                "status": "error",
                "message": "This slot is already booked for the same patient and doctor ❌"
            }

    if data.amount <= 0:
        return {"status": "error", "message": "Invalid payment amount"}

    confirmation_id = f"APT-{random.randint(10000, 99999)}"
    payment_id = f"PAY-{random.randint(10000, 99999)}"

    appointment = {
        "appointment_id": confirmation_id,
        "name": data.name,
        "doctor": data.doctor,
        "date": data.date,
        "time": data.time,
        "amount": data.amount,
        "payment_id": payment_id,
        "status": "confirmed"
    }

    booked_appointments.append(appointment)

    return {
        "status": "success",
        "appointment_confirmation_message": "Appointment and payment confirmed successfully ✅",
        "appointment_confirmation": appointment
    }
