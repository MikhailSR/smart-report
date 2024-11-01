"""
Основная задача этого файла сфорировать текстовый файл-отчет, по шаблону. Внутри содержиться информация о суммах,
количестве проданных услуг, обороте и других метриках, которые расчитываються на основе csv файла. CSV файл
предварительно импортируется из google sheet, по одельному месяцу.

В этом модуле использована библиотека easygui для созания пользовательского интефейса. При расщирении функционала,
она будет заменена на Tkinter или PyQt5.
"""

import csv
import pprint
import easygui
import datetime
import os
import sys


def generate_report_file(services: dict, path: str) -> int:
    """Возвращает 1, если report-файл был сформирован и закрыт.
    Файл формируется в заранее оговоренном формате. Формат меняется по необходимости.

    Args:
        services (dict): словарь с данными для записи в отчет-файл.
        path (str): путь к .csv файлу, на основе которого был сформирован словарь services.

    Returns:
        1 (int): в случае успешного закрытия файла
    """

    file_name: str = exstract_basename(path)
    file_result_name: str = datetime.datetime.now().strftime(f"report_%Y-%m-%d_%H-%M-%S_{file_name}.txt")
    home_directory: str = os.path.expanduser('~')
    directory_to_write: str = home_directory + r'\Desktop'
    result_file: str = fr"{directory_to_write}\{file_result_name}"

    with open(result_file, 'w', encoding='utf8') as file:
        revenue: float = round(sum(item[0] for item in services.values()), 2)
        file.write(f'Расчет\nОборот: {revenue}\n\n')

        poslina_and_perevod: float = round(
            sum(value[0] for key, value in services.items() if key in ('Пошлина', 'Перевод')),
            2)
        file.write(f'🧡Без пошлин и переводов: {revenue - poslina_and_perevod}\n\n')

        sita: float = services.get('Сита')[0]
        spravka: float = services.get('Справка')[0]
        obmen_prav: float = services.get('Под ключ права обмен')[0]
        file.write(
            f'🩵Без пошлин, переводов, сит, справок и обмена прав: {revenue - poslina_and_perevod - sita - spravka - obmen_prav}\n\n')

        file.write(
            f'💚Без пошлин, переводов, сит, справок, с обменом прав: {revenue - poslina_and_perevod - sita - spravka}\n\n')

        for service, value in services.items():
            number_sales_service: int = value[1]
            if number_sales_service == 0:
                continue
            sums: str = ' + '.join(value[2])
            file.write(f'{service}\n{value[1]} шт: {sums}\n💰Сумма {value[0]}\n\n')

    return 1


def process_service_data(path_file: str) -> dict[str:list[float, int, list]]:
    """Возвращает сформированный словарь услуг. Значения словаря в таком формате (сумма_общая: float, количество:int,
    суммы_отдельно: list[str]).

    Args:
        path_file (str): путь к .cvs файлу для анализа.
        Файл должен быть в определенномм формете Дата, Сумма, Услуга и т.д.

    Returns:
        dict: заполненный словарь, в формате услуга: [сумма_общая, количество, суммы_отдельно].
    """

    services: dict[str:list[float, int, list]] = {'Консультация': [0, 0, []],
                                                  'Бакалавр': [0, 0, []],
                                                  'Магистратура': [0, 0, []],
                                                  'NIE': [0, 0, []],
                                                  'Доверенность': [0, 0, []],
                                                  'ФОП/автономо': [0, 0, []],
                                                  'Школа испанского': [0, 0, []],
                                                  'Омологация аттестата': [0, 0, []],
                                                  'Омологация диплома': [0, 0, []],
                                                  'ВЗ1': [0, 0, []],
                                                  'Под ключ права обмен': [0, 0, []],
                                                  'Сита': [0, 0, []],
                                                  'Продление студ визы': [0, 0, []],
                                                  'Языковая школа': [0, 0, []],
                                                  'Пошлина': [0, 0, []],
                                                  'Перевод': [0, 0, []],
                                                  'Справка': [0, 0, []],
                                                  'Другая услуга': [0, 0, []]}

    with open(path_file, encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)

        # заполнение словаря
        for row in reader:
            service: str = row[3]
            if service == '' or service.isdigit():
                continue

            summa: str = normalize_number(row[1])
            # сумма
            services[service][0] += float(summa)
            # количество
            services[service][1] += 1
            # суммы_отдельно
            services[service][2].append(summa)

    return services


def exstract_basename(path: str) -> str:
    """Возвращает имя файла, извлеченное из пути к нему.

    Args:
        path (str): путь к файлу.

    Returns:
        str: извлеченное имя файла
    """

    return os.path.basename(path)


def normalize_number(number: str) -> str:
    """Возвращает строку с числом, приведенным к правильному виду. Запятая заменяется на точку,
    начальные и конучные пробелы удаляются.

    Args:
        number (str): число для форматирования.

    Returns:
        str: иоторматированное число"""

    number = number.strip()
    number = number.replace(',', '.')
    return number


def is_csv_file(path: str) -> bool:
    """
    Возвращает True, если файл по указанному пути имеет расширение .csv и False в ином случае. Если параметр path
    пустой, возвращает False.
    Args:
        path (str): путь к файлу с конечным именем и типом файла.

    Returns:
        bool: True - валидный тип. False - не валидный тип.
    """
    if not path:
        return False

    filename, file_extension = os.path.splitext(path)
    if file_extension == '.csv':
        return True
    return False


def main():
    button: str = easygui.buttonbox('Выберите .csv файл.\nПредварительно его нужно испортировать из Google Sheet.',
                                    title='Формирование отчета за месяц', choices=['Выбрать файл', 'Закрыть'])
    if button is None:
        sys.exit()
    if button == 'Закрыть':
        sys.exit()

    path: str = easygui.fileopenbox()
    while not is_csv_file(path):
        easygui.msgbox(title='Ошибка', msg='Выбран неверный файл! С типом НЕ .csv\nПопробуйте еще раз!')
        button = easygui.buttonbox('Выберите .csv файл.\nПредварительно его нужно испортировать из Google Sheet.',
                                   title='Формирование отчета за месяц', choices=['Выбрать файл', 'Закрыть'])
        if button is None:
            sys.exit()
        if button == 'Закрыть':
            sys.exit()
        path = easygui.fileopenbox()

    services: dict = process_service_data(path)
    if generate_report_file(services, path):
        easygui.msgbox('Отчет готов! находиться на рабочем столе')

    pprint.pprint(services)


if __name__ == '__main__':
    main()
