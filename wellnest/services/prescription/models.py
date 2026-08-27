from pydantic import BaseModel
from typing import List, Optional


# ==========================
# Medicine
# ==========================

class Medicine(BaseModel):
    original_name: Optional[str] = None
    normalized_name: Optional[str] = None
    generic_names: Optional[List[str]] = None
    strength: Optional[str] = None
    dosage_form: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    instruction: Optional[str] = None
    instruction_translation: Optional[str] = None


# ==========================
# Patient
# ==========================

class Patient(BaseModel):
    name: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None


# ==========================
# Doctor
# ==========================

class Doctor(BaseModel):
    name: Optional[str] = None

class Investigation(BaseModel):
    name: Optional[str] = None
    instruction: Optional[str] = None
    instruction_translation: Optional[str] = None

# ==========================
# General Instructions
# ==========================

class GeneralInstruction(BaseModel):
    instruction: str
    instruction_translation: Optional[str] = None


# ==========================
# Follow Up
# ==========================

class FollowUp(BaseModel):
    duration: Optional[str] = None
    duration_original: Optional[str] = None


# ==========================
# Prescription
# ==========================

class Prescription(BaseModel):
    patient: Patient
    doctor: Doctor
    hospital: Optional[str] = None
    date: Optional[str] = None

    diagnosis: Optional[List[str]] = None

    medicines: List[Medicine]

    investigations: Optional[List[Investigation]] = None

    general_instructions: Optional[List[GeneralInstruction]] = None

    follow_up: Optional[FollowUp] = None
