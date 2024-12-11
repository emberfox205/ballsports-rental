import tensorflow as tf
import numpy as np
from PIL import Image
import cv2, base64
from flask import jsonify 
from io import BytesIO
import time
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
model = tf.keras.models.load_model('model/model.keras', compile=False)
logo = tf.keras.models.load_model('model/logo.keras', compile=False)
recognition_data =  {
    'ball_name': None,  
    'accuracy': None,
    'recognition_count': 0  
}


def preprocess_image(img, target_size=(224, 224)):
    img = img.resize(target_size)
    
    # Convert to array and expand dimensions
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
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

def logo_check(model, img) -> dict:
    try:
        pil_img = img
        preprocessed_img = preprocess_image(pil_img)
        predictions = model.predict(preprocessed_img)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = predictions[0][predicted_class_idx]
        print({
            'class_name': class_logo_names[predicted_class_idx],
            'confidence': float(confidence)})
        return {'class_name': class_logo_names[predicted_class_idx],'confidence': float(confidence)}
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None




def detect(image):

    start_time = time.time()
    is_recognized = process_image(model, image)  # return dict {"class_name": ,"confidence": }
    have_logo = logo_check(logo, image)
    logo_check_time = time.time() - start_time
    print(f"Time taken for: {logo_check_time} seconds")

    if is_recognized:
        
        # First recognition
        if recognition_data['ball_name'] is None:
            recognition_data['ball_name'] = is_recognized["class_name"]
            recognition_data['confidence'] = is_recognized["confidence"]
            recognition_data['recognition_count'] = 1
        
        # If next recognition produce same result
        elif recognition_data['ball_name'] == is_recognized["class_name"]:
            recognition_data['confidence'] =  is_recognized["confidence"]
            recognition_data['recognition_count'] += 1
        
        # Reset if diffrent result is detected
        else:
            recognition_data['ball_name'] = is_recognized["class_name"]
            recognition_data['confidence'] = is_recognized["confidence"]
            recognition_data['recognition_count'] = 1

        

        # Check if the count reaches the threshold
        if recognition_data['recognition_count'] >= 10:  # Reset after success
            recognition_data['recognition_count'] = 0
            print("Detected", {
        'ball_name': recognition_data['ball_name'],
        'confidence': recognition_data['confidence'],
        'recognition_count': recognition_data['recognition_count']
    })
            return

if __name__ == "__main__":
    """"imgs = []
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
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            detect(pil_img)"""
            
    with open('recognized_ball.txt', 'r') as file:
        image = file.read()
    image = image.split(',')[1]
    image = base64.b64decode(image)  # Skip the data URI prefix, idk what this is
    image = Image.open(BytesIO(image))
    image = image.convert('RGB')
    detect(image)