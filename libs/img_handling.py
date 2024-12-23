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
class_logo_names = [
    'empty',
    'with_logo'
]
def preprocess_image(img, target_size=(224, 224)):
    """Load and preprocess an image for model prediction."""
    # Resize image
    img = img.resize(target_size)
    
    # Convert to array and expand dimensions
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array.astype(np.float32)
    
    # Normalize
    img_array = img_array / 255.0
    return img_array


def process_image(interpreter, input_details, output_details, img) -> dict: 
    try:
        pil_img = img
        input_data = preprocess_image(pil_img)
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        predictions = np.copy(interpreter.get_tensor(output_details[0]['index']))
        
        predicted_class_idx = np.argmax(predictions[0])
        confidence = predictions[0][predicted_class_idx]
        
        #print({
        #   'class_name': class_names[predicted_class_idx],
        #   'confidence': float(confidence)})
        return {'class_name': class_names[predicted_class_idx],'confidence': float(confidence)}
       
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None
def logo_check(interpreter, input_details, output_details, img) -> dict: 
    try:
        pil_img = img
        input_data = preprocess_image(pil_img, target_size=(160, 160))
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        predictions = np.copy(interpreter.get_tensor(output_details[0]['index']))
        
        predicted_class_idx = np.argmax(predictions[0])
        confidence = predictions[0][predicted_class_idx]
        
        #print({
        #   'class_name': class_names[predicted_class_idx],
        #   'confidence': float(confidence)})
        if class_logo_names[predicted_class_idx] == 'with_logo' and confidence >= 0.8:
            return "logo"
        else:
            return None
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None
    
def logo_check_(model, img) -> dict:
    try:
        pil_img = img
        preprocessed_img = preprocess_image(pil_img, target_size = (160,160))
        predictions = model.predict(preprocessed_img, verbose=0)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = predictions[0][predicted_class_idx]
        #print({
        #   'class_name': class_logo_names[predicted_class_idx],
        #   'confidence': float(confidence)})
        if class_logo_names[predicted_class_idx] == 'with_logo' and confidence >= 0.8:
            return "logo"
        else:
            return None
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None
