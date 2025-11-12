from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Doctor Appointment - Patient Validation API")

# -----------------------------------------------------
# Pydantic Model
# -----------------------------------------------------
class PatientName(BaseModel):
    name: str


class NewPatient(BaseModel):
    name: str
    age: int
    email: str


# -----------------------------------------------------
# Predefined Registered Patients
# -----------------------------------------------------
registered_patients = {
    "John Doe": {
        "name": "John Doe",
        "age": 35,
        "email": "john.doe@example.com",
        "is_registered": True
    },
    "Johnny": {
        "name": "Johnny",
        "age": 29,
        "email": "johnny@example.com",
        "is_registered": True
    }
}


# -----------------------------------------------------
# 1️⃣ Validate Patient Name
# -----------------------------------------------------
@app.post("/validate-patient/")
def validate_patient(payload: PatientName):
    name = payload.name.strip()

    # Check if patient is registered
    if name in registered_patients:
        patient = registered_patients[name]
        return {
            "message": "Registered patient found!",
            "name": patient["name"],
            "age": patient["age"],
            "email": patient["email"],
            "is_registered": True
        }

    # Not registered → go to registration flow
    return {
        "message": "Patient not registered. Please register to continue.",
        "name": name,
        "age": None,
        "email": "",
        "is_registered": False
    }


