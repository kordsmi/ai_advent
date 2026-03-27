"""
🔥День 4. Температура

Выполните один и тот же запрос с параметрами:
👉 temperature = 0
👉 temperature = 0.7
👉 temperature = 1.2

Сравните ответы по:
👉 точности
👉 креативности
👉 разнообразию

Сформулируйте:
👉 для каких задач лучше подходит каждая настройка

Результат:
Примеры ответов с разной температурой и выводы по их использованию
"""

import rich
from gigachat import GigaChat, MessagesRole
from rich.markdown import Markdown

import config


QUERY_PROMPT = 'Расскажи в двух предложениях о том, как можно человеку попасть на луну?'


if __name__ == '__main__':
    console = rich.console.Console()

    giga = GigaChat(
        credentials=config.GIGACHAT_API_KEY,
        scope=config.GIGACHAT_SCOPE,
        model=config.GIGACHAT_MODEL,
        ca_bundle_file=config.CERTIFICATE_PATH,
    )

    print(QUERY_PROMPT, '\n\n')

    temperature_values = (0, 0.7, 1.2)
    for i, temperature in enumerate(temperature_values):
        print(f'{i}. temperature={temperature}\t\t')
        print('-' * 20)
        messages = [
            {'role': MessagesRole.USER, 'content': QUERY_PROMPT},
        ]
        response = giga.chat(payload={'messages': messages, 'temperature': temperature})
        console.print(Markdown(response.choices[0].message.content), '\n\n')
