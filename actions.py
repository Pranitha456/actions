from fastapi import FastAPI, Request
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
# 1️⃣ Validate Patient (no 422 even for wrong/empty input)
# ----------------------------------------------------
@app.post("/validate-patient/")
async def validate_patient(request: Request):
    try:
        data = await request.json()
        name = data.get("name", "").strip()
        age = data.get("age", None)
        email = data.get("email", "").strip()

        # Handle empty or missing inputs
        if not name or not age or not email:
            return {
                "status": "error",
                "message": "Patient not found. Please register first."
            }

        # Simple email validation
        if "@" not in email or "." not in email:
            return {
                "status": "error",
                "message": "Patient not found. Please register first."
            }

        # Check patient exists
        for patient in patients:
            if (
                patient["name"].lower() == name.lower()
                and patient["age"] == age
                and patient["email"].lower() == email.lower()
            ):
                return {
                    "status": "success",
                    "message": f"Patient {name} validated successfully ✅"
                }

        return {
            "status": "error",
            "message": "Patient not found. Please register first."
        }

    except Exception:
        return {
            "status": "error",
            "message": "Patient not found. Please register first."
        }


# ----------------------------------------------------
# 2️⃣ Register Patient (no 422 even for missing input)
# ----------------------------------------------------
@app.post("/register-patient/")
async def register_patient(request: Request):
    try:
        data = await request.json()
        name = data.get("name", "").strip()
        age = data.get("age", None)
        email = data.get("email", "").strip()

        if not name or not age or not email:
            return {
                "status": "error",
                "message": "Invalid or missing patient details."
            }

        if "@" not in email or "." not in email:
            return {
                "status": "error",
                "message": "Invalid email format."
            }

        # Check duplicate
        for patient in patients:
            if (
                patient["name"].lower() == name.lower()
                and patient["email"].lower() == email.lower()
            ):
                return {
                    "status": "error",
                    "message": "Patient already registered."
                }

        patients.append({
            "name": name,
            "age": age,
            "email": email
        })

        return {
            "status": "success",
            "message": f"Patient {name} registered successfully ✅"
        }

    except Exception:
        return {
            "status": "error",
            "message": "Invalid request format."
        }


# ----------------------------------------------------
# 3️⃣ Get Available Slots
# ----------------------------------------------------
@app.post("/get-available-slots/")
async def get_slots(request: Request):
    try:
        data = await request.json()
        speciality = data.get("speciality", "").strip()
        doctor = data.get("doctor", "").strip()

        if not speciality or not doctor:
            return {"status": "error", "message": "Missing speciality or doctor name."}

        if speciality not in specialities:
            return {"status": "error", "message": "Invalid speciality."}

        if doctor not in specialities[speciality]:
            return {"status": "error", "message": "Doctor not available in this speciality."}

        today = datetime.now()
        slots = []

        for _ in range(3):  # generate 3 random slots
            days_ahead = random.randint(1, 10)
            hour = random.choice([9, 10, 11, 14, 15, 16, 17, 18, 19])
            minute = random.choice(["00", "30"])
            slot_datetime = (today + timedelta(days=days_ahead)).strftime(f"%Y-%m-%d {hour}:{minute}")
            slots.append(slot_datetime)

        return {
            "status": "success",
            "doctor": doctor,
            "speciality": speciality,
            "available_dates": ", ".join(slots)
        }

    except Exception:
        return {"status": "error", "message": "Invalid request format."}


# ----------------------------------------------------
# 4️⃣ Confirm Appointment & Prevent Duplicate
# ----------------------------------------------------
@app.post("/confirm-appointment/")
async def confirm_appointment(request: Request):
    try:
        data = await request.json()
        name = data.get("name", "").strip()
        doctor = data.get("doctor", "").strip()
        date = data.get("date", "").strip()
        time = data.get("time", "").strip()
        amount = data.get("amount", 0.0)

        # Validate input
        if not name or not doctor or not date or not time or not amount:
            return {"status": "error", "message": "Missing appointment details."}

        if amount <= 0:
            return {"status": "error", "message": "Invalid payment amount."}

        # Check duplicate booking
        for booking in booked_appointments:
            if (
                booking["name"].lower() == name.lower()
                and booking["doctor"].lower() == doctor.lower()
                and booking["date"] == date
                and booking["time"] == time
            ):
                return {
                    "status": "error",
                    "message": "This slot is already booked for the same patient and doctor ❌"
                }

        confirmation_id = f"APT-{random.randint(10000, 99999)}"
        payment_id = f"PAY-{random.randint(10000, 99999)}"

        appointment = {
            "appointment_id": confirmation_id,
            "name": name,
            "doctor": doctor,
            "date": date,
            "time": time,
            "amount": amount,
            "payment_id": payment_id,
            "confirmation_status": "confirmed"
        }

        booked_appointments.append(appointment)

        return {
            "status": "success",
            "appointment_confirmation_message": "Appointment and payment confirmed successfully ✅",
            **appointment
        }

    except Exception:
        return {"status": "error", "message": "Invalid request format."}
