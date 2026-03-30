"""
🔥 День 8. Работа с токенами

Добавьте в код агента подсчёт токенов:
👉 для текущего запроса
👉 для всей истории диалога
👉 для ответа модели

Сравните:

👉 короткий диалог
👉 длинный диалог
👉 диалог, который превышает лимит модели

Покажите:

👉 как растёт стоимость/токены по мере диалога
👉 что ломается при переполнении

Результат:

Код, который считает токены и показывает, как они влияют на поведение агента
"""

import rich
from gigachat import GigaChat, MessagesRole
from rich.markdown import Markdown

import config


class SimpleAgent:
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

    def send_query(self, user_query: str) -> str:
        """Отправляет запрос к LLM с сохранением контекста и возвращает ответ"""
        # Добавляем пользовательский запрос в контекст
        self.messages.append({'role': MessagesRole.USER, 'content': user_query})
        
        # Отправляем полный контекст диалога
        response = self.giga.chat(payload={'messages': self.messages})
        
        # Извлекаем информацию о токенах
        usage = response.usage
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens
        precached_tokens = usage.precached_prompt_tokens

        # Показываем статистику по токенам
        self.console.print(f"[bold cyan]Статистика токенов:[/bold cyan]")
        self.console.print(f"- Токены запроса: {prompt_tokens}")
        self.console.print(f"- Токены ответа: {completion_tokens}")
        self.console.print(f"- Всего токенов: {total_tokens}")
        if precached_tokens > 0:
            self.console.print(f"- Кэшированные токены: {precached_tokens}")
        
        # Общее количество токенов в истории диалога
        self.console.print(f"- Общее количество токенов в истории: {prompt_tokens + precached_tokens}")
        
        # Сохраняем ответ агента в контекст
        agent_response = response.choices[0].message
        self.messages.append({'role': agent_response.role, 'content': agent_response.content})
        
        # Сохраняем обновленный контекст в файл
        self.save_history()
        
        return agent_response.content
    
    def run(self):
        """Запускает агента и обрабатывает пользовательские запросы"""
        self.load_history()
        if self.messages:
            context_size = len(self.messages)
            self.console.print(f"[bold yellow]Загружено {context_size} сообщений из истории диалога.[/bold yellow]")
            
        user_prompt = 'Агент запущен. Введите ваш запрос (или "выход/exit" для завершения):'
        self.console.print(f'[bold green]{user_prompt}[/bold green]')
        
        while True:
            user_input = input("\nВаш запрос: ")
            
            if user_input.lower() in ['выход', 'exit', 'quit']:
                self.console.print("[bold red]Работа агента завершена.[/bold red]")
                break
                
            try:
                response = self.send_query(user_input)
                self.console.print("\n[bold blue]Ответ агента:[/bold blue]")
                self.console.print(Markdown(response))
            except Exception as e:
                self.console.print(f"[bold red]Ошибка при обращении к LLM: {e}[/bold red]")
                raise


    def load_history(self):
        """Загружает историю диалога из JSON-файла"""
        import os
        import json
        
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    raw_messages = json.load(f)
                    # Оставляем только поля role и content
                    self.messages = [
                        {'role': msg['role'], 'content': msg['content']} 
                        for msg in raw_messages 
                        if 'role' in msg and 'content' in msg
                    ]
                self.console.print(f"[bold green]История диалога загружена из {self.history_file}[/bold green]")
            except Exception as e:
                self.console.print(f"[bold red]Ошибка при загрузке истории: {e}[/bold red]")
                self.messages = []
        else:
            self.console.print("[bold blue]История диалога не найдена. Начинаем новый диалог.[/bold blue]")
            self.messages = []

    def save_history(self):
        """Сохраняет историю диалога в JSON-файл, оставляя только поля role и content"""
        import json
        
        try:
            # Фильтруем сообщения, оставляя только нужные поля
            filtered_messages = [
                {'role': msg['role'], 'content': msg['content']} 
                for msg in self.messages 
                if 'role' in msg and 'content' in msg
            ]
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_messages, f, ensure_ascii=False, indent=2)
            self.console.print(f"[bold green]История диалога сохранена в {self.history_file}[/bold green]", end="\r")
        except Exception as e:
            self.console.print(f"[bold red]Ошибка при сохранении истории: {e}[/bold red]")


if __name__ == '__main__':
    agent = SimpleAgent()
    agent.run()
