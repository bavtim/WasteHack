# WasteHack
## Использование разработанного решения
* Устанавливаем python 3.10 [тык](https://www.python.org/downloads/release/python-3100/)
* Скачиваем исходники Backend (папка Backend)
* Скачиваем разработанную модель [тык](https://drive.google.com/file/d/1eZ-92d_02oLWUbgqqCOhWFa-sNDZwhgU/view?usp=sharing)
* При помощи команды _pip install -r requirements.txt_ устанавливаем необходимые зависимости
* Запускаем решение _uvicorn main:app --reload_
* API взаимодействия доступно по ссылке _http://127.0.0.1:8000/docs_

## Использование примера приложения
* Устанавливаем python 3.10 [тык](https://www.python.org/downloads/release/python-3100/)
* Скачиваем исходники AppExample (папка AppExample)
* При помощи команды _pip install -r requirements.txt_ устанавливаем необходимые зависимости
* Запускаем _main.py_

Для работы с решением достаточно выполнить импорт, инициализацию класса и передать путь к видео
 ```
import file_func
from ultralytics import YOLO


def execute(video_path, model):
    uid_name_video = file_func.time_crop_video(video_path)
    name_video, results = file_func.extract_frames_from_video(uid_name_video, model)
    return results, name_video


if __name__ == '__main__':
    path=""
    model_v8m_35e_6cls = YOLO('model_yolov8m_for_35e_with_two_new_class.pt')
    dicts_results, name_video_with_bb = execute(path_video, model_v8m_35e_6cls)
```
По результаты работы будет выдана статистика и обработанное видео
