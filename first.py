import logging
import tkinter as tk
from tkinter import scrolledtext, messagebox

from gigachat import GigaChat, Chat, Messages, MessagesRole


logger = logging.getLogger(__name__)


giga = GigaChat(
    credentials='MDE5Y2Y3OWEtOWE1OS03YWJkLWI4YmItODZkMTgwNTMwNWYxOmU3ODAzNGFlLTJmOGYtNGRjZi04YmFlLTE2YjNiMWE2NjI0Ng==',
    scope='GIGACHAT_API_PERS',
    model='GigaChat-2-Pro',
    ca_bundle_file='/usr/local/share/ca-certificates/russian_trusted_root_ca_pem.crt',
)

class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Настройки окна
        self.title("GigaChat Dialog")
        self.geometry("800x600")

        # Блок системного промпта
        self.system_prompt_label = tk.Label(self, text="Системный промпт:")
        self.system_prompt_label.pack()
        self.system_prompt_entry = tk.Entry(self, width=50)
        self.system_prompt_entry.pack(pady=(0, 10))

        # Окно диалога
        self.dialog_text = scrolledtext.ScrolledText(self, wrap='word', height=20, width=70)
        self.dialog_text.pack(pady=(0, 10))

        # Блок пользовательского ввода
        self.user_input_label = tk.Label(self, text="Ваше сообщение:")
        self.user_input_label.pack()
        self.user_input_entry = tk.Entry(self, width=50)
        self.user_input_entry.pack(pady=(0, 10))

        # Кнопки
        self.send_button = tk.Button(self, text="Отправить", command=self.send_message)
        self.clear_session_button = tk.Button(self, text="Очистить сессию", command=self.clear_session)
        self.send_button.pack(side=tk.LEFT, padx=(0, 10))
        self.clear_session_button.pack(side=tk.RIGHT)

        # Инициализация переменных состояния
        self.is_new_session = True

        self.chat = Chat(messages=[])

    def send_message(self):
        """Отправка нового сообщения"""
        if not self.user_input_entry.get().strip():
            return

        new_user_prompt = self.user_input_entry.get().strip()

        # Формируем системный запрос, если новая сессия
        if self.is_new_session:
            system_prompt = self.system_prompt_entry.get().strip()
            if not system_prompt:
                messagebox.showerror("Ошибка", "Пожалуйста, введите системный промпт перед началом разговора.")
                return

            self.chat.messages.append(Messages(role=MessagesRole.SYSTEM, content=system_prompt))
            self.is_new_session = False

        # Добавляем новое сообщение от пользователя
        self.chat.messages.append(Messages(role=MessagesRole.USER, content=new_user_prompt))

        # Отображаем сообщение пользователя
        self.display_message(new_user_prompt, role="user")

        # Отправляем запрос в GigaChat
        try:
            response = giga.chat(self.chat)
            assistant_message = response.choices[0].message

            # Сохраняем ответ ассистента
            self.chat.messages.append(assistant_message)

            # Отображаем ответ ассистента
            self.display_message(assistant_message.content, role="assistant")

        except Exception as e:
            print(self.chat)
            logging.exception(f"Error in chat completion request")
            messagebox.showerror("Ошибка", f"Произошла ошибка при общении с сервером:\n{e}")

        finally:
            # Очищаем поле ввода после отправки
            self.user_input_entry.delete(0, 'end')

    def display_message(self, content, role=None):
        """Отображение сообщения в окне диалога"""
        if role == "user":
            self.dialog_text.insert('end', f"Вы: {content}\n\n", "user")
        elif role == "assistant":
            self.dialog_text.insert('end', f"Ассистент: {content}\n\n", "assistant")
        else:
            self.dialog_text.insert('end', f"{content}\n\n")

        # Выделяем цвета разным ролям
        self.dialog_text.tag_configure("user", foreground="blue")
        self.dialog_text.tag_configure("assistant", foreground="green")

    def clear_session(self):
        """Очистка всей информации о текущей сессии"""
        self.system_prompt_entry.config(state='normal')  # Разрешаем редактировать системный промпт снова
        self.system_prompt_entry.delete(0, 'end')
        self.dialog_text.delete('1.0', 'end')
        self.chat.messages = []
        self.is_new_session = True


if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()
