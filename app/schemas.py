"""Request and response contracts for the prediction API."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LoanApplication(BaseModel):
    model_config = ConfigDict(extra="forbid")

    Applicant_Income: float = Field(gt=0, le=10_000_000)
    Coapplicant_Income: float = Field(ge=0, le=10_000_000)
    Employment_Status: Literal["Contract", "Salaried", "Self-employed", "Unemployed"]
    Age: int = Field(ge=18, le=100)
    Marital_Status: Literal["Married", "Single"]
    Dependents: int = Field(ge=0, le=20)
    Credit_Score: int = Field(ge=300, le=900)
    Existing_Loans: int = Field(ge=0, le=50)
    DTI_Ratio: float = Field(ge=0, le=1)
    Savings: float = Field(ge=0, le=100_000_000)
    Collateral_Value: float = Field(ge=0, le=100_000_000)
    Loan_Amount: float = Field(gt=0, le=100_000_000)
    Loan_Term: int = Field(ge=1, le=480)
    Loan_Purpose: Literal["Business", "Car", "Education", "Home", "Personal"]
    Property_Area: Literal["Rural", "Semiurban", "Urban"]
    Education_Level: Literal["Graduate", "Not Graduate"]
    Gender: Literal["Female", "Male"]
    Employer_Category: Literal["Business", "Government", "MNC", "Private", "Unemployed"]


class PredictionResponse(BaseModel):
    approved: bool
    decision: Literal["Approved", "Not Approved"]
    approval_probability: float
    confidence: float
    model: str
    disclaimer: str

