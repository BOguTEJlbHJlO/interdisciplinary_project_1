class PPELogic:
    def __init__(self):
        pass

    def check_ppe(self, detections):
        """
        detections → список объектов

        Возвращает:
        [
          {
            "person_bbox": [...],
            "helmet": True/False,
            "vest": True/False,
            "status": "OK / NO HELMET / NO VEST"
          }
        ]
        """
        pass
    def is_inside(boxA, boxB):
        """
        Проверяет: boxA внутри boxB
        """
        pass
    def match_objects(persons, helmets, vests):
        """
        Связывает СИЗ с людьми
        """
        pass