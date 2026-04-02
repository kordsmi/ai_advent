"""
🔥 День 9. Управление контекстом: сжатие истории

Реализуйте механизм управления контекстом:

👉 храните последние N сообщений “как есть”
👉 остальное заменяйте summary (например каждые 10 сообщений)
👉 храните summary отдельно и подставляйте его в запрос вместо полной истории

Сравните:

👉 качество ответов без сжатия
👉 качество ответов со сжатием
👉 расход токенов до/после

Результат:

Агент, который работает с компрессией истории и экономит токены
"""
import json
import os

import rich
from gigachat import GigaChat, MessagesRole
from rich.markdown import Markdown

import config


class Agent:
    """Простой агент для взаимодействия с LLM через API"""
    
    def __init__(self, history_file="agent_history.json"):
        self.console = rich.console.Console()
        self.giga = GigaChat(
            credentials=config.GIGACHAT_API_KEY,
            scope=config.GIGACHAT_SCOPE,
            model=config.GIGACHAT_MODEL,
            ca_bundle_file=config.CERTIFICATE_PATH,
        )
        self.history_file = history_file
        self.messages = []
        self.system_prompt = ''
        self.summary = ''

    def send_query(self, user_query: str) -> str:
        """Отправляет запрос к LLM с сохранением контекста и возвращает ответ"""
        # Добавляем пользовательский запрос в контекст
        self.messages.append({'role': MessagesRole.USER, 'content': user_query})
        
        # Отправляем полный контекст диалога
        response = self.giga.chat(payload={'messages': self.messages})
        
        # Извлекаем информацию о токенах
        usage = response.usage
        self.show_token_usage(usage)

        # Сохраняем ответ агента в контекст
        agent_response = response.choices[0].message
        self.messages.append({'role': agent_response.role, 'content': agent_response.content})

        return agent_response.content

    def show_token_usage(self, usage):
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens
        precached_tokens = usage.precached_prompt_tokens

        # Показываем статистику по токенам
        self.console.print(f"[bold cyan]Статистика токенов[/bold cyan] На запрос: {prompt_tokens} "
                           f"На ответ: {completion_tokens} Всего: {total_tokens} Кэшированные : {precached_tokens} "
                           f"Общее количество в истории: {prompt_tokens + precached_tokens}")

    def run(self):
        """Запускает агента и обрабатывает пользовательские запросы"""
        self.load_history()
        self.create_system_prompt()

        if self.summary:
            self.console.print(Markdown(self.summary))

        user_prompt = 'Агент запущен. Введите ваш запрос (или "выход/exit" для завершения):'
        self.console.print(f'[bold green]{user_prompt}[/bold green]')

        if self.messages and self.messages[-1]['role'] == MessagesRole.ASSISTANT:
            self.print_assistant_message(self.messages[-1]['content'])

        while True:
            user_input = input("\nВаш запрос: ")
            
            if user_input.lower() in ['выход', 'exit', 'quit']:
                self.console.print("[bold red]Работа агента завершена.[/bold red]")
                break
                
            try:
                response = self.send_query(user_input)
                self.print_assistant_message(response)
                self.summarize_dialogue()
                # Сохраняем обновленный контекст в файл
                self.save_history()
            except Exception as e:
                self.console.print(f"[bold red]Ошибка при обращении к LLM: {e}[/bold red]")
                raise

    def print_assistant_message(self, message):
        self.console.print("\n[bold blue]Ответ агента:[/bold blue]")
        self.console.print(Markdown(message))

    def load_history(self):
        """Загружает историю диалога из JSON-файла"""
        if not os.path.exists(self.history_file):
            self.console.print("[bold blue]История диалога не найдена. Начинаем новый диалог.[/bold blue]")
            self.messages = []
            return

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.system_prompt = data.get('system_prompt', '')
            self.summary = data.get('summary', '')
            # Оставляем только поля role и content
            self.messages = [
                {'role': msg['role'], 'content': msg['content']}
                for msg in data.get('messages', [])
                if 'role' in msg and 'content' in msg
            ]
            self.console.print(f"[bold green]История диалога загружена из {self.history_file}[/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]Ошибка при загрузке истории: {e}[/bold red]")
            self.messages = []

        if self.messages:
            context_size = len(self.messages)
            self.console.print(f"[bold yellow]Загружено {context_size} сообщений из истории диалога.[/bold yellow]")

    def save_history(self):
        """Сохраняет историю диалога в JSON-файл, оставляя только поля role и content"""
        data = {
            'system_prompt': self.system_prompt,
            'summary': self.summary,
        }

        try:
            # Фильтруем сообщения, оставляя только нужные поля
            filtered_messages = [
                {'role': msg['role'], 'content': msg['content']} 
                for msg in self.messages 
                if 'role' in msg and 'content' in msg and msg['role'] in (MessagesRole.USER, MessagesRole.ASSISTANT)
            ]
            data['messages'] = filtered_messages
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.console.print(f"[bold green]История диалога сохранена в {self.history_file}[/bold green]", end="\r")
        except Exception as e:
            self.console.print(f"[bold red]Ошибка при сохранении истории: {e}[/bold red]")

    def create_system_prompt(self):
        system_prompt = f'{self.system_prompt}\n\n{self.summary}'
        self.messages = [
            message for message in self.messages if message['role'] != MessagesRole.SYSTEM
        ]
        self.messages.insert(0, {"role": MessagesRole.SYSTEM,"content": system_prompt})

    def summarize_dialogue(self):
        if len(self.messages) < 20:
            return True

        print('!')

        messages_history = self.messages[:10]
        messages_data = json.dumps(messages_history, ensure_ascii=False)

        system_prompt_text = ('Ты лингвист-аналитик. Твоя задача проанализировать диалог и вывести резюме, '
                              'которое будет использоваться как системный промпт. На вход получаешь JSON структуру. '
                              'На выходе должен быть готовый текст, содержащий информативную выдержку. '
                              'Результат должен представлять из себя системный промпт для LLM, который будет '
                              'передаваться в следующих запросах. '
                              'Обязательно нужно выделить конечную цель и ключевые '
                              'моменты диалога. Также нужно привести детали диалога по уже обсуждённым и утвержденным '
                              'темам. Также нужны договорённости, как мы работаем с тобой.'
                              'Ответ не должен содержать в себе информацию, что это резюме')
        messages = [
            {'role': MessagesRole.SYSTEM, 'content': system_prompt_text},
            {'role': MessagesRole.USER, 'content': messages_data},
        ]
        response = self.giga.chat(payload={'messages': messages})
        summary = response.choices[0].message.content
        messages.extend([
            response.choices[0].message,
            {'role': MessagesRole.USER, 'content': 'Является ли этот ответ точным на моё задание? '
                                                   'Ответь только да или нет'}
        ])
        response = self.giga.chat(payload={"messages": messages})
        answer: str = response.choices[0].message.content
        if answer.upper() == 'ДА':
            self.summary = summary
            self.messages = self.messages[10:]
            self.create_system_prompt()
            self.console.print(f"[bold pink]Промежуточная суммаризация:\n{summary}[/bold pink]")
            return True
        self.console.print(f"[bold green]Промежуточная суммаризация:\n{summary}[/bold green]")
        return False


if __name__ == '__main__':
    agent = Agent()
    agent.system_prompt = ('')
    agent.run()
