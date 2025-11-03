import unittest
import pages.smart_report as test_file


class TestNormalizeNumber(unittest.TestCase):
    def tests_comma(self):
        self.assertEqual(test_file.normalize_number('4,5'), '4.5')
        self.assertEqual(test_file.normalize_number('467,51'), '467.51')

    def test_dot(self):
        self.assertEqual(test_file.normalize_number('4.5'), '4.5')

    def tests_integer(self):
        self.assertEqual(test_file.normalize_number('467'), '467')
        self.assertEqual(test_file.normalize_number('0'), '0')


class TestCalculationMetrics(unittest.TestCase):
    def testMetricsDictJaly(self):
        test_dict = {'NIE': {'count': 0, 'details': [], 'summa': 0},
                     'Бакалавр': {'count': 3, 'details': ['750', '750', '300'], 'summa': 1800.0},
                     'ВЗ1': {'count': 4, 'details': ['750', '250', '320', '220'], 'summa': 1540.0},
                     'Доверенность': {'count': 2, 'details': ['370', '950'], 'summa': 1320.0},
                     'Другая услуга': {'count': 32,
                                       'details': ['719',
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
                                                   '150'],
                                       'summa': 3414.0},
                     'Консультация': {'count': 22,
                                      'details': ['90',
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
                                                  '80'],
                                      'summa': 2219.0},
                     'Магистратура': {'count': 2, 'details': ['200', '490'], 'summa': 690.0},
                     'Омологация аттестата': {'count': 3,
                                              'details': ['500', '500', '900'],
                                              'summa': 1900.0},
                     'Омологация диплома': {'count': 0, 'details': [], 'summa': 0},
                     'Перевод': {'count': 20,
                                 'details': ['750',
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
                                             '320'],
                                 'summa': 4830.0},
                     'Под ключ права обмен': {'count': 5,
                                              'details': ['400', '400', '400', '400', '400'],
                                              'summa': 2000.0},
                     'Пошлина': {'count': 3, 'details': ['49', '49', '49'], 'summa': 147.0},
                     'Продление студ визы': {'count': 0, 'details': [], 'summa': 0},
                     'Сита': {'count': 5,
                              'details': ['100', '50', '50', '50', '200'],
                              'summa': 450.0},
                     'Справка': {'count': 0, 'details': [], 'summa': 0},
                     'ФОП/автономо': {'count': 1, 'details': ['500'], 'summa': 500.0},
                     'Школа испанского': {'count': 4,
                                          'details': ['84', '72', '72', '84'],
                                          'summa': 312.0},
                     'Языковая школа': {'count': 3,
                                        'details': ['990', '600', '1480'],
                                        'summa': 3070.0}}
        expected_metrics: dict = {'revenue': 24192.0,
                                  'пошлина_перевод': 4977.0,
                                  'без_пошлин_переводов': 24192.0 - 4977.0,
                                  'обмен_прав': 2000.0,
                                  'сита': 450.0,
                                  'справка': 0.0,
                                  'без_пошлин_переводов_сит_справок_обмена_прав': 24192.0 - 4977.0 - 450.0 - 2000.0,
                                  'без_пошлин_переводов_сит_справок_с_обменом_прав': 24192.0 - 4977.0 - 450.0}
        self.assertEqual(test_file.calculation_metrics(test_dict), expected_metrics)


class TestFormatNumberWithSpaces(unittest.TestCase):
    def test_integer(self):
        self.assertEqual(test_file.format_number_with_spaces(100), "100")
        self.assertEqual(test_file.format_number_with_spaces(1000), '1 000')
        self.assertEqual(test_file.format_number_with_spaces(120345), '120 345')

    def test_float(self):
        self.assertEqual(test_file.format_number_with_spaces(100.5), "100,5")
        self.assertEqual(test_file.format_number_with_spaces(1000.5), "1 000,5")
        self.assertEqual(test_file.format_number_with_spaces(10000.5), "10 000,5")
        self.assertEqual(test_file.format_number_with_spaces(100.0), "100")
        self.assertEqual(test_file.format_number_with_spaces(10000.0), "10 000")


if __name__ == '__main__':
    unittest.main()
