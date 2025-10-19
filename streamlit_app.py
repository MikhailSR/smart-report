"""
Задача этого файла сфорировать текстовое сообщение-отчет, по шаблону. Внутри содержиться информация о суммах,
количестве проданных услуг, обороте и других метриках, которые расчитываються на основе csv файла. CSV файл
предварительно импортируется из Google Sheets, по одельному месяцу.
"""

import io
import streamlit as st
import csv
import pprint
import os

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

    sita: float = services.get('Сита')['summa']
    metrics['сита'] = sita

    spravka: float = services.get('Справка')['summa']
    metrics['справка'] = spravka

    obmen_prav: float = services.get('Под ключ права обмен')['summa']
    metrics['обмен_прав'] = obmen_prav

    metrics['без_пошлин_переводов'] = revenue - poslina_and_perevod
    metrics[
        'без_пошлин_переводов_сит_справок_обмена_прав'] = round(
        revenue - poslina_and_perevod - sita - spravka - obmen_prav, 2)
    metrics['без_пошлин_переводов_сит_справок_с_обменом_прав'] = round(revenue - poslina_and_perevod - sita - spravka,
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

    for service, value in services.items():
        number_sales_service: int = value['count']
        if number_sales_service == 0:
            continue
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

    services: dict[str, ServiceInfo] = {
        'Консультация': {'summa': 0, 'count': 0, 'details': []},
        'Бакалавр': {'summa': 0, 'count': 0, 'details': []},
        'Магистратура': {'summa': 0, 'count': 0, 'details': []},
        'NIE': {'summa': 0, 'count': 0, 'details': []},
        'Доверенность': {'summa': 0, 'count': 0, 'details': []},
        'ФОП/автономо': {'summa': 0, 'count': 0, 'details': []},
        'Школа испанского': {'summa': 0, 'count': 0, 'details': []},
        'Омологация аттестата': {'summa': 0, 'count': 0, 'details': []},
        'Омологация диплома': {'summa': 0, 'count': 0, 'details': []},
        'ВЗ1': {'summa': 0, 'count': 0, 'details': []},
        'Под ключ права обмен': {'summa': 0, 'count': 0, 'details': []},
        'Сита': {'summa': 0, 'count': 0, 'details': []},
        'Продление студ визы': {'summa': 0, 'count': 0, 'details': []},
        'Языковая школа': {'summa': 0, 'count': 0, 'details': []},
        'Пошлина': {'summa': 0, 'count': 0, 'details': []},
        'Перевод': {'summa': 0, 'count': 0, 'details': []},
        'Справка': {'summa': 0, 'count': 0, 'details': []},
        'Другая услуга': {'summa': 0, 'count': 0, 'details': []},
        'Модификация': {'summa': 0, 'count': 0, 'details': []},
        'Цифровой кочевник': {'summa': 0, 'count': 0, 'details': []}
    }

    stringio = StringIO(file.getvalue().decode("utf-8"))
    csv_reader = csv.reader(stringio)
    head = next(csv_reader)
    column_service_index = find_index_column_service(head)

    # заполнение словаря
    for row in csv_reader:
        service: str = row[column_service_index]  # NOTE: положение столбца 'Услуга' в таблице может меняться
        if service == '' or service.isdigit():
            continue

        summa: str = normalize_number(row[1])
        got_service = services.get(service, -1)
        if got_service == -1:
            services[service] = {'summa': 0, 'count': 0, 'details': []}
            got_service = services.get(service)

        got_service['summa'] += float(summa)
        got_service['count'] += 1
        got_service['details'].append(summa)

    return services


def exstract_basename(path: str) -> str:
    """Возвращает имя файла, извлеченное из пути к нему

    Args:
        path (str): путь к файлу

    Returns:
        str: извлеченное имя файла
    """

    return os.path.basename(path)


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
