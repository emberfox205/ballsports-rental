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
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgs.append(pil_img)
    imgs[1].save(f'frame_.jpg')
    camera.release()        
    print(len(imgs))
    print(process_image(imgs))


