# Data / ML Pipeline - Python Stack

## Overview

Python-focused stack for building data processing pipelines, ML training workflows, ETL processes, and data science applications.

## Use Cases

- **Ideal For:**
  - ETL (Extract, Transform, Load) pipelines
  - ML model training and evaluation workflows
  - Data warehousing and analytics
  - Batch data processing
  - Real-time streaming analytics
  - Data lake processing
  - Feature engineering pipelines
  - Model serving and monitoring
  - Automated reporting and dashboards

- **Not Ideal For:**
  - User-facing web applications (use full-stack options)
  - Real-time applications requiring microsecond latency
  - Systems programming
  - Mobile applications

## Tech Stack Components

### Core Python Stack
- **Language:** Python 3.11+
- **Data Processing:** Pandas, Polars, Dask (for large datasets)
- **ML/AI:** scikit-learn, XGBoost, TensorFlow, PyTorch
- **Data Validation:** Great Expectations, Pydantic
- **Testing:** pytest, pytest-cov
- **Type Checking:** mypy
- **Linting:** ruff, black, isort

### Workflow Orchestration
- **Apache Airflow:** Complex DAG-based workflows
- **Prefect:** Modern Python-native orchestration
- **Dagster:** Data-aware orchestration
- **Kedro:** ML pipelines with software engineering best practices
- **Metaflow:** ML/DS workflows (Netflix)

### Data Storage
- **Data Warehouse:** Snowflake, BigQuery, Redshift
- **Data Lake:** S3, Azure Data Lake, GCS
- **Databases:** PostgreSQL, MongoDB
- **Feature Store:** Feast, Tecton
- **Vector DB:** Pinecone, Weaviate, Chroma (for ML)

### Message Queue & Streaming
- **Kafka:** Real-time data streaming (with confluent-kafka-python)
- **Redis Streams:** Lightweight streaming
- **RabbitMQ:** Message queuing
- **AWS Kinesis / GCP Pub/Sub:** Cloud-native streaming

### ML Tools
- **Experiment Tracking:** MLflow, Weights & Biases, Neptune
- **Model Registry:** MLflow Model Registry
- **Hyperparameter Tuning:** Optuna, Ray Tune
- **AutoML:** Auto-sklearn, TPOT
- **Model Serving:** FastAPI, BentoML, Seldon Core

### Infrastructure
- **Containerization:** Docker
- **Orchestration:** Kubernetes, AWS ECS
- **Compute:** EC2, Lambda, GCP Compute Engine
- **Notebooks:** JupyterLab, Databricks
- **Monitoring:** Prometheus, Grafana, Datadog

## Architecture Patterns

### Project Structure

```
data-pipeline/
├── dags/                       # Airflow DAGs or workflow definitions
│   ├── __init__.py
│   ├── etl_daily.py
│   └── ml_training.py
│
├── pipelines/                  # Pipeline logic
│   ├── __init__.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── sources.py          # Data source connectors
│   │   └── extractors.py       # Data extraction logic
│   │
│   ├── transformation/
│   │   ├── __init__.py
│   │   ├── cleaners.py         # Data cleaning
│   │   ├── validators.py       # Data validation
│   │   └── features.py         # Feature engineering
│   │
│   └── loading/
│       ├── __init__.py
│       └── loaders.py          # Data loading to destinations
│
├── models/                     # ML models
│   ├── __init__.py
│   ├── training/
│   │   ├── __init__.py
│   │   ├── train.py            # Training scripts
│   │   └── evaluate.py         # Evaluation scripts
│   │
│   ├── inference/
│   │   ├── __init__.py
│   │   └── predict.py          # Inference logic
│   │
│   └── registry/
│       └── models/             # Trained model artifacts
│
├── data/                       # Data (gitignored)
│   ├── raw/                    # Raw input data
│   ├── processed/              # Processed data
│   └── features/               # Feature datasets
│
├── notebooks/                  # Jupyter notebooks for exploration
│   ├── exploration/
│   └── experiments/
│
├── tests/                      # Tests
│   ├── __init__.py
│   ├── test_pipelines/
│   ├── test_models/
│   └── test_utils/
│
├── config/                     # Configuration files
│   ├── __init__.py
│   ├── settings.py
│   └── environments/
│       ├── dev.yaml
│       ├── staging.yaml
│       └── prod.yaml
│
├── scripts/                    # Utility scripts
│   ├── setup_environment.sh
│   └── run_pipeline.py
│
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
│
├── pyproject.toml
├── setup.py
├── Dockerfile
└── README.md
```

