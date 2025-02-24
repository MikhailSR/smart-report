"""
Основная задача этого файла сфорировать текстовый файл-отчет, по шаблону. Внутри содержиться информация о суммах,
количестве проданных услуг, обороте и других метриках, которые расчитываються на основе csv файла. CSV файл
предварительно импортируется из google sheet, по одельному месяцу.

В этом модуле использована библиотека easygui для созания пользовательского интефейса. При расщирении функционала,
она будет заменена на Tkinter или PyQt5.
"""

import csv
import pprint
import datetime
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import TypedDict

global path
root = tk.Tk()


class ServiceInfo(TypedDict):
    summa: float
    count: int
    details: list[str]


def format_number_with_spaces(number: int | float) -> str:
    """Возвращает отформатированное число: разделяет тысячные пробелом, заменят точку на запятую, удаляет незначимый ноль.
        Например, число 1200, функция вернет "1 200".
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
    """
    Возвращает словарь расчитанных основных метрик.
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
        'без_пошлин_переводов_сит_справок_обмена_прав'] = revenue - poslina_and_perevod - sita - spravka - obmen_prav
    metrics['без_пошлин_переводов_сит_справок_с_обменом_прав'] = revenue - poslina_and_perevod - sita - spravka

    return metrics


def generate_report_file(services: dict, path: str, metrics: dict) -> int:
    """Возвращает 1, если report-файл был сформирован и закрыт.
    Файл формируется в заранее оговоренном формате. Формат меняется по необходимости.

    Args:
        services (dict): словарь с данными для записи в отчет-файл.
        path (str): путь к .csv файлу, на основе которого был сформирован словарь services.
        metrics (dict): словарь расчитанных метрик для вывода

    Returns:
        1 (int): в случае успешного закрытия файла
    """

    file_name: str = exstract_basename(path)
    file_result_name: str = datetime.datetime.now().strftime(f"report_%Y-%m-%d_%H-%M-%S_{file_name}.txt")
    home_directory: str = os.path.expanduser('~')
    directory_to_write: str = home_directory + r'\Desktop'
    result_file: str = fr"{directory_to_write}\{file_result_name}"

    metrics = metrics.copy()
    # Форматирую числа для записи в файл
    for key, value in metrics.items():
        metrics[key] = format_number_with_spaces(value)

    with open(result_file, 'w', encoding='utf8') as file:
        file.write(f'Расчет\nОборот: {metrics["revenue"]} евро\n\n')
        file.write(f'🧡Без пошлин и переводов: {metrics["без_пошлин_переводов"]} евро\n\n')
        file.write(
            f'🩵Без пошлин, переводов, сит, справок и обмена прав: {metrics["без_пошлин_переводов_сит_справок_обмена_прав"]} евро\n\n')
        file.write(
            f'💚Без пошлин, переводов, сит, справок, с обменом прав: {metrics["без_пошлин_переводов_сит_справок_с_обменом_прав"]} евро\n\n')

        for service, value in services.items():
            number_sales_service: int = value['count']
            if number_sales_service == 0:
                continue
            sums: str = ' + '.join(value['details'])
            total_sum = format_number_with_spaces(value["summa"])
            file.write(f'{service}\n{value["count"]} шт: {sums}\n💰Сумма {total_sum} евро\n\n')

    return 1


def process_service_data(path_file: str) -> dict[str, ServiceInfo]:
    """Возвращает сформированный словарь услуг. Значения словаря в таком формате (сумма_общая: float, количество:int,
    суммы_отдельно: list[str]).

    Args:
        path_file (str): путь к .cvs файлу для анализа.
        Файл должен быть в определенномм формете Дата, Сумма, Услуга и т.д.

    Returns:
        dict: заполненный словарь, в формате услуга: [сумма_общая, количество, суммы_отдельно].
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

    with open(path_file, encoding='utf-8') as file:
        reader = csv.reader(file)
        head = next(reader)

        # заполнение словаря
        for row in reader:
            service: str = row[3]
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


def select_file():
    file_path = filedialog.askopenfilename()

    if file_path:
        while not is_csv_file(file_path) and file_path != '':
            messagebox.showwarning(title='Ошибка!',
                                   message='Выбран неверный файл! С типом НЕ .csv\nПопробуйте еще раз!')
            file_path = filedialog.askopenfilename()

        if file_path:
            messagebox.showinfo("Файл выбран", f"Вы выбрали файл: {file_path}")
            root.destroy()

    global path
    path = file_path


def main():
    # Создание основного окна
    root.title('Формирование отчета за месяц')
    root.geometry("450x250")
    root.configure(bg="#ffffff")

    message_text = 'Выберите .csv файл.\nПредварительно его нужно испортировать из Google Sheet.'
    # Многострочный виджет для текста, сделанный неподвижным (без прокрутки)
    text_message = tk.Label(root, text=message_text, font=("nunito", 12), bg="#ffffff", fg="#333333", wraplength=400,
                            justify="center")
    text_message.pack(pady=(30, 20))  # Отступы сверху и между текстом и кнопкой

    button = tk.Button(root, text="Выбрать файл",
                       font=("nunito", 11, "bold"),
                       bg="#007BFF", fg="white",
                       activebackground="#0056b3",
                       activeforeground="white",
                       relief="flat", borderwidth=0,
                       highlightthickness=0,
                       padx=20, pady=8,
                       command=select_file)
    button.pack()

    # Настройка закругленных углов для кнопки через `canvas`
    button.config(cursor="hand2", bd=0, highlightthickness=0, relief="solid")
    button.pack_propagate(False)
    root.mainloop()

    # обработка полученного файла
    if not path:
        print('INFO: Программа закрыта пользователем')
        return 1

    services: dict = process_service_data(path)
    if generate_report_file(services, path, calculation_metrics(services)):
        messagebox.showinfo(message='Ваш отчет готов, находиться на рабочем столе!')

    pprint.pprint(services)


if __name__ == '__main__':
    main()
