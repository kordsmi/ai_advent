"""
🔥 День 2. Формат ответа

Отправьте один и тот же запрос, но:
👉 добавьте явное описание формата ответа
👉 добавьте ограничение на длину ответа
👉 добавьте условие завершения ответа (stop sequence или явную инструкцию)

Сравните ответы:
👉 без ограничений
👉 с ограничениями

Результат:
Один и тот же запрос с разным уровнем контроля ответа через API
"""

from gigachat import GigaChat, MessagesRole

import config


QUERY_PROMPT = 'Для чего нужна астрономия?'

if __name__ == '__main__':
    giga = GigaChat(
        credentials=config.GIGACHAT_API_KEY,
        scope=config.GIGACHAT_SCOPE,
        model=config.GIGACHAT_MODEL,
        ca_bundle_file=config.CERTIFICATE_PATH,
    )

    print('Ответ по умолчанию:')
    print('-------------------')
    response = giga.chat(payload=QUERY_PROMPT)
    print(response.choices[0].message.content)

    # Явно описываем формат ответа
    print('\n\nОтвет в соответствии с описанным форматом:')
    print('------------------------------------------')
    system_prompt = ('Выведи только текст без форматирования. В первом абзаце приведи описание термина "Астрономия", '
                     'во втором абзаце её назначение')
    messages = [
        {'role': MessagesRole.SYSTEM, 'content': system_prompt},
        {'role': MessagesRole.USER,'content': QUERY_PROMPT},
    ]
    response = giga.chat(payload = {'messages': messages})
    print(response.choices[0].message.content)

    # Ограничиваем максимальную длинну текста
    print('\n\nОграниченный по длине ответ:')
    print('----------------------------')
    response = giga.chat(payload={'max_tokens': 20, 'messages': messages})
    print(response.choices[0].message.content)

    # Ограничиваем максимальную длинну текста
    print('\n\nУсловие завершения ответа:')
    print('--------------------------')
    user_prompt = (f'Выдай ответ, остановившись ровно на слове "Вселенная". Не продолжай предложение после этого слова '
                   f'ни при каких обстоятельствах. Используй именно это слово, как жесткое ограничение вывода.'
                   f' {QUERY_PROMPT}')
    response = giga.chat(payload=user_prompt)
    print(response.choices[0].message.content)
