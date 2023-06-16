import Logic.SkippingAndRepeatingFramesController as sarfController
import Logic.UploadOriginalVideoController as uovController
import Logic.PreparationVideoController as pvController
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askopenfilename


originalVideo = ''
video = ''

def getOriginalPathTest():
    global originalVideo
    originalVideo = askopenfilename()
    str = originalVideo.split('/')
    get_orig_path_label.config(text=f'Выбран: {str[-1]}')
    uploadVideo()

def uploadVideo():
    if(originalVideo == ''):
        messagebox.showwarning("Ошибка", "Выберите видеофайл")
        return
    notes_text.insert(tk.END, "Загрузка видео...\n")
    flow_min_threshold_var, flow_max_threshold_var, local_min_threshold_var, local_max_threshold_var = uovController.analyze_video(originalVideo)
    # Вывод сообщений
    notes_text.insert(tk.END, "Загрузка видео прошла успешно\n")
    notes_text.insert(tk.END, flow_min_threshold_var.__str__() + "\n")
    notes_text.insert(tk.END, flow_max_threshold_var.__str__() + "\n")
    notes_text.insert(tk.END, local_min_threshold_var.__str__() + "\n")
    notes_text.insert(tk.END, local_max_threshold_var.__str__() + "\n")
    flow_min_threshold_entry.delete(0, tk.END)
    flow_min_threshold_entry.insert(0, flow_min_threshold_var)
    flow_max_threshold_entry.delete(0, tk.END)
    flow_max_threshold_entry.insert(0, flow_max_threshold_var)
    local_min_threshold_entry.delete(0, tk.END)
    local_min_threshold_entry.insert(0, local_min_threshold_var)
    local_max_threshold_entry.delete(0, tk.END)
    local_max_threshold_entry.insert(0, local_max_threshold_var)

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
        local_min_threshold = float(local_min_threshold_var.get())
        local_max_threshold = float(local_max_threshold_var.get())
    except:
        messagebox.showwarning("Ошибка", "Данные в полях для ввода должны быть действительными числами")
        return

    # Очистка текстового поля с заметками
    notes_text.delete(1.0, tk.END)

    # Вывод сообщений
    notes_text.insert(tk.END, "Выполняется...\n")

    pvController.Preparation(video)
    notes_text.insert(tk.END, sarfController.detect_duplicates_and_gaps(flow_min_threshold, flow_max_threshold,
                                                                        local_min_threshold, local_max_threshold))

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

global window
window = tk.Tk()
window.title("vkr")
window.minsize(350, 1)
window.protocol("WM_DELETE_WINDOW", finish)

# Создание переменных для значений переменных
global flow_min_threshold_var
flow_min_threshold_var = tk.StringVar(value="0.1")
global flow_max_threshold_var
flow_max_threshold_var = tk.StringVar(value="0.5")
global local_min_threshold_var
local_min_threshold_var = tk.StringVar(value="0.0")
global local_max_threshold_var
local_max_threshold_var = tk.StringVar(value="100.0")

# Создание левой части окна
left_frame = tk.Frame(window)
left_frame.grid(row=0, column=0, padx=10, pady=10)

# Создание кнопки "Получить путь"
get_path_button = tk.Button(left_frame, text="Выберите оригинальный видеофайл", command=getOriginalPathTest)
get_path_button.grid(row=0, column=0, pady=10)
global get_orig_path_label
get_orig_path_label = Label(left_frame, text="Видеофайл не выбран")
get_orig_path_label.grid(column=1, row=0, pady=10)

# Создание кнопки "Получить путь"
get_path_button = tk.Button(left_frame, text="Выберите тестируемый видеофайл", command=getPathTest)
get_path_button.grid(row=1, column=0, pady=10)
global get_path_label
get_path_label = Label(left_frame, text="Видеофайл не выбран")
get_path_label.grid(column=1, row=1, pady=10)

# Создание полей для ввода переменных
flow_min_threshold_label = tk.Label(left_frame, text="flow_min_threshold:")
flow_min_threshold_label.grid(row=2, column=0, sticky=tk.W)
flow_min_threshold_entry = tk.Entry(left_frame, textvariable=flow_min_threshold_var)
flow_min_threshold_entry.grid(row=2, column=1, pady=5)

flow_max_threshold_label = tk.Label(left_frame, text="flow_max_threshold:")
flow_max_threshold_label.grid(row=3, column=0, sticky=tk.W)
flow_max_threshold_entry = tk.Entry(left_frame, textvariable=flow_max_threshold_var)
flow_max_threshold_entry.grid(row=3, column=1, pady=5)

local_min_threshold_label = tk.Label(left_frame, text="local_min_threshold_var:")
local_min_threshold_label.grid(row=4, column=0, sticky=tk.W)
local_min_threshold_entry = tk.Entry(left_frame, textvariable=local_min_threshold_var)
local_min_threshold_entry.grid(row=4, column=1, pady=5)

local_max_threshold_label = tk.Label(left_frame, text="local_max_threshold_var:")
local_max_threshold_label.grid(row=5, column=0, sticky=tk.W)
local_max_threshold_entry = tk.Entry(left_frame, textvariable=local_max_threshold_var)
local_max_threshold_entry.grid(row=5, column=1, pady=5)


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

