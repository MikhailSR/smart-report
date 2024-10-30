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
        self.assertEqual(form_report.is_csv_file(''), False)
        self.assertEqual(form_report.is_csv_file('D:\Work & Projects\Programming_projects'), False)
        self.assertEqual(form_report.is_csv_file('ОТДЕЛ ПРОДАЖ - Сентябрь.json'), False)
        self.assertEqual(form_report.is_csv_file('ОТДЕЛ ПРОДАЖ - Сентябрь.csv'), True)
        self.assertEqual(form_report.is_csv_file('/tests/ОТДЕЛ ПРОДАЖ - Сентябрь.csv'), True)


class TestTestBrench(unittest.TestCase):
    def tests(self):
        self.assertEqual(form_report.test_brench(), None)


if __name__ == '__main__':
    unittest.main()
