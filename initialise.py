from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Initialize patients data (global)
patients = [
    {"name": "John Doe", "age": 30, "email": "john.doe@example.com"},
    {"name": "Jane Smith", "age": 27, "email": "jane.smith@example.com"}
]

# Pydantic model to validate incoming patient data
class Patient(BaseModel):
    name: str
    age: int
    email: str

# GET endpoint to list all patients
@app.get("/patients")
async def get_patients():
    return patients

# POST endpoint to add a new patient
@app.post("/patients")
async def add_patient(patient: Patient):
    patients.append(patient.dict())
    return {"message": "Patient added successfully", "total_patients": len(patients)}
