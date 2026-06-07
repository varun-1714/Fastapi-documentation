# Part 20: AI & Machine Learning

---

## Chapter 1: Serving ML Models Asynchronously (Stock Prediction API)

### 1. Introduction
Deploying machine learning (ML) models into production requires exposing them via fast, stable web interfaces. Because running inference (making predictions) is CPU-bound, serving models in async frameworks like FastAPI requires care to prevent blocking the event loop.

### 2. Concept Explanation
* **Why it exists**: ML models require microsecond-to-second calculations. Running these directly inside an async route blocks the single-threaded event loop, delaying all other concurrent requests.
* **When to use it**: Deploying predictive classifiers, stock forecasting models, or image recognition classifiers.
* **When NOT to use it**: Extremely large deep learning models (where dedicated model servers like Triton or TorchServe are preferred).
* **Advantages**: Low latency, native JSON support, easy integration with data science pipelines.
* **Disadvantages**: Heavy CPU operations can exhaust server resources if thread pools are not managed correctly.
* **Industry Use Cases**: Predictive search suggestions, customer churn analysis.

### 3. Architecture Explanation
The application loads model binaries (e.g. Scikit-learn `.joblib` files) during startup. Incoming inference requests are offloaded to an asynchronous executor (running in a separate thread pool) to protect the web server's event loop.
```
HTTP Request ---> [ Event Loop ] ---> Offloads to [ ThreadPoolExecutor ] ---> Run ML Inference
                                                                                    |
HTTP Response <--- [ Event Loop ] <--- Returns prediction <-------------------------/
```

### 4. Visual Workflow
```
Client Request ---> [ Event Loop (Free) ] ---> [ Worker Thread (Calculates) ] ---> Returns Response
```

### 5. Real-World Scenario
A financial API needs to serve stock market forecasts using a pre-trained regression model, handling hundreds of concurrent users without freezing the web server.

### 6. Step-by-Step Implementation
1. Install machine learning and serialization packages: `scikit-learn`, `joblib`, `numpy`.
2. Train a mock Linear Regression model and export it using `joblib`.
3. Create a FastAPI app that loads the model on startup.
4. Build a predict endpoint that offloads execution to a thread pool executor.

### 7. Source Code Examples
#### Model Training Script (`train_model.py`)
```python
import joblib
import numpy as np
from sklearn.linear_model import LinearRegression

# Train model (Predict stock price based on volume and moving average)
# X = [volume, moving_average]
X = np.array([[1000, 150], [1500, 152], [2000, 155], [2500, 158], [3000, 160]])
y = np.array([151.0, 153.2, 156.1, 159.0, 161.5])

model = LinearRegression()
model.fit(X, y)

# Export model binary
joblib.dump(model, "stock_model.joblib")
print("Model trained and saved to stock_model.joblib")
```

#### FastAPI Serving Script (`main.py`)
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Stock Prediction API")

# Initialize thread pool executor for CPU-heavy tasks
executor = ThreadPoolExecutor(max_workers=4)

# Load model global reference
model = None

@app.on_event("startup")
def load_stock_model():
    global model
    try:
        model = joblib.load("stock_model.joblib")
    except Exception as e:
        print(f"Error loading model: {e}")

class PredictionPayload(BaseModel):
    volume: int
    moving_average: float

# CPU-Bound inference function
def run_model_inference(volume: int, moving_average: float) -> float:
    input_data = np.array([[volume, moving_average]])
    prediction = model.predict(input_data)
    return float(prediction[0])

@app.post("/predict")
async def predict_stock_price(payload: PredictionPayload):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not initialized")
    
    # Run CPU-bound prediction in separate worker thread
    loop = asyncio.get_running_loop()
    predicted_value = await loop.run_in_executor(
        executor, 
        run_model_inference, 
        payload.volume, 
        payload.moving_average
    )
    
    return {
        "volume": payload.volume,
        "moving_average": payload.moving_average,
        "predicted_price": round(predicted_value, 2)
    }
```

### 8. API Testing Examples
Submit an inference request via curl:
```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"volume": 1800, "moving_average": 154.5}'
# Response:
# {"volume":1800,"moving_average":154.5,"predicted_price":155.07}
```

### 9. Common Mistakes
Running raw CPU-bound calls (`model.predict(data)`) directly inside `async def` routes, blocking the event loop for other concurrent users.

### 10. Best Practices
Always load machine learning model binaries once during application startup. Use `run_in_executor` to offload inference computations to a separate thread pool.

### 11. Interview Questions
* **Q: Why should you avoid running model predictions directly in async endpoints?**
  * *A*: Machine learning model inference is highly CPU-bound. In Python, CPU-bound operations block the execution thread. Running them in the main thread blocks the event loop, preventing it from processing other requests until the inference completes.

### 12. Chapter Summary
Exposing ML models requires running inference asynchronously. Using a thread pool executor protects the event loop from blocking during CPU-heavy tasks.

### 13. Practice Exercises
Extend the API to accept lists of input payloads and run batch inference concurrently.
