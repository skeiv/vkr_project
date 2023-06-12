import cv2
from matplotlib import pyplot as plt
import numpy as np


def detect_digital_noise(image, threshold):

    # Вычисление локального стандартного отклонения
    local_std = cv2.GaussianBlur(image, (5, 5), 0)
    local_std = cv2.subtract(image, local_std)
    local_std = cv2.convertScaleAbs(local_std)

    # Пороговое значение для обнаружения шума
    _, binary = cv2.threshold(local_std, threshold, 255, cv2.THRESH_BINARY)

    # Вычисление суммарной площади шума
    total_noise_area = np.sum(binary) / 255

    # Определение наличия цифрового шума
    return total_noise_area > 0
