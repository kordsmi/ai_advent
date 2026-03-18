import logging
import wx
import wx.richtext

from gigachat import GigaChat, Chat, Messages, MessagesRole


class ChatApp(wx.Frame):
    def __init__(self):
        super().__init__(None, title="GigaChat Dialog", size=(800, 600))
        
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Блок системного промпта
        self.system_prompt_label = wx.StaticText(self.panel, label="Системный промпт:")
        self.sizer.Add(self.system_prompt_label, 0, wx.EXPAND | wx.ALL, 5)
        
        self.system_prompt_entry = wx.TextCtrl(self.panel, size=(500, -1))
        self.sizer.Add(self.system_prompt_entry, 0, wx.EXPAND | wx.ALL, 5)
        
        # Окно диалога
        self.dialog_text = wx.richtext.RichTextCtrl(
            self.panel, 
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        )
        self.sizer.Add(self.dialog_text, 1, wx.EXPAND | wx.ALL, 5)
        
        # Блок пользовательского ввода
        self.user_input_label = wx.StaticText(self.panel, label="Ваше сообщение:")
        self.sizer.Add(self.user_input_label, 0, wx.EXPAND | wx.ALL, 5)
        
        self.user_input_entry = wx.TextCtrl(self.panel, size=(500, -1), style=wx.TE_PROCESS_ENTER)
        self.user_input_entry.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
        self.sizer.Add(self.user_input_entry, 0, wx.EXPAND | wx.ALL, 5)
        
        # Кнопки
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.send_button = wx.Button(self.panel, label="Отправить")
        self.send_button.Bind(wx.EVT_BUTTON, self.send_message)
        button_sizer.Add(self.send_button, 0, wx.ALL, 5)
        
        self.clear_session_button = wx.Button(self.panel, label="Очистить сессию")
        self.clear_session_button.Bind(wx.EVT_BUTTON, self.clear_session)
        button_sizer.Add(self.clear_session_button, 0, wx.ALL, 5)
        
        self.sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        
        self.panel.SetSizer(self.sizer)
        
        # Инициализация переменных состояния
        self.is_new_session = True
        self.chat = Chat(messages=[])
        
        self.Centre()
        self.Show()
        
    def on_enter(self, event):
        self.send_message(None)
        
    def send_message(self, event):
        """Отправка нового сообщения"""
        if not self.user_input_entry.GetValue().strip():
            return

        new_user_prompt = self.user_input_entry.GetValue().strip()

        # Формируем системный запрос, если новая сессия
        if self.is_new_session:
            system_prompt = self.system_prompt_entry.GetValue().strip()
            if not system_prompt:
                wx.MessageBox("Пожалуйста, введите системный промпт перед началом разговора.", "Ошибка", wx.OK | wx.ICON_ERROR)
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
            wx.MessageBox(f"Произошла ошибка при общении с сервером:\n{e}", "Ошибка", wx.OK | wx.ICON_ERROR)

        finally:
            # Очищаем поле ввода после отправки
            self.user_input_entry.SetValue("")

    def display_message(self, content, role=None):
        """Отображение сообщения в окне диалога"""
        if role == "user":
            self.dialog_text.BeginTextColour(wx.BLUE)
            self.dialog_text.WriteText(f"Вы: {content}\n\n")
        elif role == "assistant":
            self.dialog_text.BeginTextColour(wx.GREEN)
            self.dialog_text.WriteText(f"Ассистент: {content}\n\n")
        else:
            self.dialog_text.WriteText(f"{content}\n\n")
            
        self.dialog_text.EndTextColour()
        self.dialog_text.ShowPosition(self.dialog_text.GetLastPosition())

    def clear_session(self, event):
        """Очистка всей информации о текущей сессии"""
        self.system_prompt_entry.SetValue("")
        self.dialog_text.Clear()
        self.chat.messages = []
        self.is_new_session = True

giga = GigaChat(
    credentials='MDE5Y2Y3OWEtOWE1OS03YWJkLWI4YmItODZkMTgwNTMwNWYxOmU3ODAzNGFlLTJmOGYtNGRjZi04YmFlLTE2YjNiMWE2NjI0Ng==',
    scope='GIGACHAT_API_PERS',
    model='GigaChat-2',
    ca_bundle_file='/usr/local/share/ca-certificates/russian_trusted_root_ca_pem.crt',
)

if __name__ == "__main__":
    app = wx.App()
    frame = ChatApp()
    app.MainLoop()