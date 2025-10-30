from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import random

app = FastAPI(title="Clinic Appointment API", version="3.1.0")

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


# ----------------------------------------------------
# 3️⃣ Get Available Slots (flat string with date-time pairs)
# ----------------------------------------------------
@app.post("/get-available-slots/")
def get_slots(data: SlotRequest):
    if data.speciality not in specialities:
        return {"status": "error", "message": "Invalid speciality"}
    if data.doctor not in specialities[data.speciality]:
        return {"status": "error", "message": "Doctor not available in this speciality"}

    today = datetime.now()
    slots = []

    for _ in range(3):  # generate 3 random slots
        days_ahead = random.randint(1, 10)  # random within 10 days
        hour = random.choice([9, 10, 11, 14, 15, 16, 17, 18, 19])
        minute = random.choice(["00", "30"])  # randomize 00 or 30 minutes
        slot_datetime = (today + timedelta(days=days_ahead)).strftime(f"%Y-%m-%d {hour}:{minute}")
        slots.append(slot_datetime)

    return {
        "status": "success",
        "doctor": data.doctor,
        "speciality": data.speciality,
        "available_dates": ", ".join(slots)
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
        "confirmation_status": "confirmed"
    }

    booked_appointments.append(appointment)

    # ✅ Flattened response (no nested JSON)
    return {
        "status": "success",
        "appointment_confirmation_message": "Appointment and payment confirmed successfully ✅",
        **appointment  # expands all key-value pairs directly into the main response
    }
