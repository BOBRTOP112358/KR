import tkinter as tk
from tkinter import messagebox
import random

# Список для хранения зарегистрированных пользователей
users = []


def register():
    username = entry_username.get()
    password = entry_password.get()

    if username and password:
        # Проверяем, существует ли уже пользователь
        for user in users:
            if user['username'] == username:
                messagebox.showwarning("Ошибка", "Пользователь с таким именем уже существует.")
                return

        # Сохраняем данные пользователя в список
        users.append({'username': username, 'password': password})
        messagebox.showinfo("Успех", "Регистрация прошла успешно!")
        entry_username.delete(0, tk.END)
        entry_password.delete(0, tk.END)
    else:
        messagebox.showwarning("Ошибка", "Пожалуйста, заполните все поля.")


def login():
    username = entry_username.get()
    password = entry_password.get()

    if username and password:
        # Проверяем, существует ли пользователь и совпадает ли пароль
        for user in users:
            if user['username'] == username and user['password'] == password:
                messagebox.showinfo("Успех", "Вход выполнен успешно!")
                entry_username.delete(0, tk.END)
                entry_password.delete(0, tk.END)

                # Скрываем интерфейс регистрации и входа
                hide_login_interface()

                # Отображаем имя пользователя и запускаем конфетти
                show_welcome(username)
                return

        messagebox.showwarning("Ошибка", "Неверное имя пользователя или пароль.")
    else:
        messagebox.showwarning("Ошибка", "Пожалуйста, заполните все поля.")


def hide_login_interface():
    label_username.pack_forget()
    entry_username.pack_forget()
    label_password.pack_forget()
    entry_password.pack_forget()
    button_register.pack_forget()
    button_login.pack_forget()


def show_welcome(username):
    welcome_label = tk.Label(root, text=f"Добро пожаловать, {username}!", font=("Helvetica", 16))
    welcome_label.pack(pady=20)

    # Запускаем анимацию конфетти
    create_confetti()


def create_confetti():
    for _ in range(100):  # Количество конфетти
        x = random.randint(0, root.winfo_width())
        y = random.randint(0, root.winfo_height())
        confetti = tk.Label(root, text="🎉", font=("Helvetica", random.randint(10, 30)))
        confetti.place(x=x, y=y)
        confetti.after(random.randint(1000, 3000), confetti.destroy)  # Удаляем конфетти через 1-3 секунды


# Создаем главное окно
root = tk.Tk()
root.title("Регистрация и Вход")
root.geometry("400x400")  # Устанавливаем размер окна

# Создаем метки и поля ввода
label_username = tk.Label(root, text="Имя пользователя:")
label_username.pack()

entry_username = tk.Entry(root)
entry_username.pack()

label_password = tk.Label(root, text="Пароль:")
label_password.pack()

entry_password = tk.Entry(root, show='*')
entry_password.pack()

# Создаем кнопки регистрации и входа
button_register = tk.Button(root, text="Зарегистрироваться", command=register)
button_register.pack(pady=10)

button_login = tk.Button(root, text="Войти", command=login)
button_login.pack(pady=10)

# Запускаем главный цикл
root.mainloop()
