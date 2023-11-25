import cv2
import uuid

import numpy as np

from PIL import Image

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


def time_crop_video(path_video):
    '''
    Функция принимает на вход видео и обрезает его по времени приезда самосвала
    '''
    time_start_in_second = 110  # 1 min 50 sec
    time_end_in_second = 150  # 2 min 30 sec
    uid = str(uuid.uuid4())
    name_crop_video = uid + ".mp4"

    ffmpeg_extract_subclip(path_video,
                           time_start_in_second,
                           time_end_in_second,
                           targetname=name_crop_video)

    return name_crop_video


def create_video(list_frames_without,
                 list_frames_with,
                 path_video,
                 list_bool):
    height, width, _ = np.array(list_frames_without[0]).shape

    writer = cv2.VideoWriter(
        path_video,
        cv2.VideoWriter_fourcc(*'XVID'),  # codec
        12.0,

        (width, height))

    for index_bool, digit_bool in enumerate(list_bool):
        if digit_bool == 0:
            writer.write(np.array(list_frames_without[index_bool]))
        elif digit_bool == 1:
            writer.write(np.array(list_frames_with[index_bool]))

    writer.release()
    cv2.destroyAllWindows()

    return path_video


def approve(results):
    list_bool_frame = []
    coef = 0.07

    for iterator_index in range(len(results)):

        try:
            x = results[iterator_index][0].boxes.xyxy[0][2] - results[iterator_index][0].boxes.xyxy[0][0]
            y = results[iterator_index][0].boxes.xyxy[0][3] - results[iterator_index][0].boxes.xyxy[0][1]
            square = float(x * y)
        except:
            square = 0
        square_img = 720 * 720
        coef_square = square / square_img
        if coef_square > coef:
            list_bool_frame.append(1)
        else:
            list_bool_frame.append(0)

    for iterator_index_bool, iterator_bool in enumerate(list_bool_frame):
        try:
            if iterator_bool != list_bool_frame[iterator_index_bool - 1] and iterator_bool != list_bool_frame[
                iterator_index_bool + 1]:
                if iterator_bool != 0:
                    list_bool_frame[iterator_index_bool] = 0
                else:
                    list_bool_frame[iterator_index_bool] = 1
        except:
            continue

    return list_bool_frame


def schet_results(results, list_bool):
    list_beton = []
    list_brezent = []
    list_brick = []
    list_dirt = []
    list_empty = []
    list_wood = []
    lists_materials = [list_beton,
                       list_brezent,
                       list_brick,
                       list_dirt,
                       list_empty,
                       list_wood]

    list_conf_beton = []
    list_conf_brezent = []
    list_conf_brick = []
    list_conf_dirt = []
    list_conf_empty = []
    list_conf_wood = []
    lists_conf_materials = [list_conf_beton,
                            list_conf_brezent,
                            list_conf_brick,
                            list_conf_dirt,
                            list_conf_empty,
                            list_conf_wood]

    for iterator_index in range(len(results)):

        if list_bool[iterator_index] == 1:

            for iterator_index_inside_results in range(len(results[iterator_index][0].boxes.cls)):
                index_class = int(results[iterator_index][0].boxes.cls[iterator_index_inside_results])
                lists_materials[index_class].append(1)
                lists_conf_materials[index_class].append(
                    float(results[iterator_index][0].boxes.conf[iterator_index_inside_results]))

    for iterator_index in range(len(lists_materials)):
        lists_materials[iterator_index] = sum(lists_materials[iterator_index])
        if len(lists_conf_materials[iterator_index]) == 0:
            lists_conf_materials[iterator_index] = 0
        else:
            lists_conf_materials[iterator_index] = round(
                sum(lists_conf_materials[iterator_index]) / len(lists_conf_materials[iterator_index]), 2)

    dict_classes = {'beton': {lists_materials[0]: lists_conf_materials[0]},
                    'brezent': {lists_materials[1]: lists_conf_materials[1]},
                    'brick': {lists_materials[2]: lists_conf_materials[2]},
                    'dirt': {lists_materials[3]: lists_conf_materials[3]},
                    'empty': {lists_materials[4]: lists_conf_materials[4]},
                    'wood': {lists_materials[5]: lists_conf_materials[5]}
                    }

    return dict_classes


def extract_frames_from_video(path_video, detect_class_model):
    vidcap = cv2.VideoCapture(path_video)
    success, image = vidcap.read()
    list_frames_plot_for_video = []
    list_frames_without_plot_for_video = []
    list_result = []

    while success:

        results_detect_class_model = detect_class_model.predict(image, imgsz=736, conf=0.45)
        for r in results_detect_class_model:
            image_array = r.plot()  # plot a BGR numpy array of predictions
            image_pil = Image.fromarray(image_array[..., ::-1])  # RGB PIL image
            list_frames_without_plot_for_video.append(image)
            list_frames_plot_for_video.append(image_pil)
        list_result.append(results_detect_class_model)

        success, image = vidcap.read()

    list_bool = approve(list_result)
    return_dict = schet_results(list_result, list_bool)
    name_label_video = create_video(list_frames_without_plot_for_video,
                                    list_frames_plot_for_video,
                                    path_video,
                                    list_bool)

    return name_label_video, return_dict