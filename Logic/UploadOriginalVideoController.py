import cv2
import numpy as np


def analyze_video(video_path):
    # Открытие видеофайла
    video = cv2.VideoCapture(video_path)

    while not video.isOpened():
        video = cv2.VideoCapture(video_path)
        cv2.waitKey(1000)

    # Инициализация переменных для хранения максимального и минимального порогов оптического потока и дефектов изображения
    min_optical_flow_threshold = float('inf')
    max_optical_flow_threshold = float('-inf')

    # Чтение первого кадра
    ret, prev_frame = video.read()

    thresholds = []
    # Цикл по всем кадрам видео
    while True:
        # Чтение следующего кадра
        ret, next_frame = video.read()

        # Проверка, удалось ли прочитать следующий кадр
        if not ret:
            break

        # Перевод кадров в градации серого
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)

        # Вычисление оптического потока с помощью алгоритма Farneback
        flow = cv2.calcOpticalFlowFarneback(prev_gray, next_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

        # Вычисление значения оптического потока
        flow_mean = np.mean(np.abs(flow))

        # Обновление максимального и минимального порогов оптического потока
        min_optical_flow_threshold = min(min_optical_flow_threshold, np.min(flow_mean))
        max_optical_flow_threshold = max(max_optical_flow_threshold, np.max(flow_mean))

        # Вычисление локального стандартного отклонения и порогового значения
        local_std = cv2.GaussianBlur(next_frame, (5, 5), 0)
        local_std = cv2.subtract(next_frame, local_std)
        local_std = cv2.convertScaleAbs(local_std)
        _, binary = cv2.threshold(local_std, 0, 255, cv2.THRESH_BINARY)
        threshold = np.mean(binary)
        # Добавление порогового значения в список
        thresholds.append(threshold)

        # Обновление текущего кадра
        prev_frame = next_frame


    # Вычисление порогового значения на основе статистических метрик
    threshold_max = np.max(thresholds)  # Можно использовать среднее значение порога или другую метрику
    threshold_min = np.min(thresholds)

    # Закрытие видеофайла
    video.release()

    # Возврат максимального и минимального порогов оптического потока и дефектов
    return min_optical_flow_threshold, max_optical_flow_threshold, threshold_min, threshold_max
