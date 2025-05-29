import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import os
from tkinter import font

class InpaintingApp:
    """
    Клас, що представляє графічний інтерфейс користувача для програми відновлення зображень.
    Дозволяє завантажувати, відновлювати та зберігати зображення.
    """

    def create_custom_button_with_overlay_text(self, parent, image_paths, text_image_path, command):
        """
        Створює кастомну кнопку зі зображенням-текстом зверху.
        Кнопка має різні стани (звичайний, наведення, натиснутий).
        """
        # Завантажуємо зображення для різних станів кнопки
        normal = ImageTk.PhotoImage(Image.open(image_paths['normal']).resize((232, 72)))
        hover = ImageTk.PhotoImage(Image.open(image_paths['hover']).resize((232, 72)))
        pressed = ImageTk.PhotoImage(Image.open(image_paths['pressed']).resize((232, 72)))
        # Завантажуємо зображення з текстом, яке буде накладено на кнопку
        text_img = ImageTk.PhotoImage(Image.open(text_image_path).resize((232, 72)))

        # Створюємо Canvas для розміщення зображень кнопки
        canvas = tk.Canvas(parent, width=232, height=72, highlightthickness=0, bd=0)
        # Зберігаємо посилання на зображення, щоб вони не були видалені з пам'яті
        canvas.image_normal = normal
        canvas.image_hover = hover
        canvas.image_pressed = pressed
        canvas.text_img = text_img

        # Створюємо фонове зображення кнопки (спочатку в нормальному стані)
        bg_image = canvas.create_image(0, 0, anchor="nw", image=normal)
        # Накладаємо зображення з текстом поверх фону
        text_overlay = canvas.create_image(0, 0, anchor="nw", image=text_img)

        # Функції для обробки подій миші
        def on_enter(e):
            # Змінюємо зображення кнопки на стан "наведення"
            canvas.itemconfig(bg_image, image=canvas.image_hover)
        def on_leave(e):
            # Змінюємо зображення кнопки на нормальний стан
            canvas.itemconfig(bg_image, image=canvas.image_normal)
        def on_press(e):
            # Змінюємо зображення кнопки на стан "натиснуто"
            canvas.itemconfig(bg_image, image=canvas.image_pressed)
        def on_release(e):
            # Повертаємо кнопку до стану "наведення" після відпускання
            canvas.itemconfig(bg_image, image=canvas.image_hover)
            # Викликаємо функцію, пов'язану з кнопкою
            command()

        # Прив'язуємо події миші до Canvas
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<ButtonRelease-1>", on_release)

        # Розміщуємо Canvas на вікні
        canvas.pack(pady=5)


    def __init__(self, root):
        """
        Ініціалізує головне вікно програми та її компоненти.
        """
        # Створюємо Canvas для відображення зображень
        self.canvas = tk.Canvas(root, width=160, height=160)
        self.canvas.pack(pady=20)
        
        # Завантажуємо фонове зображення та рамку для Canvas
        self.bg_img = ImageTk.PhotoImage(Image.open("assets/Background_Image.png").resize((160, 160)))
        self.frame_img = ImageTk.PhotoImage(Image.open("assets/Frame.png").resize((160, 160)))

        # Створюємо фонове зображення на Canvas
        self.bg_item = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_img)
        self.image_item = None # Змінна для поточного відображуваного зображення

        # Створюємо рамку, яка буде накладена поверх зображення
        self.frame_item = self.canvas.create_image(0, 0, anchor="nw", image=self.frame_img)

        self.root = root
        self.root.title("Реставратор зображень 64*64") # Заголовок вікна
        self.root.geometry("350x470") # Розмір вікна
        self.root.resizable(False, False) # Забороняємо зміну розміру вікна

        self.image_path = None # Шлях до завантаженого зображення
        self.restored_path = "temp_restored.jpg" # Тимчасовий шлях для збереження відновленого зображення
        self.restored_img = None # Об'єкт PIL зображення для відновленого зображення

        # Фрейм для кнопок
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        # Створення кнопок за допомогою кастомної функції
        self.create_custom_button_with_overlay_text(
            self.button_frame,
            {
                'normal': "assets/Button.png",
                'hover': "assets/Choosen_Button.png",
                'pressed': "assets/Clicked_Button.png"
            },
            "assets/loadtext.png",
            self.load_image # Функція, яка буде викликана при натисканні
        )

        self.create_custom_button_with_overlay_text(
            self.button_frame,
            {
                'normal': "assets/Button.png",
                'hover': "assets/Choosen_Button.png",
                'pressed': "assets/Clicked_Button.png"
            },
            "assets/restoretext.png",
            self.restore_image # Функція для відновлення зображення
        )

        self.create_custom_button_with_overlay_text(
            self.button_frame,
            {
                'normal': "assets/Button.png",
                'hover': "assets/Choosen_Button.png",
                'pressed': "assets/Clicked_Button.png"
            },
            "assets/savetext.png",
            self.save_restored # Функція для збереження відновленого зображення
        )


    def load_image(self):
        """
        Відкриває діалогове вікно для вибору зображення та відображає його.
        """
        # Відкриваємо діалог вибору файлу, дозволяючи лише файли зображень
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if not file_path:
            return # Якщо файл не вибрано, виходимо
        self.image_path = file_path # Зберігаємо шлях до вибраного зображення
        self.show_image(file_path) # Відображаємо зображення на Canvas

    def restore_image(self):
        """
        Викликає скрипт відновлення зображення та відображає результат.
        """
        if not self.image_path:
            messagebox.showerror("Помилка", "Будь ласка, спочатку оберіть зображення.")
            return

        try:
            # Запускаємо зовнішній скрипт restore.py, передаючи йому шляхи
            # до вхідного та вихідного зображень. check=True викликає виняток, якщо процес завершився з помилкою.
            subprocess.run(["python", "restore.py", self.image_path, self.restored_path], check=True)
        except subprocess.CalledProcessError:
            messagebox.showerror("Помилка", "Не вдалося відновити зображення. Переконайтеся, що модель навчена та 'restore.py' працює коректно.")
            return

        # Перевіряємо, чи був створений відновлений файл
        if os.path.exists(self.restored_path):
            self.restored_img = Image.open(self.restored_path) # Відкриваємо відновлене зображення
            self.show_image(self.restored_path) # Відображаємо відновлене зображення
        else:
            messagebox.showerror("Помилка", "Відновлений файл не знайдено.")

    def save_restored(self):
        """
        Зберігає відновлене зображення у вибране користувачем місце.
        """
        if self.restored_img is None:
            messagebox.showerror("Помилка", "Спочатку відновіть зображення.")
            return

        # Відкриваємо діалог збереження файлу
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                 filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
        if file_path:
            self.restored_img.save(file_path) # Зберігаємо зображення
            messagebox.showinfo("Готово", f"Зображення збережено:\n{file_path}")

    def show_image(self, path):
        """
        Відображає зображення на Canvas.
        """
        # Відкриваємо зображення та змінюємо його розмір до 64x64 (розмір, який обробляє модель)
        img = Image.open(path).resize((64, 64))
        
        # Якщо відображається відновлене зображення, зберігаємо його копію
        if path == self.restored_path:
            self.restored_img = img.copy()

        # Змінюємо розмір зображення для відображення на Canvas (збільшуємо для кращого перегляду)
        preview_img = img.resize((128, 128), Image.NEAREST) # Використовуємо Image.NEAREST для збереження пікселів
        self.tk_img = ImageTk.PhotoImage(preview_img)

        # Центруємо зображення всередині 160x160 області Canvas
        x_offset = (160 - 128) // 2
        y_offset = (160 - 128) // 2

        # Оновлюємо або створюємо об'єкт зображення на Canvas
        if self.image_item:
            self.canvas.itemconfig(self.image_item, image=self.tk_img)
        else:
            self.image_item = self.canvas.create_image(x_offset, y_offset, anchor="nw", image=self.tk_img)

        # Переміщуємо рамку наверх, щоб вона завжди була поверх зображення
        self.canvas.tag_raise(self.frame_item)

# Запуск GUI
if __name__ == "__main__":
    root = tk.Tk() # Створюємо головне вікно Tkinter
    app = InpaintingApp(root) # Створюємо екземпляр нашої програми
    root.mainloop() # Запускаємо цикл подій Tkinter

