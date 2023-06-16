import cv2
import numpy as np
import os
import Logic.NoiseDetectionController as noiseDetectionController


def add_log_message(message, notes=None):
    return notes + message + '\n'


def detect_duplicates_and_gaps(flow_min_threshold, flow_max_threshold, local_min_threshold, local_max_threshold):
    notes = ''
    cap = cv2.VideoCapture('temp.mp4')
    fps = cap.get(cv2.CAP_PROP_FPS)
    notes = add_log_message(f'Количество кадров в секунду: {round(fps, 2)}', notes)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if not cap.isOpened():
        cap = cv2.VideoCapture('temp.mp4')
        return 'Ошибка'

    # Читаем первый кадр и инициализируем переменные
    ret, prev_frame = cap.read()
    prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    frame_index = 0
    duplicate_start = 0
    duplicate_end = 0
    gap_start = 0
    gap_end = 0

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    isGap = False
    isDuplicate = False

    while True:
        errStr = ''
        # Преобразуем кадр в изображение
        image = cv2.cvtColor(prev_frame, cv2.IMREAD_GRAYSCALE)
        # Читаем следующий кадр
        ret, curr_frame = cap.read()

        if not ret:
            break

        if(noiseDetectionController.detect_digital_noise(curr_frame, local_min_threshold, local_max_threshold)):
            notes = add_log_message(f'Обнаружен дефект. Кадр: {frame_index}', notes)
            errStr = 'Defect detecting'

        position = (10, height - 10)
        cv2.putText(image, # numpy array on which text is written
                     f'{frame_index}/{frame_count} {errStr}',#text
                     position, #position at which writing has to start
                     cv2.FONT_HERSHEY_SIMPLEX, #font family
                     1, #font size
                     (200, 200, 200, 255), #font color
                     3) #font stroke

        # Показываем видео
        cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Video', width // 2, height // 2)
        cv2.imshow("Video", image)

        curr_frame_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        # Вычисляем оптический поток между текущим и предыдущим кадрами
        flow = cv2.calcOpticalFlowFarneback(prev_frame_gray, curr_frame_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

        # Вычисляем среднюю величину оптического потока для кадра
        flow_mean = np.mean(np.abs(flow))

        if flow_mean < flow_min_threshold and not isDuplicate:
            duplicate_start = frame_index
            isDuplicate = True

        if flow_mean > flow_min_threshold and isDuplicate:
            duplicate_end = frame_index
            isDuplicate = False
            notes = add_log_message(f'Возможный повтор кадров: кадры {duplicate_start}-{duplicate_end}', notes)

        if flow_mean > flow_max_threshold and not isGap:
            gap_start = frame_index
            isGap = True

        if flow_mean <flow_max_threshold and isGap:
            gap_end = frame_index
            isGap = False
            notes = add_log_message(f'Возможный пропуск кадров: кадры {gap_start}-{gap_end}', notes)

        # Обновляем предыдущий кадр и индекс
        prev_frame_gray = curr_frame_gray
        prev_frame = curr_frame
        print(frame_index)
        frame_index += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Проверяем состояние окна и выходим из цикла, если окно закрыто
        if cv2.getWindowProperty('Video', cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()

    os.remove('temp.mp4')

    return notes
