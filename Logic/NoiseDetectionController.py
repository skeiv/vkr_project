import cv2
import numpy as np


def detect_digital_noise(image, threshold_min, threshold_max):

    # Вычисление локального стандартного отклонения
    local_std = cv2.GaussianBlur(image, (5, 5), 0)
    local_std = cv2.subtract(image, local_std)
    local_std = cv2.convertScaleAbs(local_std)

    # Пороговое значение для обнаружения шума
    _, binary = cv2.threshold(local_std, 0, 255, cv2.THRESH_BINARY)
    threshold = np.mean(binary)

    if np.mean(threshold) > threshold_max or np.mean(threshold) < threshold_min:
        return True
    else:
        return False
