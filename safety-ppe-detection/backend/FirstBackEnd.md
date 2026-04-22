# Первый BackEnd:

* изучить формат вывода YOLO
* описать структуру данных:

```python
Detection = {
  "class": str,
  "bbox": [x1, y1, x2, y2],
  "conf": float
}
```

* написать:

  * `is_inside(boxA, boxB)`

---

* реализовать:

  * `split_detections()` → разделить:

    * people
    * helmets
    * vests

---

* реализовать:

  * `check_ppe()`
* логика:

  * helmet внутри person → True
  * vest внутри person → True

---

* добавить:

  * статус:

    * OK
    * NO HELMET
    * NO VEST

---

* реализовать:

  * лог нарушений:

```python
[time, status]
```

---

* улучшить:

  * обработку ошибок
  * edge cases:

    * несколько людей
    * несколько касок

---

* проверить:

  * корректность логики
* пофиксить баги

---

* подготовить:

  * описание логики (для отчёта)

  
