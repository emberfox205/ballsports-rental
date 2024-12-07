import cv2
import time

def scanner():
    camera = cv2.VideoCapture('/mnt/d/Coding_Projects/PythonHacks/Intro_CS/ballsports-rental/inputs/Ball.mp4')
    fps = camera.get(cv2.CAP_PROP_FPS)
    delay = 1 / fps

    # Check for available camera
    while True:
        # read the camera frame
        success, frame = camera.read()
        if not success:
            print("Can not read camera")
            break
        else:
            print("reading")
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        time.sleep(delay)