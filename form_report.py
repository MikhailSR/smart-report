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

global path
root = tk.Tk()


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

    revenue: float = round(sum(item[0] for item in services.values()), 2)
    metrics['revenue'] = revenue

    poslina_and_perevod: float = round(
        sum(value[0] for key, value in services.items() if key in ('Пошлина', 'Перевод')),
        2)
    metrics['пошлина_перевод'] = poslina_and_perevod

    sita: float = services.get('Сита')[0]
    metrics['сита'] = sita

    spravka: float = services.get('Справка')[0]
    metrics['справка'] = spravka

    obmen_prav: float = services.get('Под ключ права обмен')[0]
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

    with open(result_file, 'w', encoding='utf8') as file:
        file.write(f'Расчет\nОборот: {metrics["revenue"]}\n\n')
        file.write(f'🧡Без пошлин и переводов: {metrics["без_пошлин_переводов"]}\n\n')
        file.write(
            f'🩵Без пошлин, переводов, сит, справок и обмена прав: {metrics["без_пошлин_переводов_сит_справок_обмена_прав"]}\n\n')
        file.write(
            f'💚Без пошлин, переводов, сит, справок, с обменом прав: {metrics["без_пошлин_переводов_сит_справок_с_обменом_прав"]}\n\n')

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