### Key Architectural Decisions

1. **Modular Pipeline Design**
   - Separate extract, transform, load logic
   - Reusable components
   - Testable units
   - Clear data contracts

2. **Data Quality Gates**
   - Validation at each step
   - Schema enforcement
   - Data quality metrics
   - Alerting on anomalies

3. **Reproducibility**
   - Version control for code and data
   - Environment management (Poetry/conda)
   - Experiment tracking
   - Model versioning

4. **Scalability**
   - Distributed processing (Dask/Spark)
   - Batch processing for large datasets
   - Streaming for real-time needs
   - Resource optimization

## Coding Standards

**Python Standards:** Refer to `.languages/python/principles.md`

### Data Pipeline Example

```python
# pipelines/transformation/features.py
from typing import Protocol
import pandas as pd
import numpy as np
from pydantic import BaseModel, validator


class FeatureConfig(BaseModel):
    """Configuration for feature engineering."""
    numerical_features: list[str]
    categorical_features: list[str]
    target_column: str

    @validator('numerical_features', 'categorical_features')
    def validate_feature_lists(cls, v):
        if not v:
            raise ValueError("Feature list cannot be empty")
        return v


class FeatureTransformer(Protocol):
    """Protocol for feature transformers."""
    def fit(self, df: pd.DataFrame) -> 'FeatureTransformer':
        ...

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        ...


class DataFeatureEngineer:
    """Feature engineering for ML models."""

    def __init__(self, config: FeatureConfig):
        self.config = config
        self.fitted = False

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features from raw data.

        Args:
            df: Input dataframe

        Returns:
            DataFrame with engineered features
        """
        df = df.copy()

        # Numerical features
        df = self._engineer_numerical_features(df)

        # Categorical features
        df = self._engineer_categorical_features(df)

        # Interaction features
        df = self._create_interactions(df)

        return df

    def _engineer_numerical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer numerical features."""
        for col in self.config.numerical_features:
            # Log transform for skewed features
            df[f'{col}_log'] = np.log1p(df[col].clip(lower=0))

            # Square root transform
            df[f'{col}_sqrt'] = np.sqrt(df[col].clip(lower=0))

            # Binning
            df[f'{col}_bin'] = pd.qcut(
                df[col],
                q=5,
                labels=False,
                duplicates='drop'
            )

        return df

    def _engineer_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer categorical features."""
        for col in self.config.categorical_features:
            # Frequency encoding
            freq = df[col].value_counts(normalize=True)
            df[f'{col}_freq'] = df[col].map(freq)

            # One-hot encoding for low cardinality
            if df[col].nunique() < 10:
                dummies = pd.get_dummies(df[col], prefix=col)
                df = pd.concat([df, dummies], axis=1)

        return df

    def _create_interactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create interaction features."""
        numerical = self.config.numerical_features

        # Create ratios and products for pairs of numerical features
        for i in range(len(numerical)):
            for j in range(i + 1, len(numerical)):
                col1, col2 = numerical[i], numerical[j]

                # Ratio
                df[f'{col1}_div_{col2}'] = df[col1] / (df[col2] + 1e-5)

                # Product
                df[f'{col1}_mul_{col2}'] = df[col1] * df[col2]

        return df
```

### ML Training Pipeline

