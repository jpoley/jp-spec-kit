# Mobile Frontend - Python Backend Stack

## Overview

Cross-platform mobile stack using React Native or native development, with Python backend for data-intensive features, ML integration, and rapid development.

## Use Cases

- **Ideal For:**
  - Data-driven mobile applications
  - Mobile apps with ML/AI features
  - Applications requiring data science capabilities
  - Rapid mobile development with Python expertise
  - Mobile dashboards and analytics apps
  - Apps with complex data processing
  - Prototypes and MVPs with mobile interfaces

- **Not Ideal For:**
  - Ultra-high performance mobile backends
  - Real-time gaming or trading apps
  - Apps requiring microsecond latency
  - Simple mobile apps without data processing needs

## Tech Stack Components

### Mobile Frontend
- **React Native:** See `mobile-frontend-go-backend.md` for React Native details
- **Native iOS:** Swift + SwiftUI
- **Native Android:** Kotlin + Jetpack Compose

### Backend (Python)
- **Framework:** FastAPI (recommended for async) or Django REST Framework
- **ORM:** SQLAlchemy or Django ORM
- **Database:** PostgreSQL, MongoDB
- **Cache:** Redis
- **Task Queue:** Celery
- **ML/AI:** scikit-learn, TensorFlow, PyTorch
- **Data Processing:** Pandas, NumPy
- **Authentication:** FastAPI-Users or Django-AllAuth
- **API Documentation:** OpenAPI/Swagger (FastAPI auto-generated)

### Infrastructure
- Similar to `react-frontend-python-backend.md`
- Push notifications: Firebase Cloud Messaging
- File storage: S3-compatible storage
- Monitoring: Sentry, Prometheus

## Architecture Patterns

Project structure combines mobile app structure from `mobile-frontend-go-backend.md` with Python backend structure from `react-frontend-python-backend.md`.

## Coding Standards

**Mobile Frontend:** Refer to `.languages/mobile/` and `.languages/ts-js/`
**Python Backend:** Refer to `.languages/python/principles.md`

## Selection Criteria

### Choose When:
- Mobile app needs ML/AI features
- Data science team with Python expertise
- Complex data processing on backend
- Rapid development with Python ecosystem
- Data visualization requirements
- Team familiar with Python but needs mobile presence

### Avoid When:
- Need ultra-high performance
- Simple mobile CRUD application
- Team lacks Python/mobile expertise
- Real-time gaming or high-frequency trading

## Best Practices

### ML Model Serving (Safe Methods)

```python
# app/services/ml_service.py
import joblib  # Safer than pickle for scikit-learn models
from pathlib import Path
import numpy as np
from pydantic import BaseModel
import tensorflow as tf


class PredictionInput(BaseModel):
    """Input schema for predictions."""
    features: list[float]


class PredictionOutput(BaseModel):
    """Output schema for predictions."""
    prediction: float
    confidence: float


class MLService:
    """
    ML model serving service.

    Uses safe model loading:
    - joblib for scikit-learn (safer than pickle)
    - Native TensorFlow loader
    - Native PyTorch loader
    """

    def __init__(self, model_path: str, model_type: str = "sklearn"):
        self.model_type = model_type
        self.model = self._load_model(model_path)

    def _load_model(self, path: str):
        """Load trained ML model using safe methods."""
        if self.model_type == "sklearn":
            # joblib is safer than pickle for sklearn models
            return joblib.load(path)
        elif self.model_type == "tensorflow":
            # Use TensorFlow's native loader
            return tf.keras.models.load_model(path)
        elif self.model_type == "pytorch":
            # Use PyTorch's native loader
            import torch
            model = torch.load(path, map_location='cpu')
            # Set model to inference mode (not evaluation of code!)
            model.train(False)  # Disable training mode
            return model
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    async def predict(self, input_data: PredictionInput) -> PredictionOutput:
        """Make prediction using loaded model."""
        features = np.array([input_data.features])

        if self.model_type == "sklearn":
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)
            confidence = float(np.max(probabilities))

        elif self.model_type == "tensorflow":
            predictions = self.model.predict(features)
            prediction = float(predictions[0][0])
            confidence = float(np.max(predictions))

        else:  # pytorch
            import torch
            # Inference mode - no gradient computation
            with torch.no_grad():
                tensor_input = torch.FloatTensor(features)
                output = self.model(tensor_input)
                prediction = float(output[0])
                confidence = float(torch.max(output))

        return PredictionOutput(
            prediction=float(prediction),
            confidence=float(confidence)
        )


# app/api/deps.py
from functools import lru_cache
from app.services.ml_service import MLService
from app.core.config import settings

@lru_cache()
def get_ml_service() -> MLService:
    """Get ML service singleton."""
    return MLService(
        model_path=settings.ML_MODEL_PATH,
        model_type=settings.ML_MODEL_TYPE
    )


# app/api/v1/ml.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.ml_service import MLService, PredictionInput, PredictionOutput
from app.api.deps import get_ml_service

router = APIRouter()

@router.post("/predict", response_model=PredictionOutput)
async def predict(
    input_data: PredictionInput,
    ml_service: MLService = Depends(get_ml_service),
):
    """
    Get ML prediction.

    Security note: Uses safe model loading methods:
    - joblib for sklearn (not pickle)
    - Native loaders for TensorFlow/PyTorch
    """
    try:
        return await ml_service.predict(input_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )
```

