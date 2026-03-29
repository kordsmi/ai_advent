"""
🔥 День 6. Первый агент

Реализуйте простого агента, который:
👉 принимает запрос пользователя
👉 отправляет его в LLM через API
👉 получает ответ
👉 выводит результат в вашем интерфейсе

(простой чат, CLI или web, запросы через HTTP-клиент)

Важно:
👉 агент должен быть отдельной сущностью, а не просто один вызов API
👉 логика запроса и ответа должна быть инкапсулирована в агенте

Результат:
Агент принимает запрос и корректно вызывает LLM через API
"""

import rich
from gigachat import GigaChat, MessagesRole
from rich.markdown import Markdown

import config


class SimpleAgent:
    """Простой агент для взаимодействия с LLM через API"""
    
    def __init__(self):
        self.console = rich.console.Console()
        self.giga = GigaChat(
            credentials=config.GIGACHAT_API_KEY,
            scope=config.GIGACHAT_SCOPE,
            model=config.GIGACHAT_MODEL,
            ca_bundle_file=config.CERTIFICATE_PATH,
        )
        self.messages = []
        
    def send_query(self, user_query: str) -> str:
        """Отправляет запрос к LLM с сохранением контекста и возвращает ответ"""
        # Добавляем пользовательский запрос в контекст
        self.messages.append({'role': MessagesRole.USER, 'content': user_query})
        
        # Отправляем полный контекст диалога
        response = self.giga.chat(payload={'messages': self.messages})
        
        # Сохраняем ответ агента в контекст
        agent_response = response.choices[0].message
        self.messages.append(agent_response)
        
        return agent_response.content
    
    def run(self):
        """Запускает агента и обрабатывает пользовательские запросы"""
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


if __name__ == '__main__':
    agent = SimpleAgent()
    agent.run()
