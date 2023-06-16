import cv2
import numpy as np
import Logic.SkippingAndRepeatingFramesController as sarfController

# Глобальная переменная для хранения обрезанного видео
cropped_video_frames = []
fps = 0

def process_video(video_path):
    global cropped_video_frames

    # Загрузка оригинального видео
    cap = cv2.VideoCapture(video_path)
    global fps
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Проверка успешности загрузки видео
    if not cap.isOpened():
        print("Не удалось загрузить видео")
        return

    x = 0
    y = 0
    w = 0
    h = 0
    while True:
        # Чтение кадра из видео
        ret, frame = cap.read()

        # Проверка успешности чтения кадра
        if not ret:
            break

        # Обнаружение синего прямоугольника на первом кадре
        if len(cropped_video_frames) == 0:

            # Преобразование BGR изображения в HSV
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Определение диапазона синего цвета в HSV
            lower_blue = np.array([90, 0, 0])
            upper_blue = np.array([130, 255, 255])

            # Создание маски синего цвета
            mask = cv2.inRange(hsv_frame, lower_blue, upper_blue)

            # Поиск контуров на маске
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Фильтрация контуров по площади
            valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 500]

            if valid_contours:
                # Получение ограничивающего прямоугольника для самого большого контура
                x, y, w, h = cv2.boundingRect(max(valid_contours, key=cv2.contourArea))

        # Сохранение обрезанного кадра в глобальную переменную
        cropped_frame = frame[y:h, x:w]
        cropped_video_frames.append(cropped_frame)

        # Прерывание цикла при нажатии клавиши 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Освобождение ресурсов
    cap.release()
    cv2.destroyAllWindows()


def saveVideo():
    # Создание нового видео из обрезанных кадров
    if len(cropped_video_frames) == 0:
        print("Нет обрезанных кадров для создания видео")
        return

    # Получение размеров видео из первого обрезанного кадра
    height, width, _ = cropped_video_frames[0].shape

    # Создание объекта для сохранения видео
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Формат видео
    output = cv2.VideoWriter('temp.mp4', fourcc, 30.0, (width, height))

    # Запись обрезанных кадров в выходное видео
    for frame in cropped_video_frames:
        output.write(frame)

    # Закрытие объекта сохранения видео
    output.release()

def Preparation(input_video):

    # Запускаем функцию поиска и сохранения синего прямоугольника
    process_video(input_video)

    # Создание нового видео из обрезанных кадров
    saveVideo()