```python
# models/training/train.py
from dataclasses import dataclass
from pathlib import Path
import joblib
import mlflow
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, roc_auc_score


@dataclass
class TrainingConfig:
    """Configuration for model training."""
    model_type: str
    hyperparameters: dict
    test_size: float = 0.2
    random_state: int = 42
    cv_folds: int = 5


class ModelTrainer:
    """Train and evaluate ML models."""

    def __init__(self, config: TrainingConfig):
        self.config = config
        self.model = None
        self.metrics = {}

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        experiment_name: str = "default"
    ) -> None:
        """
        Train model with MLflow tracking.

        Args:
            X: Feature matrix
            y: Target variable
            experiment_name: MLflow experiment name
        """
        # Set up MLflow
        mlflow.set_experiment(experiment_name)

        with mlflow.start_run():
            # Log parameters
            mlflow.log_params(self.config.hyperparameters)
            mlflow.log_param("model_type", self.config.model_type)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=self.config.test_size,
                random_state=self.config.random_state,
                stratify=y
            )

            # Initialize model
            self.model = self._get_model()

            # Cross-validation
            cv_scores = cross_val_score(
                self.model,
                X_train,
                y_train,
                cv=self.config.cv_folds,
                scoring='roc_auc'
            )

            print(f"CV ROC-AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
            mlflow.log_metric("cv_roc_auc_mean", cv_scores.mean())
            mlflow.log_metric("cv_roc_auc_std", cv_scores.std())

            # Train final model
            self.model.fit(X_train, y_train)

            # Evaluate
            y_pred = self.model.predict(X_test)
            y_pred_proba = self.model.predict_proba(X_test)[:, 1]

            # Calculate metrics
            roc_auc = roc_auc_score(y_test, y_pred_proba)
            self.metrics = {
                "roc_auc": roc_auc,
                "test_size": len(X_test),
            }

            # Log metrics
            mlflow.log_metrics(self.metrics)

            # Log classification report
            report = classification_report(y_test, y_pred)
            print(report)
            mlflow.log_text(report, "classification_report.txt")

            # Log model
            mlflow.sklearn.log_model(
                self.model,
                "model",
                registered_model_name=f"{self.config.model_type}_model"
            )

            print(f"Model logged with ROC-AUC: {roc_auc:.4f}")

    def _get_model(self):
        """Initialize model based on configuration."""
        if self.config.model_type == "random_forest":
            return RandomForestClassifier(**self.config.hyperparameters)
        else:
            raise ValueError(f"Unknown model type: {self.config.model_type}")

    def save(self, path: Path) -> None:
        """Save model to disk."""
        if self.model is None:
            raise ValueError("Model not trained yet")

        joblib.dump(self.model, path)
        print(f"Model saved to {path}")
```

### Airflow DAG Example

