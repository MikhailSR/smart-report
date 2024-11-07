import unittest
import form_report


class TestExstractBasename(unittest.TestCase):
    def tests_exstract(self):
        self.assertEqual(form_report.exstract_basename(
            '/tests/ОТДЕЛ ПРОДАЖ - Сентябрь.csv'),
            'ОТДЕЛ ПРОДАЖ - Сентябрь.csv')
        self.assertEqual(form_report.exstract_basename('D:\Work & Projects\Programming_projects'),
                         'Programming_projects')
        self.assertEqual(form_report.exstract_basename(''), '')


class TestNormalizeNumber(unittest.TestCase):
    def tests_comma(self):
        self.assertEqual(form_report.normalize_number('4,5'), '4.5')
        self.assertEqual(form_report.normalize_number('467,51'), '467.51')

    def test_dot(self):
        self.assertEqual(form_report.normalize_number('4.5'), '4.5')

    def tests_integer(self):
        self.assertEqual(form_report.normalize_number('467'), '467')
        self.assertEqual(form_report.normalize_number('0'), '0')


class TestIsCSVFile(unittest.TestCase):
    def tests(self):
        self.assertFalse(form_report.is_csv_file(''))
        self.assertFalse(form_report.is_csv_file('D:\Work & Projects\Programming_projects'), False)
        self.assertFalse(form_report.is_csv_file('ОТДЕЛ ПРОДАЖ - Сентябрь.json'), False)
        self.assertTrue(form_report.is_csv_file('ОТДЕЛ ПРОДАЖ - Сентябрь.csv'), True)
        self.assertTrue(form_report.is_csv_file('/tests/ОТДЕЛ ПРОДАЖ - Сентябрь.csv'), True)


class TestCalculationMetrics(unittest.TestCase):
    def testMetricsDictJaly(self):
        test_dict = {'NIE': [0, 0, []],
                     'Бакалавр': [1800.0, 3, ['750', '750', '300']],
                     'ВЗ1': [1540.0, 4, ['750', '250', '320', '220']],
                     'Доверенность': [1320.0, 2, ['370', '950']],
                     'Другая услуга': [3414.0,
                                       32,
                                       ['719',
                                        '400',
                                        '20',
                                        '600',
                                        '150',
                                        '250',
                                        '5',
                                        '5',
                                        '5',
                                        '5',
                                        '5',
                                        '10',
                                        '5',
                                        '5',
                                        '5',
                                        '10',
                                        '5',
                                        '45',
                                        '450',
                                        '5',
                                        '5',
                                        '5',
                                        '500',
                                        '5',
                                        '5',
                                        '10',
                                        '5',
                                        '5',
                                        '5',
                                        '5',
                                        '10',
                                        '150']],
                     'Консультация': [2219.0,
                                      22,
                                      ['90',
                                       '89',
                                       '110',
                                       '110',
                                       '110',
                                       '110',
                                       '110',
                                       '100',
                                       '110',
                                       '110',
                                       '50',
                                       '110',
                                       '110',
                                       '110',
                                       '110',
                                       '110',
                                       '110',
                                       '110',
                                       '50',
                                       '110',
                                       '110',
                                       '80']],
                     'Магистратура': [690.0, 2, ['200', '490']],
                     'Омологация аттестата': [1900.0, 3, ['500', '500', '900']],
                     'Омологация диплома': [0, 0, []],
                     'Перевод': [4830.0,
                                 20,
                                 ['750',
                                  '300',
                                  '205',
                                  '55',
                                  '190',
                                  '200',
                                  '200',
                                  '185',
                                  '185',
                                  '110',
                                  '240',
                                  '310',
                                  '340',
                                  '120',
                                  '330',
                                  '210',
                                  '250',
                                  '110',
                                  '220',
                                  '320']],
                     'Под ключ права обмен': [2000.0, 5, ['400', '400', '400', '400', '400']],
                     'Пошлина': [147.0, 3, ['49', '49', '49']],
                     'Продление студ визы': [0, 0, []],
                     'Сита': [450.0, 5, ['100', '50', '50', '50', '200']],
                     'Справка': [0, 0, []],
                     'ФОП/автономо': [500.0, 1, ['500']],
                     'Школа испанского': [312.0, 4, ['84', '72', '72', '84']],
                     'Языковая школа': [3070.0, 3, ['990', '600', '1480']]}
        expected_metrics: dict = {'revenue': 24192.0,
                                  'пошлина_перевод': 4977.0,
                                  'без_пошлин_переводов': 24192.0 - 4977.0,
                                  'обмен_прав': 2000.0,
                                  'сита': 450.0,
                                  'справка': 0.0,
                                  'без_пошлин_переводов_сит_справок_обмена_прав': 24192.0 - 4977.0 - 450.0 - 2000.0,
                                  'без_пошлин_переводов_сит_справок_с_обменом_прав': 24192.0 - 4977.0 - 450.0}
        self.assertEqual(form_report.calculation_metrics(test_dict), expected_metrics)


if __name__ == '__main__':
    unittest.main()
