
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **macOS/Linux**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the application:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Open `http://127.0.0.1:8000` in a browser.

FastAPI's interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Opens the web interface |
| `GET` | `/api/health` | Checks the API and loaded model |
| `GET` | `/api/model-info` | Returns model metrics and metadata |
| `POST` | `/api/predict` | Validates an application and returns a prediction |

Example prediction request:

```json
{
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
  "Employer_Category": "Private"
}
```

## Running the tests

```bash
pytest tests -q
```

The tests cover the home page, the prediction response contract, invalid input handling, and recovery from an incompatible saved model.

## Deploying on Render

Create a Python web service connected to this repository and use the following settings:

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

The `.python-version` file pins Python 3.13.7. The scikit-learn version is also pinned because saved scikit-learn models are not guaranteed to work across different library versions.

## Limitations

- The model was trained on a small educational dataset.
- Predictions can reflect patterns or bias present in the training data.
- The current probability threshold is fixed at 0.5.
- The application does not perform identity, document, fraud, or regulatory checks.
- The result must not be used to approve or reject a real loan.

## Future improvements

- Compare additional classification algorithms using cross-validation.
- Add explainability so users can understand which factors influenced a result.
- Store prediction history in a database.
- Add authentication and an administrative dashboard.
- Add monitoring for model performance and data drift.

## Author

**Ketan Mandave**

This project was created as part of my supervised machine learning practice and to learn how to deploy an end-to-end ML application.
Live Link: https://creditwise-machine-learning-loan.onrender.com
