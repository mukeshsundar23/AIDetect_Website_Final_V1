import tensorflow as tf
import tensorflow_text
import os
import numpy as np
from lime.lime_text import LimeTextExplainer
import re

# Absolute paths to text model components
VECTORIZER_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "models", "text", "vectorizer_model")
)

MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "models", "text", "ai_text_model")
)

vectorizer_model = tf.keras.layers.TFSMLayer(VECTORIZER_PATH, call_endpoint="serving_default")
main_model = tf.keras.layers.TFSMLayer(MODEL_PATH, call_endpoint="serving_default")

def predict_text(text: str, explain=False):
    try:
        input_tensor = tf.constant([[text]])  # shape (1, 1)
        vectorized = vectorizer_model(input_tensor)

        # If wrapped in a dict, unwrap it
        if isinstance(vectorized, dict):
            vectorized = list(vectorized.values())[0]

        output = main_model(vectorized)

        # If wrapped in a dict, unwrap
        if isinstance(output, dict):
            output = output.get("predictions") or list(output.values())[0]

        # Convert to float
        if isinstance(output, tf.Tensor):
            output = output.numpy()

        score = float(output[0][0]) if hasattr(output[0], '__getitem__') else float(output[0])

        label = "AI-generated" if score > 0.5 else "Human-written"
        confidence = score if label == "AI-generated" else 1 - score
        
        result = {
            "label": label,
            "confidence": round(confidence, 4)
        }
        
        # Add LIME explanations if requested
        if explain:
            lime_result = generate_lime_explanation(text, label)
            result.update(lime_result)
            
        return result

    except Exception as e:
        return {"error": str(e)}

def model_predict_fn(texts):
    """Wrapper function for LIME to use our model"""
    results = []
    for text in texts:
        input_tensor = tf.constant([[text]])
        vectorized = vectorizer_model(input_tensor)
        
        # If wrapped in a dict, unwrap it
        if isinstance(vectorized, dict):
            vectorized = list(vectorized.values())[0]
            
        output = main_model(vectorized)
        
        # If wrapped in a dict, unwrap
        if isinstance(output, dict):
            output = output.get("predictions") or list(output.values())[0]
            
        # Convert to float
        if isinstance(output, tf.Tensor):
            output = output.numpy()
            
        score = float(output[0][0]) if hasattr(output[0], '__getitem__') else float(output[0])
        results.append([1-score, score])  # [human_prob, ai_prob]
    
    return np.array(results)

def generate_lime_explanation(text, label):
    """Generate LIME explanations for the model's prediction"""
    try:
        # Initialize LIME explainer
        explainer = LimeTextExplainer(class_names=["Human-written", "AI-generated"])
        
        # Generate explanation
        exp = explainer.explain_instance(
            text, 
            model_predict_fn, 
            num_features=10,
            num_samples=100
        )
        
        # Get the explanation for the predicted class
        class_idx = 1 if label == "AI-generated" else 0
        
        # Get top features with weights
        feature_weights = {}
        for feature, weight in exp.as_list(label=class_idx):
            feature_weights[feature] = weight
        
        # Generate human-readable explanations
        lime_explanations = []
        
        # Add overall explanation
        lime_explanations.append(f"Model detected {label} content with {round(exp.score*100)}% confidence")
        
        # Add explanations based on top features
        positive_features = [f for f, w in exp.as_list(label=class_idx) if w > 0]
        negative_features = [f for f, w in exp.as_list(label=class_idx) if w < 0]
        
        if positive_features:
            if label == "AI-generated":
                lime_explanations.append(f"Key indicators of AI generation: {', '.join(positive_features[:3])}")
            else:
                lime_explanations.append(f"Key indicators of human writing: {', '.join(positive_features[:3])}")
        
        if negative_features:
            if label == "AI-generated":
                lime_explanations.append(f"Features suggesting human authorship: {', '.join(negative_features[:3])}")
            else:
                lime_explanations.append(f"Features suggesting AI generation: {', '.join(negative_features[:3])}")
        
        # Add text statistics for additional context
        word_count = len(re.findall(r'\b\w+\b', text))
        sentence_count = len(re.findall(r'[.!?]+', text)) + 1
        avg_words_per_sentence = word_count / max(1, sentence_count)
        
        lime_explanations.append(f"Text statistics: {word_count} words, {sentence_count} sentences, {avg_words_per_sentence:.1f} words per sentence")
        
        return {
            "lime_explanations": lime_explanations,
            "feature_weights": feature_weights
        }
    except Exception as e:
        # If LIME fails, return basic explanations
        return {
            "lime_explanations": [
                f"Model detected {label} content",
                f"Unable to generate detailed explanations: {str(e)}"
            ]
        }