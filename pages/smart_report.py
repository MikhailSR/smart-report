"""
Задача этого файла сформировать текстовое сообщение-отчет, по шаблону. Внутри содержится информация о суммах,
количестве проданных услуг, обороте и других метриках, которые расчитываются на основе csv файла. CSV файл
предварительно импортируется из Google Sheets, по одельному месяцу.
"""

import io
import streamlit as st
import csv
import pprint

from io import StringIO
from typing import TypedDict


class ServiceInfo(TypedDict):
    summa: float
    count: int
    details: list[str]


def format_number_with_spaces(number: int | float) -> str:
    """Возвращает отформатированное число: разделяет тысячные пробелом, заменят точку на запятую, удаляет незначимый ноль
        Например, число 1200, функция вернет "1 200"
    Args:
        number (int|float): число для форматирования

    Returns:
        str: строка с отформатированным числом
    """

    def delete_nonsignificant_zero(num: float):
        if num % 1 == 0:
            num = int(num)
        return num

    number = delete_nonsignificant_zero(number)

    # Разделяем целую и дробную части
    integer_part, *decimal_part = str(number).split(".")

    # Форматируем целую часть с пробелами
    formatted_integer_part = f"{int(integer_part):,}".replace(",", " ")

    # Собираем обратно с дробной частью, если она есть
    if decimal_part:
        return f"{formatted_integer_part},{decimal_part[0]}"
    else:
        return formatted_integer_part


def calculation_metrics(services: dict) -> dict:
    """Возвращает словарь расчитанных основных метрик

    Args:
        services (dict): словарь на основании которого общитываются метрики

    Returns:
        dict[str:float]: Ключи словаря - имена метрик. Занчения словаря - расчитанные значения
    """

    metrics: dict = {'revenue': 0.0,
                     'пошлина_перевод': 0.0,
                     'без_пошлин_переводов': 0.0,
                     'обмен_прав': 0.0,
                     'сита': 0.0,
                     'справка': 0.0,
                     'без_пошлин_переводов_сит_справок_обмена_прав': 0.0,
                     'без_пошлин_переводов_сит_справок_с_обменом_прав': 0.0}

    revenue: float = round(sum(item['summa'] for item in services.values()), 2)
    metrics['revenue'] = revenue

    poslina_and_perevod: float = round(
        sum(value['summa'] for key, value in services.items() if key in ('Пошлина', 'Перевод')),
        2)
    metrics['пошлина_перевод'] = poslina_and_perevod

    sita: dict | int = services.get('Сита', 0)
    if sita != 0:
        metrics['сита'] = sita['summa']

    spravka: dict | int = services.get('Справка', 0)
    if spravka != 0:
        metrics['справка'] = spravka['summa']

    obmen_prav: dict | int = services.get('Под ключ права обмен', 0)
    if obmen_prav != 0:
        metrics['обмен_прав'] = obmen_prav['summa']

    metrics['без_пошлин_переводов'] = revenue - poslina_and_perevod
    metrics[
        'без_пошлин_переводов_сит_справок_обмена_прав'] = round(
        revenue - poslina_and_perevod - metrics['сита'] - metrics['справка'] - metrics['обмен_прав'], 2)
    metrics['без_пошлин_переводов_сит_справок_с_обменом_прав'] = round(
        revenue - poslina_and_perevod - metrics['сита'] - metrics['справка'],
        2)

    return metrics


def generate_report_message(services: dict, metrics: dict) -> str:
    """Созвращает готовое report-сообщение

    Args:
        services (dict): словарь с данными для записи в отчет-файл
        metrics (dict): словарь расчитанных метрик для вывода

    Returns:
        (str): в случае успешной генерации сообщения
    """

    metrics = metrics.copy()
    # Форматирую числа для записи в файл
    for key, value in metrics.items():
        metrics[key] = format_number_with_spaces(value)

    result_message = ""
    result_message += f'Расчет\nОборот: {metrics["revenue"]} евро\n\n'
    result_message += f'🧡Без пошлин и переводов: {metrics["без_пошлин_переводов"]} евро\n\n'
    result_message += f'🩵Без пошлин, переводов, сит, справок и обмена прав: {metrics["без_пошлин_переводов_сит_справок_обмена_прав"]} евро\n\n'
    result_message += f'💚Без пошлин, переводов, сит, справок, с обменом прав: {metrics["без_пошлин_переводов_сит_справок_с_обменом_прав"]} евро\n\n'
    result_message += f'🖤Возвраты: \n\n'

    for service, value in services.items():
        number_sales_service: int = value['count']
        if number_sales_service == 0:
            continue

        if service == 'Другая услуга':
            sums: str = '\n'.join(value['details'])
        else:
            sums: str = ' + '.join(value['details'])
        total_sum = format_number_with_spaces(value["summa"])
        result_message += f'{service}\n{value["count"]} шт: {sums}\n💰Сумма {total_sum} евро\n\n'

    return result_message


def find_index_column_service(head_table: list[str]) -> int:
    """Возвращает индекс столбца 'Услуга' в шапке таблицы

    Args:
        head_table (list): список с заголовками колонок таблицы

    Returns:
        index (int): индекс столбца 'Услуга' в шапке таблицы
    """

    for i in range(len(head_table)):
        item = head_table[i].strip().lower()
        if item in ('услуга', 'ыслуга', 'uslyga'):
            return i


def process_service_data(file: io.BytesIO) -> dict[str, ServiceInfo]:
    """Возвращает сформированный словарь услуг. Значения словаря в таком формате (сумма_общая: float, количество:int,
    суммы_отдельно: list[str])

    Args:
        file (BytesIO): файл csv в виде объекта класса UploadedFile, который является подклассом BytesIO

    Returns:
        dict: заполненный словарь, в формате услуга: [сумма_общая, количество, суммы_отдельно]
    """

    services: dict[str, ServiceInfo] = {}

    stringio = StringIO(file.getvalue().decode("utf-8"))
    csv_reader = csv.reader(stringio)
    head = next(csv_reader)
    column_service_index = find_index_column_service(head)

    # заполнение словаря
    for row in csv_reader:
        service: str = row[column_service_index]  # NOTE: положение столбца 'Услуга' в таблице может меняться
        if service == '' or service.isdigit():
            continue

        got_service = services.get(service, -1)
        if got_service == -1:
            services[service] = {'summa': 0, 'count': 0, 'details': []}

        summa: str = normalize_number(row[1])
        services[service]['summa'] += float(summa)
        services[service]['count'] += 1
        services[service]['details'].append(summa)

    return services


def normalize_number(number: str) -> str:
    """Возвращает строку с числом, приведенным к правильному виду. Запятая заменяется на точку,
    пробелы удаляются, удалены неразрывные пробелы (\xa0)

    Args:
        number (str): число для форматирования

    Returns:
        str: отформатированное число"""

    number = number.replace("\xa0", "")
    number = number.replace(" ", "")
    number = number.replace(',', '.')
    return number


def main():
    st.title("Формирование отчета за месяц")
    uploaded_file = st.file_uploader('Выберите .csv файл.\nЕго нужно импортировать из Google Sheets',
                                     type='csv')

    if st.button('Сгенерировать отчет', type='primary'):
        if uploaded_file is None:
            st.error('Выберите файл!')
        else:
            services: dict = process_service_data(uploaded_file)
            result_message = generate_report_message(services, calculation_metrics(services))
            st.code(result_message)
            st.toast('Не забудьте скопировать результат', icon='📋')
            pprint.pprint(services)


if __name__ == '__main__':
    main()
