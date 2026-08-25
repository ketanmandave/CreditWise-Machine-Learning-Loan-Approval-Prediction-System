"""Training and inference utilities for the CreditWise classifier."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "loan_approval_data.csv"
ARTIFACT_DIR = ROOT / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "loan_model.joblib"
METADATA_PATH = ARTIFACT_DIR / "metadata.json"

RAW_FEATURES = [
    "Applicant_Income",
    "Coapplicant_Income",
    "Employment_Status",
    "Age",
    "Marital_Status",
    "Dependents",
    "Credit_Score",
    "Existing_Loans",
    "DTI_Ratio",
    "Savings",
    "Collateral_Value",
    "Loan_Amount",
    "Loan_Term",
    "Loan_Purpose",
    "Property_Area",
    "Education_Level",
    "Gender",
    "Employer_Category",
]

NUMERIC_FEATURES = [
    "Applicant_Income",
    "Coapplicant_Income",
    "Age",
    "Dependents",
    "Existing_Loans",
    "Savings",
    "Collateral_Value",
    "Loan_Amount",
    "Loan_Term",
    "Credit_Score_sq",
    "DTI_Ratio_sq",
]

CATEGORICAL_FEATURES = [
    "Employment_Status",
    "Marital_Status",
    "Loan_Purpose",
    "Property_Area",
    "Education_Level",
    "Gender",
    "Employer_Category",
]


class CreditFeatureEngineer(BaseEstimator, TransformerMixin):
    """Match the notebook's final squared-feature transformation."""

    def fit(self, X: pd.DataFrame, y: Any = None) -> "CreditFeatureEngineer":
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        frame = X.copy()
        frame["Credit_Score_sq"] = pd.to_numeric(
            frame["Credit_Score"], errors="coerce"
        ).pow(2)
        frame["DTI_Ratio_sq"] = pd.to_numeric(
            frame["DTI_Ratio"], errors="coerce"
        ).pow(2)
        return frame.drop(columns=["Credit_Score", "DTI_Ratio"])


def build_pipeline() -> Pipeline:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="mean")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "one_hot",
                OneHotEncoder(drop="first", handle_unknown="ignore"),
            ),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )
    return Pipeline(
        steps=[
            ("feature_engineering", CreditFeatureEngineer()),
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )


def train_and_save() -> tuple[Pipeline, dict[str, Any]]:
    data = pd.read_csv(DATA_PATH)
    labeled = data.dropna(subset=["Loan_Approved"]).copy()
    X = labeled[RAW_FEATURES]
    y = labeled["Loan_Approved"].map({"No": 0, "Yes": 1}).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    evaluation_model = build_pipeline()
    evaluation_model.fit(X_train, y_train)
    predictions = evaluation_model.predict(X_test)

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "precision": round(float(precision_score(y_test, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, predictions, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, predictions, zero_division=0)), 4),
        "training_rows": int(len(labeled)),
        "test_rows": int(len(y_test)),
        "model": "Logistic Regression",
        "threshold": 0.5,
    }

    final_model = build_pipeline()
    final_model.fit(X, y)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_model, MODEL_PATH)
    METADATA_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return final_model, metrics


def load_model() -> tuple[Pipeline, dict[str, Any]]:
    if not MODEL_PATH.exists() or not METADATA_PATH.exists():
        return train_and_save()
    model = joblib.load(MODEL_PATH)
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    return model, metadata

