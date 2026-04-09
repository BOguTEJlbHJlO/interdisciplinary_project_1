import cv2
from detector import Detector
from logic import PPELogic
from visualizer import Visualizer
class VideoProcessor:
    def __init__(self):
        self.detector = Detector()
        self.logic = PPELogic()
        self.visualizer = Visualizer()

    def process(self, source=0):
        cap = cv2.VideoCapture(source)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            detections = self.detector.detect(frame)
            results = self.logic.check_ppe(detections)
            frame = self.visualizer.draw(frame, results)

            cv2.imshow("PPE System", frame)

            if cv2.waitKey(1) == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
    '''
    Формат данных:
    [
    {"class": "person", "bbox": [x1,y1,x2,y2]},
    {"class": "helmet", "bbox": [...]}
    ]'''

    '''Результат: 
    [
    {
        "bbox": [...],
        "helmet": True,
        "vest": False,
        "status": "NO VEST"
    }
    ]'''