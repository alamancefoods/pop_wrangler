import sys, traceback
import xlsxwriter
import datetime
from datetime import date
import pandas as pd
from natsort import natsorted

class PaWrangler:

    def __init__(self, file):
        self.f = file
        self.quant = pd.DataFrame()
        self.bal = pd.DataFrame()
        self.pdate = pd.DataFrame()
        self.sdate = pd.DataFrame()
        self.quant_state = ''
        self.median_date = None
        self.is_half_bin = False
        self.full_bin = {'A': {}, 'P': {}, 'H': {}, 'W': {}, 'L': {}}
        self.half_bin = {'A': {}, 'P': {}, 'H': {}, 'W': {}, 'L': {}}

    # Accepts a file and builds a sensible dataframe:
    def truss(self):
        df = pd.read_excel(self.f, sheet_name='Sheet1', usecols= "A,C,D,E")
        new_header = df.iloc[0]
        df = df[1:]
        df.columns= new_header

        self.quant = df['Q.O.H.']
        self.bal = df['Balance']
        self.pdate = df['Pickdate']
        self.sdate = df['Ship Date']

        # Determine median date from shipping date data series:
        sorted_sdate = self.sdate.sort_values()
        filtered_sdate = sorted_sdate.dropna().reset_index(drop=True)
        mid_date_index = (len(filtered_sdate) // 2)
        self.median_date = filtered_sdate[mid_date_index]

    # Iterate through dataframes with private validators and helper functions.
    def wrangle(self):
        i = 1
        while(i < len(self.quant) -1):
            self._item_check(i)
            self._bal_check_neg(i)
            i+= 1


    """
    Build Excel file by converting nested dictionaries into dataframes via
    _format_df method.
    """
    def print_to_file(self):
        to_date = datetime.datetime.now().strftime("%b-%d-%Y")
        doc_title = "PA_Negatives_" + to_date + ".xlsx"
        fullbin_key_lists = self._natural_sorter(self.full_bin)
        halfbin_key_lists = self._natural_sorter(self.half_bin)

        writer = pd.ExcelWriter(
            doc_title,
            engine= 'xlsxwriter',
            date_format= 'mmmm dd yyyy',
            datetime_format= 'mmmm dd yyyy'
            )

        workbook = writer.book
        cell_format = workbook.add_format({'bold': True})

        sheet_names = {
            'A': 'Aerosol',
            'P': 'Pops',
            'W': 'Water - 1Gal',
            'L': 'Water - 2.5Gal',
            'H': 'Drinks'
        }

        for key in self.full_bin:
            dff = self._format_df(self.full_bin, key, fullbin_key_lists[key])
            dfh = self._format_df(self.half_bin, key, halfbin_key_lists[key])
            try:
                dff.to_excel(writer, sheet_name= sheet_names[key], startrow = 1)
                worksheet = workbook.get_worksheet_by_name(sheet_names[key])
                worksheet.write('A1', 'Full Bin', cell_format)
            except:
                pass
            try:
                dfh.to_excel(writer, sheet_name= sheet_names[key], startrow= 1, startcol= 7)
                worksheet = workbook.get_worksheet_by_name(sheet_names[key])
                worksheet.write(0, 6, 'Half Bin', cell_format)
            except:
                pass

        workbook = writer.book
        for worksheet in workbook.worksheets():
            worksheet.set_column(1, 1, 0, 0, {'hidden': True})
            worksheet.set_column(3, 3, 15, 0)
            worksheet.set_column(4, 4, 15, 0)
            worksheet.set_column(8, 8, 0, 0, {'hidden': True})
            worksheet.set_column(10, 10, 15, 0)
            worksheet.set_column(11, 11, 15, 0)
        writer.save()


    # Determine item state.
    def _item_check(self, index):
      if(isinstance(self.quant[index], str)):
        self.quant_state = self.quant[index]
        if(self.quant[index][1] == 'H'):
            self.is_half_bin = True
        else:
            self.is_half_bin = False


    """
    Determine if item is half-bin or full-bin.
    Pass appropriate dictionary and index to _dict_mod()
    """
    def _bal_check_neg(self, i):
        try:
            if(self.bal[i] < 0):
                if(self.is_half_bin):
                    self._dict_mod(self.half_bin, i)
                else:
                    self._dict_mod(self.full_bin, i)
        except:
            pass


    """
    The following two functions check for proper data types. _filter_date disregards values from too far
    in the future, while _update_bal gives a different value depending on the sign of the prior value.
    """

    def _update_bal(self, i):
        if((self.bal[i - 1] > 0) or not (isinstance(self.bal[i -1], int))):
            return abs(self.bal[i])
        else:
            return abs(self.bal[i] - self.bal[i - 1])


    def _filter_date(self, i):
        if pd.isna(self.sdate[i]):
            return False
        delta = abs(self.sdate[i] - self.median_date)
        if(delta.days > 45):
            return False
        else:
            return self.sdate[i]


    """
    Given item state and index, construct a list in the appropriate
    dictionary bin.  Create bin if one doesn't exist, update one otherwise.
    """
    def _dict_mod(self, spec_dict, i):
        new_bal = self._update_bal(i)
        ship_date = self._filter_date(i)
        if ship_date:
            try:
                spec_dict[self.quant_state[0]][self.quant_state].append((new_bal, self.pdate[i], ship_date))
            except:
                spec_dict[self.quant_state[0]][self.quant_state] = []
                spec_dict[self.quant_state[0]][self.quant_state].append((new_bal, self.pdate[i], ship_date))
        else:
            pass


    """
    Format dataframe for excel output.
    """
    def _format_df(self, df_dict, df_key, df_key_list):
        concat_list = []
        for i in range(len(df_key_list)):
            tmp_df = pd.DataFrame.from_dict(df_dict[df_key][df_key_list[i]])
            tmp_df.sort_values(by=[2], inplace=True)
            concat_list.append(tmp_df)
        try:
            fin_df = pd.concat(concat_list, keys= df_key_list)
            fin_df.columns = ['deficit', 'pick date', 'ship date']
            return fin_df
        except:
            pass

    """
    Sorts nested dictionary keys into ordered list.
    """
    def _natural_sorter(self, data_dict):
        key_dict = {'A': [], 'P': [], 'W': [], 'H': [], 'L': []}
        for key in key_dict:
            key_dict[key] = natsorted(list(data_dict[key].keys()))
        return key_dict




