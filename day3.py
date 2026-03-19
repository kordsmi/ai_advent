"""
🔥 День 3. Разные способы рассуждения

Возьмите одну задачу
(логическую, алгоритмическую или аналитическую)

Решите её через API четырьмя способами:
👉 получите прямой ответ без дополнительных инструкций
👉 добавьте в промпт инструкцию: «решай пошагово»
👉 попросите модель сначала составить промпт для решения задачи, а затем используйте его
👉 создайте в промпте группу экспертов (например: аналитик, инженер, критик) и получите решение от каждого

Сравните:
👉 отличаются ли ответы
👉 какой способ дал наиболее точный результат

Результат:
Несколько решений одной задачи и их сравнение
"""

import rich
from gigachat import GigaChat, MessagesRole
from rich.markdown import Markdown

import config


QUERY_PROMPT = ('Рыцари всегда говорят только правду. Лжецы всегда говорят только ложь. '
                'На острове рыцарей и лжецов собралась компания из 12 человек. Каждый человек заявил всем остальным: '
                '"Вы все лжецы!". Сколько лжецов может быть в этой компании?')


if __name__ == '__main__':
    console = rich.console.Console()

    giga = GigaChat(
        credentials=config.GIGACHAT_API_KEY,
        scope=config.GIGACHAT_SCOPE,
        model=config.GIGACHAT_MODEL,
        ca_bundle_file=config.CERTIFICATE_PATH,
    )

    print(f'Задача: {QUERY_PROMPT}\n\n')

    print('1. Ответ без дополнительных инструкций')
    print('--------------------------------------')
    response = giga.chat(payload=QUERY_PROMPT)
    console.print(Markdown(response.choices[0].message.content), '\n\n')

    print('2. Пошаговое решение')
    print('--------------------')
    response = giga.chat(payload=f'Реши задачу пошагово: {QUERY_PROMPT}')
    console.print(Markdown(response.choices[0].message.content))

    print('3. Решение задачи через предложенный промпт.')
    print('--------------------------------------------')
    response = giga.chat(payload=f'Составь промпт для решения задачи: {QUERY_PROMPT}')
    console.print(Markdown(response.choices[0].message.content), '\n\n')
    response = giga.chat(payload=response.choices[0].message.content)
    print('-' * 50)
    console.print(Markdown(response.choices[0].message.content), '\n\n')

    print('4. Решение задачи от разных экспертов.')
    print('--------------------------------------')
    experts_prompt_list = {
        'Аналитик': 'Ты аналитик, твои ответы должны быть чётко сформулированными',
        'Физик': 'Ты учёный-физик. Твои ответы должны быть лаконичными, но математически верны',
        'Школьник': 'Ты ученик первого класса. У тебя минимум рассуждений и достаточно быстрые ответы',
    }
    for expert_name, expert_prompt in experts_prompt_list.items():
        print(f'{expert_name}:')
        print('-' * (len(expert_name) + 1))
        messages = [
            {'role': MessagesRole.SYSTEM, 'content': expert_prompt},
            {'role': MessagesRole.USER, 'content': QUERY_PROMPT},
        ]
        response = giga.chat(payload={'messages': messages})
        console.print(Markdown(response.choices[0].message.content), '\n\n')
