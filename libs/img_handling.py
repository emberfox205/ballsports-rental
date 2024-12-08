import tensorflow as tf
import numpy as np
from PIL import Image
import cv2
from flask import jsonify 
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



def process_image(img_list:list) -> str: 
    # Example usage
    image_path = 'inputs/image.jpg'
    i = 0
    high_accus = []
    try:
        #camera = cv2.VideoCapture('inputs/Ball.mp4')
        model = tf.keras.models.load_model('model/uncleanse_ball_classification_model.keras')
        
        while i < len(img_list):
          
            #pil_img = Image.open(image_path)
            
            if i % 3 == 0: # Detect ball each 5 frame for efficency ** TANGABLE **
                pil_img = img_list[i]
                preprocessed_img = preprocess_image(pil_img)
                predictions = model.predict(preprocessed_img)
                predicted_class_idx = np.argmax(predictions[0])
                confidence = predictions[0][predicted_class_idx]
                print({
                    'class_name': class_names[predicted_class_idx],
                    'confidence': float(confidence)})
                if round(float(confidence), 4) > 0.85: # Set bottom limit for best results ** TANGABLE **
                    high_accus.append({
                    'class_name': class_names[predicted_class_idx],
                    'confidence': float(confidence)})
                
            i += 1
            if len(high_accus) > 2:  # Ratio for detected_w_high_acc/ number of frames ** TANGABLE **
                return ({
                    'class_name': max(high_accus, key=lambda x: x['confidence'])['class_name'],
                    'confidence': max(high_accus, key=lambda x: x['confidence'])['confidence']
                }) ## Should be json
        return None
           
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None

if __name__ == "__main__":
    imgs = []
    imgs.append(Image.open("inputs/image.jpg"))
    imgs.append(Image.open("inputs/sample.jpg"))
    imgs.append(Image.open("inputs/sample.jpg"))
    imgs.append(Image.open("inputs/valley.jpg"))
    imgs.append(Image.open("inputs/valley.jpg"))
    imgs.append(Image.open("inputs/valley.jpg"))
    imgs.append(Image.open("inputs/sample.jpg"))    
 
    #Mimic
    camera = cv2.VideoCapture('inputs/Ball.mp4')
    for i in range(200):
        if i % 10 == 0:    
            success, frame = camera.read()
            if not success:
                print("Can not read camera")
                break
            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                camera.release()
                break
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            imgs.append(pil_img)
            
    print(len(imgs))
    print(process_image(imgs))


