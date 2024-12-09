import tensorflow as tf
import numpy as np
from PIL import Image
class_names = [
    'american_football',
    'baseball',
    'basketball',
    'football',
    'table_tennis_ball',
    'tennis_ball',
    'volleyball'
]

def preprocess_image(img, target_size=(224, 224)):
    """Load and preprocess an image for model prediction."""
    # Resize image
    img = img.resize(target_size)
    
    # Convert to array and expand dimensions
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    
    # Normalize
    img_array = img_array / 255.0
    
    return img_array



def process_image(model, img) -> dict: 
    try:
        pil_img = img
        preprocessed_img = preprocess_image(pil_img)
        predictions = model.predict(preprocessed_img)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = predictions[0][predicted_class_idx]
        print({
            'class_name': class_names[predicted_class_idx],
            'confidence': float(confidence)})
        if round(float(confidence), 4) > 0.85: # Set bottom limit for best results ** TANGABLE **
            return {'class_name': class_names[predicted_class_idx],'confidence': float(confidence)}
        return None
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None




