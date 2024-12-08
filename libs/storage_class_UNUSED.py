

class Detected_Object:
    def __init__(self, name: str, confidence_score: float, image):
        self.name = name
        self.score = confidence_score
        self.image = image 
    def __str__(self):
        return f"Ball type: {self.name}\nConfidence Score: {self.score}"