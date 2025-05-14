import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os

# Файл для хранения аккаунтов
ACCOUNTS_FILE = 'accounts.json'


# Загружаем аккаунты из файла
def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r') as file:
            return json.load(file)
    return {}


# Сохраняем аккаунты в файл
def save_accounts(accounts):
    with open(ACCOUNTS_FILE, 'w') as file:
        json.dump(accounts, file)


# Главный класс приложения
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Language Learning App")

        # Храним аккаунты
        self.accounts = load_accounts()
        self.current_user = None

        # Первоначальные элементы интерфейса
        self.start_screen()

    def start_screen(self):
        self.clear_screen()

        self.title_label = tk.Label(self.root, text="Добро пожаловать!", font=("Arial black", 18))
        self.title_label.pack(pady=400)

        self.register_button = tk.Button(self.root, text="Зарегистрироваться", command=self.register, width=20,
                                         bg='lightblue', borderwidth=22, relief='raised')
        self.register_button.pack(pady=8)

        self.login_button = tk.Button(self.root, text="Войти", command=self.login, width=20, bg='lightgreen',
                                      borderwidth=22, relief='raised')
        self.login_button.pack(pady=5)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def register(self):
        username = simpledialog.askstring("Регистрация", "Введите имя пользователя:")
        password = simpledialog.askstring("Регистрация", "Введите пароль:", show='*')

        if username and password:
            self.accounts[username] = password
            save_accounts(self.accounts)
            messagebox.showinfo("Успех", "Вы успешно зарегистрировались!")
        else:
            messagebox.showwarning("Предупреждение", "Имя пользователя и пароль не могут быть пустыми.")

    def login(self):
        username = simpledialog.askstring("Вход", "Введите имя пользователя:")
        password = simpledialog.askstring("Вход", "Введите пароль:", show='*')

        if username in self.accounts and self.accounts[username] == password:
            self.current_user = username
            messagebox.showinfo("Успех", "Вы вошли в свою учетную запись!")
            self.main_menu()
        else:
            messagebox.showwarning("Ошибка", "Неправильное имя пользователя или пароль.")

    def main_menu(self):
        self.clear_screen()

        self.menu_label = tk.Label(self.root, text="Главное меню", font=("Arial black", 18))
        self.menu_label.pack(pady=400)

        self.lesson_button = tk.Button(self.root, text="Начать новый урок", command=self.select_level, width=20,
                                       bg='lightblue', borderwidth=11, relief='raised')
        self.lesson_button.pack(pady=8)

        self.settings_button = tk.Button(self.root, text="Настройки", command=self.settings, width=20, bg='lightgreen',
                                         borderwidth=11, relief='raised')
        self.settings_button.pack(pady=5)

    def settings(self):
        self.clear_screen()

        self.settings_label = tk.Label(self.root, text="Настройки", font=("Arial black", 24))
        self.settings_label.pack(pady=400)

        self.font_size_button = tk.Button(self.root, text="Изменить размер шрифта", command=self.set_font_size,
                                          width=26, bg='lightblue', borderwidth=20, relief='raised')
        self.font_size_button.pack(pady=5)

        self.color_settings_button = tk.Button(self.root, text="Изменить цвет интерфейса", command=self.set_color,
                                               width=26, bg='lightgreen', borderwidth=20, relief='raised')
        self.color_settings_button.pack(pady=5)

        self.button_color_button = tk.Button(self.root, text="Изменить цвет кнопок", command=self.set_button_color,
                                             width=26, bg='lightyellow', borderwidth=20, relief='raised')
        self.button_color_button.pack(pady=20)

        self.back_button = tk.Button(self.root, text="Назад", command=self.main_menu, width=20, bg='lightcoral',
                                     borderwidth=16, relief='raised')
        self.back_button.pack(pady=5)

    def set_font_size(self):
        size = simpledialog.askinteger("Размер шрифта", "Введите размер шрифта:")
        if size:
            self.root.option_add("*Font", f"Arial {size}")
            messagebox.showinfo("Успех", "Размер шрифта изменен!")

    def set_color(self):
        color = simpledialog.askstring("Цвет интерфейса", "Введите цвет (например, 'red', '#FF5733'):")
        if color:
            self.root.configure(bg=color)
            messagebox.showinfo("Успех", "Цвет интерфейса изменен!")

    def set_button_color(self):
        color = simpledialog.askstring("Цвет кнопок", "Введите цвет кнопок (например, 'blue', '#5733FF'):")
        if color:
            for button in self.root.winfo_children():
                if isinstance(button, tk.Button):
                    button.configure(bg=color)
            messagebox.showinfo("Успех", "Цвет кнопок изменен!")

    def select_level(self):
        self.clear_screen()

        self.level_label = tk.Label(self.root, text="ваш уровень английского", font=("Arial black", 15))
        self.level_label.pack(pady=400)


        self.beginner_button = tk.Button(self.root, text="Только начинаю",
                                         command=lambda: self.start_lesson("Только начинаю"), width=26, bg='lightblue',
                                         borderwidth=20, relief='raised')
        self.beginner_button.pack(pady=5)

        self.intermediate_button = tk.Button(self.root, text=" составляю простые предложения",
                                             command=lambda: self.start_lesson("Могу составлять простые предложения"),
                                             width=26, bg='lightgreen', borderwidth=20, relief='raised')
        self.intermediate_button.pack(pady=5)

        self.advanced_button = tk.Button(self.root, text="Могу быть переводчиком",
                                         command=lambda: self.start_lesson("Могу быть переводчиком"), width=26,
                                         bg='lightyellow', borderwidth=20, relief='raised')
        self.advanced_button.pack(pady=20)

        self.back_button = tk.Button(self.root, text="Назад", command=self.main_menu, width=20, bg='lightcoral',
                                     borderwidth=16, relief='raised')
        self.back_button.pack(pady=5)

    def start_lesson(self, level):
        messagebox.showinfo("Урок", f"Вы выбрали уровень: {level}")
        self.main_menu()


# Создание приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.geometry("720x1280")
    root.mainloop()
