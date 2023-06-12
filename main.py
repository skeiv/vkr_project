import Logic.NoiseDetectionController as noiseDetectionController
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askopenfilename
import numpy as np
import cv2


video = ''


def getPathTest():
    global video
    video = askopenfilename()
    str = video.split('/')
    get_path_label.config(text=f'Выбран: {str[-1]}')

def start():
    if(video == ''):
        messagebox.showwarning("Ошибка", "Выберите видеофайл")
        return
    try:
        flow_min_threshold = float(flow_min_threshold_var.get())
        flow_max_threshold = float(flow_max_threshold_var.get())
        fourier_threshold = float(fourier_threshold_var.get())
    except:
        messagebox.showwarning("Ошибка", "Данные в полях для ввода должны быть действительными числами")
        return

    # Очистка текстового поля с заметками
    notes_text.delete(1.0, tk.END)

    # Вывод сообщений
    notes_text.insert(tk.END, "Выполняется...\n")

    detect_duplicates_and_gaps(video, flow_min_threshold, flow_max_threshold, fourier_threshold)

def exportToFile():
    file_path = asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])

    if file_path:
        try:
            with open(file_path, "w") as file:
                file.write(notes_text.get("1.0", tk.END))
            messagebox.showinfo("Успех", "Файл успешно экспортирован")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при экспорте файла: {str(e)}")

def finish():
    window.destroy()  # ручное закрытие окна и всего приложения

def add_log_message(message):
    notes_text.insert(tk.END, message + '\n')

def detect_duplicates_and_gaps(video_path, flow_min_threshold, flow_max_threshold, fourier_threshold):

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    add_log_message(f'Количество кадров в секунду: {round(fps, 2)}')
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while not cap.isOpened():
        cap = cv2.VideoCapture(video_path)
        cv2.waitKey(1000)

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
        if(noiseDetectionController.detect_digital_noise(image, fourier_threshold)):
            add_log_message(f'Обнаружен дефект. Кадр: {frame_index}')
            errStr = 'Defect detecting'
        # Читаем следующий кадр
        ret, curr_frame = cap.read()

        if not ret:
            break

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
            add_log_message(f'Возможный повтор кадров: кадры {duplicate_start}-{duplicate_end}')

        if flow_mean > flow_max_threshold and not isGap:
            gap_start = frame_index
            isGap = True

        if flow_mean <flow_max_threshold and isGap:
            gap_end = frame_index
            isGap = False
            add_log_message(f'Возможный пропуск кадров: кадры {gap_start}-{gap_end}')

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

global window
window = tk.Tk()
window.title("vkr")
window.minsize(350, 1)
window.protocol("WM_DELETE_WINDOW", finish)

# Создание переменных для значений переменных
global flow_min_threshold_var
flow_min_threshold_var = tk.StringVar(value="0.17")
global flow_max_threshold_var
flow_max_threshold_var = tk.StringVar(value="0.49")
global fourier_threshold_var
fourier_threshold_var = tk.StringVar(value="100.0")

# Создание левой части окна
left_frame = tk.Frame(window)
left_frame.grid(row=0, column=0, padx=10, pady=10)

# Создание кнопки "Получить путь"
get_path_button = tk.Button(left_frame, text="Выберите видеофайл", command=getPathTest)
get_path_button.grid(row=0, column=0, pady=10)
global get_path_label
get_path_label = Label(left_frame, text="Видеофайл не выбран")
get_path_label.grid(column=1, row=0, pady=10)

# Создание полей для ввода переменных
flow_min_threshold_label = tk.Label(left_frame, text="flow_min_threshold:")
flow_min_threshold_label.grid(row=1, column=0, sticky=tk.W)
flow_min_threshold_entry = tk.Entry(left_frame, textvariable=flow_min_threshold_var)
flow_min_threshold_entry.grid(row=1, column=1, pady=5)

flow_max_threshold_label = tk.Label(left_frame, text="flow_max_threshold:")
flow_max_threshold_label.grid(row=2, column=0, sticky=tk.W)
flow_max_threshold_entry = tk.Entry(left_frame, textvariable=flow_max_threshold_var)
flow_max_threshold_entry.grid(row=2, column=1, pady=5)

fourier_threshold_label = tk.Label(left_frame, text="fourier_threshold:")
fourier_threshold_label.grid(row=3, column=0, sticky=tk.W)
fourier_threshold_entry = tk.Entry(left_frame, textvariable=fourier_threshold_var)
fourier_threshold_entry.grid(row=3, column=1, pady=5)

# Создание нижней части окна
bottom_frame = tk.Frame(window)
bottom_frame.grid(row=1, column=0, columnspan=2)

# Создание кнопки "Старт"
start_button = tk.Button(bottom_frame, text="Начать", command=start)
start_button.grid(row=0, column=0, pady=10)

# Создание кнопки "Экспорт в файл"
export_button = tk.Button(bottom_frame, text="Экспорт в файл", command=exportToFile)
export_button.grid(row=0, column=1, pady=10)

# Создание правой части окна
right_frame = tk.Frame(window)
right_frame.grid(row=0, column=1, padx=10, pady=10)

# Создание текстового поля с заметками и прокруткой
global notes_text
notes_text = scrolledtext.ScrolledText(right_frame, width=40, height=10)
notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Создание прокрутки для текстового поля
scrollbar = tk.Scrollbar(right_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Привязка прокрутки к текстовому полю
notes_text.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=notes_text.yview)


window.mainloop()

