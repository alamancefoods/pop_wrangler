import re
import numpy as np
import string
import sys, traceback
import glob
import os
import xlsxwriter
from datetime import date, datetime
import pandas as pd
from natsort import natsorted

class PaScraper:

    def __init__(self, file):
        self.f = file
        self.headers = []
        self.items = pd.DataFrame()

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
        date_list = []
        for ex_file in ex_files:
            df = pd.read_excel(ex_file, sheet_name='Sheet1', usecols='A, C')
            df.rename(columns={'Page -1 of 1': 'Q.O.H.'}, inplace=True)
            df.drop([0], inplace=True)
            df_list.append(df)
            date_list.append(df.columns.values[1])
        return df_list, date_list


    #Read from input file:
    def read_input_file(self):
        headers = self._file_headers()
        left_headers = headers[0:7]
        right_headers = headers[14:]
        left_stringy_headers = ", ".join(str(x) for x in left_headers)
        right_stringy_headers = ", ".join(str(x) for x in right_headers)
        df_l = pd.read_excel(self.f, sheet_name='DATA TABLE', usecols=left_stringy_headers)
        df_r = pd.read_excel(self.f, sheet_name='DATA TABLE', usecols=right_stringy_headers)
        items = pd.read_excel(self.f, sheet_name='DATA TABLE', usecols='A')
        self.items = items
        return df_l, df_r

    def print_current_frames(self):
        in_df = self.read_input_file()
        df_list, date_list = self.col_collector()
        date_strings = self._parse_header_list()
        for df in df_list:
            print(df.head())
        print(in_df.tail())
        print(date_list)
        print(self.headers)
        print(date_strings)
        print(self.items)

    def _convert_string_to_date(self, string):
        return datetime.strptime(string, "%m.%d.%y" )


    def _parse_header_list(self):
        date_strings = []
        for index, header in enumerate(self.headers):
            try:
                match = re.match("\w+\s+(\d{2}\.\d{2}\.\d{2})", header)
                formatted_match = self._convert_string_to_date(match.group(1))
                date_strings.append((index, formatted_match))
            except Exception as e:
                print(e)
                pass
        return date_strings


    def filter_by_string(self):
        new_list = []
        df_list, date_list = self.col_collector()
        i = 0
        for df in df_list:
            tmp1 = df['Q.O.H.'].dropna().reset_index(drop= True)
            tmp2 = tmp1[tmp1.apply(isinstance, args=(str,))].reset_index(drop= True)
            tmp3 = tmp1[tmp1.apply(isinstance, args=(int,))].reset_index(drop= True)
            tmp4 = pd.concat([tmp2, tmp3], axis=1)
            tmp4.columns = ['ITEM', date_list[i]]
            tmp4.dropna(inplace= True)
            tmpf = tmp4[tmp4['ITEM'].str.contains(r'^P')].reset_index(drop= True)
            new_list.append(tmpf)
            i+=1
        return new_list

    def join_frames(self):
        df_list = self.filter_by_string()
        df_l, df_r = self.read_input_file()
        for df in df_list:
            tmp_df = df_l.join(df.set_index('ITEM'), on='ITEM')
            df_l = tmp_df
        return pd.concat([df_l, df_r], axis=1)


    def write_to_excel(self):
        df = self.join_frames()
        writer = pd.ExcelWriter('PA_analysis.xlsx', engine='xlsxwriter')
        df.to_excel(writer, sheet_name='DATA TABLE')
        writer.save()
