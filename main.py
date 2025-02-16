import base64
import math
import cv2
import numpy as np
import pyautogui
import time
from screeninfo import get_monitors
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox
import pygetwindow as gw 

pyautogui.PAUSE = 0  # Устанавливаем небольшую паузу между действиями

def get_screen_resolution():
    monitor = get_monitors()[0]
    screen_resolution = (monitor.width, monitor.height)
    return screen_resolution

def calculate_window_area(window):
    # Координаты окна
    window_area_top_left_x = window.left
    window_area_top_left_y = window.top
    window_area_bottom_right_x = window.right
    window_area_bottom_right_y = window.bottom

    return (window_area_top_left_x, window_area_top_left_y), (window_area_bottom_right_x, window_area_bottom_right_y)

def calculate_roi(window_width, window_height, center_x, center_y):
    roi_top_left_x = center_x - (window_width // 2)
    roi_top_left_y = center_y - (window_height // 2)
    roi_bottom_right_x = center_x + (window_width // 2)
    roi_bottom_right_y = center_y + (window_height // 2)

    return (roi_top_left_x, roi_top_left_y), (roi_bottom_right_x, roi_bottom_right_y)

# Функция для отслеживания объектов по цвету в заданной области
def detect_color_objects(frame, color_bounds):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    detected_objects = {}
    for color_name, (lower_bound, upper_bound) in color_bounds.items():
        mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        detected_objects[color_name] = contours
    return detected_objects

def calculate_center(x, y, w, h):
    return (x + w // 2, y + h // 2)

def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def handle_detections(detected_objects, roi_top_left, min_size, max_size):
    bomb_contours = detected_objects.get('bomb', [])
    bomb_centers_sizes = []

    for bomb_contour in bomb_contours:
        x, y, w, h = cv2.boundingRect(bomb_contour)
        bomb_center = calculate_center(x, y, w, h)
        bomb_centers_sizes.append((bomb_center, max(w, h) * 2))

    for color_name, contours in detected_objects.items():
        if color_name == 'bomb':
            continue
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if min_size[0] <= w <= max_size[0] and min_size[1] <= h <= max_size[1]:
                target_center = calculate_center(x, y, w, h)
                # Проверка на минимальное расстояние до любой из бомб
                if all(distance(target_center, bomb_center) > bomb_size for bomb_center, bomb_size in bomb_centers_sizes):
                    x += roi_top_left[0]
                    y += roi_top_left[1]
                    pyautogui.click(x + w // 2, y + h // 2)

# Base64 строка изображения
image_base64 = "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"

def save_image_from_base64(base64_string, output_path):
    image_data = base64.b64decode(base64_string)
    with open(output_path, 'wb') as file:
        file.write(image_data)

# Сохранение изображения из base64 в файл для использования pyautogui
image_path = "share_button_temp.png"
save_image_from_base64(image_base64, image_path)

# Функция для проверки наличия кнопок окончания игры
def check_game_end(stop_event):
    while not stop_event.is_set():
        try:
            invite_button = pyautogui.locateOnScreen(image_path, confidence=0.8)
            if invite_button is not None:
                stop_event.set()
        except pyautogui.ImageNotFoundException:
            pass
        time.sleep(2)  # Проверяем наличие кнопок каждые 2 секунды

# Основная функция для обработки экрана и нажатия на объекты
def process_screen(color_bounds, roi_top_left, roi_bottom_right, min_size, max_size, stop_event):
    # Даем время игре полностью загрузиться и исчезнуть элементы предыдущего экрана
    time.sleep(1)
    while not stop_event.is_set():
        # Захват экрана в области ROI
        screenshot = pyautogui.screenshot(region=(
            roi_top_left[0], roi_top_left[1], roi_bottom_right[0] - roi_top_left[0],
            roi_bottom_right[1] - roi_top_left[1]))
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        detected_objects = detect_color_objects(frame, color_bounds)
        handle_detections(detected_objects, roi_top_left, min_size, max_size)

    print("Игра завершена.")

def find_game_window(title="Telegram"):
    # Ищем окно по его заголовку
    windows = gw.getWindowsWithTitle(title)
    if windows:
        return windows[0]  # Возвращаем первое найденное окно
    return None

def close_window(root, decision=None):
    root.decision = decision
    root.quit()  # Останавливает главный цикл окна

def ask_to_continue(root):
    root.decision = None  # Обнуляем решение пользователя
    # Показываем окно снова
    root.deiconify()

    # Закрыть окно через 5 секунд, если на него не нажали
    root.after(5000, lambda: close_window(root, "continue"))

def start_game():
    color_bounds = {
        'green': (np.array([35, 100, 100]), np.array([85, 255, 255])),
        'snowflake': (np.array([90, 50, 50]), np.array([130, 255, 255])),
        'bomb': (np.array([0, 0, 50]), np.array([180, 50, 200]))
    }

    # Найти окно игры
    window = find_game_window("Telegram")
    if not window:
        print("Окно игры не найдено!")
        return

    window_width = 468
    window_height = 325

    # Вычислить область окна с игрой
    window_area_top_left, window_area_bottom_right = calculate_window_area(window)

    # центр куда перемещаем курсор
    center_x = (window_area_top_left[0] + window_area_bottom_right[0]) // 2
    center_y = (window_area_top_left[1] + window_area_bottom_right[1]) // 2

    # Вычисление ROI, по которой будут происходить клики
    roi_top_left, roi_bottom_right = calculate_roi(window_width, window_height, center_x, center_y)

    min_size = (30, 30)
    max_size = (200, 200)

    # Координаты начальной кнопки 'play'
    play_button_x = center_x + 143
    play_button_y = center_y + 110

    # Координаты кнопки 'play' для продолжения игры
    continue_play_button_x = center_x
    continue_play_button_y = center_y + 292

    game_counter_flag = 1

    # Количество скролл-единиц (для скролла вниз)
    scroll_units = -200
    pyautogui.moveTo(center_x, center_y)
    pyautogui.scroll(scroll_units)
    time.sleep(1)

    # Создаем главное окно один раз
    root = tk.Tk()
    root.title("Продолжить игру?")
    root.decision = None  # Флаг решения пользователя

    # Добавляем текстовое сообщение
    message_label = tk.Label(root, text="Скрипт автоматически продолжится в течение 5 секунд.\nДля отмены нажмите 'End game'")
    message_label.pack(pady=20)

    end_button = tk.Button(root, text="End game", command=lambda: close_window(root, "end"))
    end_button.pack(pady=20)

    # Скрываем окно в начале, пока оно не нужно
    root.withdraw()

    while True:
        stop_event = threading.Event()
        check_thread = threading.Thread(target=check_game_end, args=(stop_event,))
        check_thread.start()

        if game_counter_flag:
            print("Нажатие на кнопку 'play'...")
            pyautogui.click(play_button_x, play_button_y)
            game_counter_flag = 0
            time.sleep(1)

        process_screen(color_bounds, roi_top_left, roi_bottom_right, min_size, max_size, stop_event)
        stop_event.set()
        check_thread.join()

        # Показываем окно и ожидаем решение
        ask_to_continue(root)

        # Запускаем главный цикл окна, он завершится после нажатия кнопки или через 5 секунд
        root.mainloop()

        # Проверяем решение пользователя после закрытия окна
        if root.decision == "end":
            break  # Если выбрано "Закончить", выходим из цикла и завершаем игру
        else:
            print("Нажатие на кнопку продолжения игры...")
            pyautogui.click(continue_play_button_x, continue_play_button_y)
            time.sleep(1)

    # После завершения игры закрываем окно полностью
    root.destroy()
    messagebox.showinfo("Игра завершена", "Игра завершена. Вы можете закрыть окно.")

def create_gui():
    root = tk.Tk()
    root.title("Blum script")

    message_label = tk.Label(root, text="Для начала игры нажмите 'Start Game'")
    message_label.pack(pady=20)

    start_button = tk.Button(root, text="Start Game", command=start_game)
    start_button.pack(pady=40)

    root.mainloop()

if __name__ == '__main__':
    create_gui()