### Mobile ML Integration

```typescript
// services/ml-service.ts
import { apiClient } from './api-client';

export interface PredictionRequest {
  features: number[];
}

export interface PredictionResponse {
  prediction: number;
  confidence: number;
}

export class MLService {
  async getPrediction(features: number[]): Promise<PredictionResponse> {
    const response = await apiClient.post<PredictionResponse>(
      '/api/v1/ml/predict',
      { features }
    );
    return response.data;
  }
}

export const mlService = new MLService();
```

### React Native Component with ML

```typescript
// screens/PredictionScreen.tsx
import React, { useState } from 'react';
import { View, Text, Button, ActivityIndicator } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { mlService } from '@/services/ml-service';

export const PredictionScreen: React.FC = () => {
  const [features, setFeatures] = useState<number[]>([]);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['prediction', features],
    queryFn: () => mlService.getPrediction(features),
    enabled: features.length > 0,
  });

  if (isLoading) return <ActivityIndicator />;
  if (error) return <Text>Error: {error.message}</Text>;

  return (
    <View>
      {data && (
        <View>
          <Text>Prediction: {data.prediction}</Text>
          <Text>Confidence: {(data.confidence * 100).toFixed(1)}%</Text>
        </View>
      )}
      <Button title="Get Prediction" onPress={() => refetch()} />
    </View>
  );
};
```

### Data Processing API

```python
# app/api/v1/data.py
from fastapi import APIRouter, Depends, BackgroundTasks
from typing import List
import pandas as pd
from pydantic import BaseModel

router = APIRouter()


class DataPoint(BaseModel):
    """Single data point for analysis."""
    timestamp: str
    value: float
    category: str


class AnalysisResult(BaseModel):
    """Analysis result schema."""
    count: int
    mean: dict[str, float]
    std: dict[str, float]
    categories: list[str]


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_data(
    data: List[DataPoint],
    background_tasks: BackgroundTasks,
):
    """
    Analyze data using pandas.

    For large datasets, processing happens in background task.
    """
    # Convert to DataFrame
    df = pd.DataFrame([d.dict() for d in data])

    # Quick synchronous analysis for small datasets
    if len(df) < 1000:
        numeric_cols = df.select_dtypes(include='number')

        return AnalysisResult(
            count=len(df),
            mean=numeric_cols.mean().to_dict(),
            std=numeric_cols.std().to_dict(),
            categories=df['category'].unique().tolist()
        )

    # Background processing for larger datasets
    background_tasks.add_task(process_large_dataset, df)

    return AnalysisResult(
        count=len(df),
        mean={},
        std={},
        categories=[],
    )


async def process_large_dataset(df: pd.DataFrame):
    """Process large dataset in background."""
    # Heavy computation here
    pass
```

## Testing ML Endpoints

```python
# tests/test_ml.py
import pytest
from httpx import AsyncClient
import numpy as np

@pytest.mark.asyncio
async def test_ml_prediction(client: AsyncClient):
    """Test ML prediction endpoint."""
    response = await client.post(
        "/api/v1/ml/predict",
        json={"features": [1.0, 2.0, 3.0, 4.0]}
    )

    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
    assert 0 <= data["confidence"] <= 1
```

## Learning Resources

- FastAPI + ML: https://fastapi.tiangolo.com/advanced/
- Joblib (safe model persistence): https://joblib.readthedocs.io/
- TensorFlow Serving: https://www.tensorflow.org/tfx/guide/serving
- Refer to `mobile-frontend-go-backend.md` for mobile details
- Refer to `react-frontend-python-backend.md` for Python backend details
- Refer to `.languages/python/` and `.languages/mobile/`

## Security Considerations

- **Model Loading:** Use joblib for sklearn, native loaders for TF/PyTorch
- **Input Validation:** Validate all ML inputs with Pydantic
- **Rate Limiting:** Protect ML endpoints from abuse (CPU-intensive)
- **Model Versioning:** Track model versions for reproducibility
- **API Security:** Same as react-frontend-python-backend.md
- **Mobile Security:** Same as mobile-frontend-go-backend.md

## Performance Optimization

- Cache ML predictions for identical inputs
- Use async endpoints for non-blocking I/O
- Consider model quantization for faster inference
- Use GPU acceleration for heavy models (TensorFlow/PyTorch)
- Batch predictions when possible
- Monitor memory usage with large models

## Success Metrics

- Prediction latency <500ms (p95)
- Model accuracy >90% (depends on use case)
- API response time <200ms (non-ML endpoints)
- Crash-free rate >99.5%
- Backend uptime >99.9%
