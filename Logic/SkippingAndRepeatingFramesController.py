import cv2
import numpy as np
import Logic.NoiseDetectionController as noiseDetectionController
import main


def detect_duplicates_and_gaps(video_path, flow_min_threshold, flow_max_threshold, fourier_threshold):

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    while not cap.isOpened():
        cap = cv2.VideoCapture(video_path)
        cv2.waitKey(1000)

    # Читаем первый кадр и инициализируем переменные
    ret, prev_frame = cap.read()
    prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    frame_index = 0
    duplicates = []
    gaps = []

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    while True:
        if(noiseDetectionController.detect_digital_noise(prev_frame, fourier_threshold)):
            main.add_log_message(f'Обнаружен дефект. Кадр: {frame_index}')
        # Читаем следующий кадр
        ret, curr_frame = cap.read()

        main.update_progress(round(frame_index / fps) * 100)
        if not ret:
            break

        # Преобразуем кадр в изображение
        image = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2RGB)

        # Показываем видео
        cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Video', width // 2, height // 2)
        cv2.imshow("Video", image)

        curr_frame_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        # Вычисляем оптический поток между текущим и предыдущим кадрами
        flow = cv2.calcOpticalFlowFarneback(prev_frame_gray, curr_frame_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

        # Вычисляем среднюю величину оптического потока для кадра
        flow_mean = np.mean(np.abs(flow))

        # Если средняя величина потока близка к нулю, это может быть дубликат кадра
        if flow_mean < flow_min_threshold:
            duplicates.append(frame_index)

        # Если кадр был пропущен (сильные движения)
        if flow_mean > flow_max_threshold:
            gaps.append(frame_index)

        # Обновляем предыдущий кадр и индекс
        prev_frame_gray = curr_frame_gray
        print(frame_index)
        frame_index += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Проверяем состояние окна и выходим из цикла, если окно закрыто
        if cv2.getWindowProperty('Video', cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()

    return duplicates, gaps
