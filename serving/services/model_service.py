import os
import time
import logging
from typing import Any, Dict
from models import IrisInput, IrisPrediction

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def predict_with_model(model, iris_input: IrisInput) -> Dict[str, Any]:
    """
    Run prediction and predict_proba with a given model. Returns a dict with all relevant info.
    """
    start_time = time.time()
    features = {
        "SepalLengthCm": iris_input.SepalLengthCm,
        "SepalWidthCm": iris_input.SepalWidthCm,
        "PetalLengthCm": iris_input.PetalLengthCm,
        "PetalWidthCm": iris_input.PetalWidthCm
    }
    try:
        prediction = model.predict(features)
        result = IrisPrediction(Species=str(prediction[0]))
        py_model = model._model_impl.python_model
        label_encoder = py_model.label_encoder
        pred_text = str(prediction[0])
        pred_num = int(label_encoder.transform([pred_text])[0])
        try:
            proba = py_model.model.predict_proba([list(features.values())])[0]
            class_labels = label_encoder.classes_.tolist()
            class_prob_map = {str(cls): float(prob) for cls, prob in zip(class_labels, proba)}
        except Exception as e:
            logger.error(f"Failed to get class probabilities: {e}")
            proba = []
            class_prob_map = {}
        duration = time.time() - start_time
        return {
            "result": result.model_dump(),
            "prediction_value": pred_num,
            "class_probabilities": proba.tolist() if hasattr(proba, 'tolist') else proba,
            "class_probabilities_map": class_prob_map,
            "duration": duration,
            "error": None
        }
    except Exception as e:
        logger.error(f"Model prediction failed: {e}")
        return {
            "result": None,
            "prediction_value": None,
            "class_probabilities": [],
            "class_probabilities_map": {},
            "duration": time.time() - start_time,
            "error": str(e)
        } 