```python
# dags/ml_training.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd


default_args = {
    'owner': 'data-science',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}


def extract_data(**context):
    """Extract data from source."""
    hook = PostgresHook(postgres_conn_id='production_db')
    sql = """
        SELECT * FROM users
        WHERE created_at >= %(start_date)s
        AND created_at < %(end_date)s
    """

    execution_date = context['execution_date']
    start_date = execution_date
    end_date = execution_date + timedelta(days=1)

    df = hook.get_pandas_df(
        sql,
        parameters={'start_date': start_date, 'end_date': end_date}
    )

    # Save to temporary location
    df.to_parquet('/tmp/extracted_data.parquet')
    return len(df)


def transform_data(**context):
    """Transform and engineer features."""
    from pipelines.transformation.features import DataFeatureEngineer, FeatureConfig

    # Load data
    df = pd.read_parquet('/tmp/extracted_data.parquet')

    # Configure feature engineering
    config = FeatureConfig(
        numerical_features=['age', 'income', 'tenure'],
        categorical_features=['country', 'subscription_type'],
        target_column='churned'
    )

    # Engineer features
    engineer = DataFeatureEngineer(config)
    df_features = engineer.create_features(df)

    # Save transformed data
    df_features.to_parquet('/tmp/transformed_data.parquet')
    return len(df_features)


def train_model(**context):
    """Train ML model."""
    from models.training.train import ModelTrainer, TrainingConfig

    # Load data
    df = pd.read_parquet('/tmp/transformed_data.parquet')

    X = df.drop('churned', axis=1)
    y = df['churned']

    # Configure training
    config = TrainingConfig(
        model_type='random_forest',
        hyperparameters={
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
        }
    )

    # Train model
    trainer = ModelTrainer(config)
    trainer.train(X, y, experiment_name='churn_prediction')

    return trainer.metrics['roc_auc']


with DAG(
    'ml_training_pipeline',
    default_args=default_args,
    description='Daily ML model training pipeline',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['ml', 'training'],
) as dag:

    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
        provide_context=True,
    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
        provide_context=True,
    )

    train_task = PythonOperator(
        task_id='train_model',
        python_callable=train_model,
        provide_context=True,
    )

    extract_task >> transform_task >> train_task
```

## Selection Criteria

### Choose This Stack When:
- Building data pipelines and ETL processes
- ML model training and evaluation workflows
- Data science research and experimentation
- Batch data processing requirements
- Team has strong Python/data science skills
- Need rich data science ecosystem

### Avoid This Stack When:
- Building user-facing web or mobile applications
- Need real-time interactive applications
- Systems programming or low-level control required
- Team lacks Python expertise

## Best Practices

1. **Data Quality**: Validate at every step
2. **Reproducibility**: Version everything (code, data, models, environment)
3. **Modularity**: Small, testable, reusable components
4. **Documentation**: Document data schemas, transformations, assumptions
5. **Monitoring**: Track pipeline health, data quality, model performance
6. **Testing**: Unit tests for transformations, integration tests for pipelines
7. **Error Handling**: Graceful failures, retries, alerting
8. **Performance**: Profile and optimize bottlenecks, use appropriate tools (Dask for large data)

## Testing Strategy

```python
# tests/test_pipelines/test_features.py
import pytest
import pandas as pd
from pipelines.transformation.features import DataFeatureEngineer, FeatureConfig


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame({
        'age': [25, 35, 45, 55],
        'income': [30000, 50000, 70000, 90000],
        'country': ['US', 'UK', 'US', 'CA'],
        'churned': [0, 0, 1, 1]
    })


@pytest.fixture
def config():
    """Create test configuration."""
    return FeatureConfig(
        numerical_features=['age', 'income'],
        categorical_features=['country'],
        target_column='churned'
    )


def test_feature_engineering(sample_data, config):
    """Test feature engineering process."""
    engineer = DataFeatureEngineer(config)
    result = engineer.create_features(sample_data)

    # Check new features were created
    assert 'age_log' in result.columns
    assert 'income_sqrt' in result.columns
    assert 'country_freq' in result.columns

    # Check no missing values introduced
    assert not result.isnull().any().any()

    # Check shape
    assert len(result) == len(sample_data)
```

## Deployment

```dockerfile
# Dockerfile for Airflow worker
FROM apache/airflow:2.7.0-python3.11

USER root
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

USER airflow
COPY requirements/prod.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY dags /opt/airflow/dags
COPY pipelines /opt/airflow/pipelines
COPY models /opt/airflow/models
```

## Learning Resources

- Apache Airflow: https://airflow.apache.org/
- MLflow: https://mlflow.org/
- Pandas: https://pandas.pydata.org/
- scikit-learn: https://scikit-learn.org/
- Refer to `.languages/python/principles.md`

## Success Metrics

- Pipeline success rate >99%
- Data quality score >95%
- Model performance meets business requirements
- Pipeline execution time within SLA
- Zero data loss incidents
- Clear audit trail for compliance
