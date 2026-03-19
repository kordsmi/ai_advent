"""
🔥 День 1. Первый запрос к LLM через API

Напишите минимальный код, который:
👉 отправляет запрос в LLM через API
👉 получает ответ
👉 выводит его в консоль или простой интерфейс (CLI / Web)

Результат:
Код, который отправляет запрос в LLM через API и получает ответ
"""

from gigachat import GigaChat

import config


if __name__ == '__main__':
    giga = GigaChat(
        credentials=config.GIGACHAT_API_KEY,
        scope=config.GIGACHAT_SCOPE,
        model=config.GIGACHAT_MODEL,
        ca_bundle_file=config.CERTIFICATE_PATH,
    )

    user_message = input("Введите запрос для LLM GigaChat:\t")
    response = giga.chat(payload=user_message)
    print(response.choices[0].message.content)
    print(f'\nPrompt tokens: {response.usage.prompt_tokens}, completion token:{response.usage.completion_tokens}, '
          f'total tokens: {response.usage.total_tokens}, cached tokens: {response.usage.precached_prompt_tokens}')
