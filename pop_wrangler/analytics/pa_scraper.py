import numpy as np
import string
import sys, traceback
import glob
import os
import xlsxwriter
import datetime
from datetime import date
import pandas as pd
from natsort import natsorted

class PaScraper:

    def __init__(self, file):
        self.f = file
        self.headers = []

    #Collect files for scraping.
    def _file_collector(self):
        path = sys.path[0]
        dungeon_tunnel = path +"/analytics/globdungeon/*.xlsx"
        files = glob.glob(dungeon_tunnel)
        return files

    def _file_headers(self):
        headers = list(string.ascii_uppercase)[:-6]
        return headers


    #Gather dataframes for files.
    def col_collector(self):
        ex_files = self._file_collector()
        df_list = []
        for ex_file in ex_files:
            df = pd.read_excel(ex_file, sheet_name='Sheet1', usecols='A')
            df_list.append(df)
        return df_list


    def date_collector(self):
        ex_files = self._file_collector()
        df_list = []
        for ex_file in ex_files:
            df = pd.read_excel(ex_file, sheet_name='Sheet1', usecols='C')
            df_list.append(df.columns.values[0])
        return df_list


    #Read from input file:
    def read_input_file(self):
        headers = self._file_headers()
        stringy_headers = ", ".join(str(x) for x in headers)
        df = pd.read_excel(self.f, sheet_name='DATA TABLE', usecols=stringy_headers)
        self.headers = list(df)
        return df

    def print_current_frames(self):
        in_df = self.read_input_file()
        df_list = self.col_collector()
        date_list = self.date_collector()
        for df in df_list:
            print(df.head())
        print(in_df.head())
        print(date_list)
