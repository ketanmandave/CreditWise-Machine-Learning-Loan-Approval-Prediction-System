from fastapi.testclient import TestClient

from app.main import app


SAMPLE_APPLICATION = {
    "Applicant_Income": 65000,
    "Coapplicant_Income": 12000,
    "Employment_Status": "Salaried",
    "Age": 34,
    "Marital_Status": "Married",
    "Dependents": 1,
    "Credit_Score": 745,
    "Existing_Loans": 1,
    "DTI_Ratio": 0.28,
    "Savings": 25000,
    "Collateral_Value": 50000,
    "Loan_Amount": 30000,
    "Loan_Term": 60,
    "Loan_Purpose": "Home",
    "Property_Area": "Urban",
    "Education_Level": "Graduate",
    "Gender": "Female",
    "Employer_Category": "Private",
}


def test_home_page_loads():
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert "CreditWise" in response.text


def test_prediction_contract():
    with TestClient(app) as client:
        response = client.post("/api/predict", json=SAMPLE_APPLICATION)
    assert response.status_code == 200
    payload = response.json()
    assert payload["decision"] in {"Approved", "Not Approved"}
    assert 0 <= payload["approval_probability"] <= 1


def test_invalid_credit_score_is_rejected():
    invalid = {**SAMPLE_APPLICATION, "Credit_Score": 1200}
    with TestClient(app) as client:
        response = client.post("/api/predict", json=invalid)
    assert response.status_code == 422

