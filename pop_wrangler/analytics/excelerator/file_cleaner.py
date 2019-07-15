import xlsxwriter
import pandas as pd


class FileCleaner:
    def __init__(self, file, sheet_name=0):
        self.f = file
        self.sheet_name = sheet_name


    def clean(self):
        df = pd.read_excel(self.f, self.sheet_name)
        df.replace(to_replace = '[$%&*()!#\+=]', value = '')
        csv_string = df.to_csv('/Users/huntertempleman/Documents/test.csv')



