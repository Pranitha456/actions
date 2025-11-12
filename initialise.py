from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os

app = FastAPI(title="Doctor Appointment - Patient Validation & Registration API")

PATIENTS_FILE = "patients.json"

# -----------------------------------------------------
# Helper Functions
# -----------------------------------------------------
def save_patients(data):
    """Save patient data to JSON file"""
    with open(PATIENTS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_patients():
    """Load patient data, create default if not found"""
    if not os.path.exists(PATIENTS_FILE):
        data = {
            "patients": [
                {
                    "name": "John Doe",
                    "age": 35,
                    "email": "john.doe@example.com",
                    "is_registered": True
                },
                {
                    "name": "Johnny",
                    "age": 29,
                    "email": "johnny@example.com",
                    "is_registered": True
                }
            ]
        }
        save_patients(data)
        return data

    with open(PATIENTS_FILE, "r") as f:
        return json.load(f)


# Initialize patient data
patients_data = load_patients()

# -----------------------------------------------------
# Pydantic Models
# -----------------------------------------------------
class PatientName(BaseModel):
    name: str


class NewPatient(BaseModel):
    name: str
    age: int
    email: str


# -----------------------------------------------------
# 1️⃣ Validate Patient Name
# -----------------------------------------------------
@app.post("/validate-patient/")
def validate_patient(payload: PatientName):
    name = payload.name.strip()
    for patient in patients_data["patients"]:
        if patient["name"].lower() == name.lower():
            return {
                "message": "Registered patient found!",
                "name": patient["name"],
                "age": patient["age"],
                "email": patient["email"],
                "is_registered": True
            }

    # If not found → new patient flow
    return {
        "message": "Patient not registered. Please register to continue.",
        "name": name,
        "age": None,
        "email": "",
        "is_registered": False
    }


# -----------------------------------------------------
# 2️⃣ Register New Patient
# -----------------------------------------------------
@app.post("/register-patient/")
def register_patient(new_patient: NewPatient):
    global patients_data
    patients_data = load_patients()  # Reload latest data

    # Check if patient already exists
    for patient in patients_data["patients"]:
        if patient["name"].lower() == new_patient.name.lower():
            raise HTTPException(status_code=400, detail="Patient already registered with this name.")

    # Add new patient
    new_entry = {
        "name": new_patient.name,
        "age": new_patient.age,
        "email": new_patient.email,
        "is_registered": True
    }
    patients_data["patients"].append(new_entry)
    save_patients(patients_data)

    return {
        "message": "Patient successfully registered!",
        "name": new_patient.name,
        "age": new_patient.age,
        "email": new_patient.email,
        "is_registered": True
    }
