import sys, traceback
import numpy as np
import xlsxwriter
import datetime
from datetime import date, datetime, timedelta
from pytz import timezone
import pandas as pd
from natsort import natsorted

class PaWrangler:

    def __init__(self, file, day_count = 30, path = ''):
        self.f = file
        self.path = path
        self.day_count = day_count
        self.quant = pd.DataFrame()
        self.qty = pd.DataFrame()
        self.pdate = pd.DataFrame()
        self.sdate = pd.DataFrame()
        self.padate = None
        self.quant_state = ''
        self.qoh_state = None
        self.median_date = None
        self.is_half_bin = False
        self.full_bin = {'A': {}, 'P': {}, 'H': {}, 'W': {}, 'L': {}}
        self.half_bin = {'A': {}, 'P': {}, 'H': {}, 'W': {}, 'L': {}}
        self.totals = {'A': {}, 'P': {}, 'H': {}, 'W': {}, 'L': {}}

    # Accepts a file and builds a sensible dataframe:
    def truss(self):
        df = pd.read_excel(self.f, sheet_name='Sheet1', usecols= "A,B,C,D,E")
        self.padate = list(df.columns)[2]
        new_header = df.iloc[0]
        df = df[1:]
        df.columns= new_header

        self.quant = df['Q.O.H.']
        self.qty = df[' Qty']
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
            self._qty_check_val(i)
            i+= 1


    """
    Build Excel file by converting nested dictionaries into dataframes via
    _format_df method.
    """
    def print_to_file(self):
        eastern = timezone('US/Eastern')
        local_dt = eastern.localize(datetime.now())
        timestamp = local_dt.strftime("%I:%M-%p")
        to_date = self.padate.strftime("%b-%d-%Y")
        doc_title = f'{self.day_count}_day_PA_Deficits_{to_date}:{timestamp}.xlsx'
        dst = self.path + doc_title
        fullbin_key_lists = self._natural_sorter(self.full_bin)
        halfbin_key_lists = self._natural_sorter(self.half_bin)

        writer = pd.ExcelWriter(
            dst,
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
            dft = self._total_table(dff, dfh)
            try:
                dft.to_excel(writer, sheet_name= sheet_names[key], startrow = 1, startcol= 0)
                worksheet = workbook.get_worksheet_by_name(sheet_names[key])
                worksheet.write('A1', 'Item ', cell_format)
            except:
                pass
            try:
                dff.to_excel(writer, sheet_name= sheet_names[key], startrow = 1, startcol= 4)
                worksheet = workbook.get_worksheet_by_name(sheet_names[key])
                worksheet.write(0, 4, 'Full Bin', cell_format)
            except:
                pass
            try:
                dfh.to_excel(writer, sheet_name= sheet_names[key], startrow= 1, startcol= 11)
                worksheet = workbook.get_worksheet_by_name(sheet_names[key])
                worksheet.write(0, 11, 'Half Bin', cell_format)
            except:
                pass

        workbook = writer.book
        for worksheet in workbook.worksheets():
            worksheet.set_column(1, 1, 0, 0, {'hidden': True})
            worksheet.set_column(2, 2, 25, 0)
            worksheet.set_column(5, 5, 0, 0, {'hidden': True})
            worksheet.set_column(7, 7, 15, 0)
            worksheet.set_column(8, 8, 15, 0)
            worksheet.set_column(9, 9, 15, 0)
            worksheet.set_column(12, 12, 0, 0, {'hidden': True})
            worksheet.set_column(14, 14, 15, 0)
            worksheet.set_column(15, 15, 15, 0)
            worksheet.set_column(16, 16, 15, 0)
        writer.save()
        return doc_title


    # Determine item state.
    def _item_check(self, index):
      if(isinstance(self.quant[index], str)):
        self.quant_state = self.quant[index]
        self.qoh_state = self.quant[index + 1]
        if(self.quant[index][1] == 'H'):
            self.is_half_bin = True
        else:
            self.is_half_bin = False


    """
    Determine if item is half-bin or full-bin.
    Pass appropriate dictionary and index to _dict_mod()
    """
    def _qty_check_val(self, i):
        try:
            if(isinstance(self.qty[i], int)):
                if(self.is_half_bin):
                    self._dict_mod(self.half_bin, i)
                else:
                    self._dict_mod(self.full_bin, i)
        except:
            pass



    """
    Determine if a quantity's correspondent date is permissible.
    """
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
        ship_date = self._filter_date(i)
        if ship_date:
            try:
                spec_dict[self.quant_state[0]][self.quant_state]['balance_list'].append((self.qty[i], self.pdate[i], ship_date))
            except:
                spec_dict[self.quant_state[0]][self.quant_state] = {'balance_list': [], 'quantity_on_hand' : self.qoh_state, 'formatted_df': pd.DataFrame()}
                spec_dict[self.quant_state[0]][self.quant_state]['balance_list'].append((self.qty[i], self.pdate[i], ship_date))
        else:
            pass




    """
    External function that will be applied acrros a pandas dataframe for calculating deficits.
    The values are negative so that I won't have to change the sign later when representing deficit values to the user.
    """
    def calculate_deficit(self, order_quantity):
        quantity_diff = self.qoh_state - order_quantity
        if(self.qoh_state > 0 and quantity_diff < 0):
            self.qoh_state = quantity_diff
            return -quantity_diff
        elif(self.qoh_state < 0):
            self.qoh_state = quantity_diff
            return order_quantity
        else:
            self.qoh_state = quantity_diff
            return -order_quantity

    def _split_sort_dataframe_by_date(self, unsorted_df, outer_date):
        no_null_pdate_df = unsorted_df.dropna(subset=['p_date'])
        no_null_pdate_df = no_null_pdate_df[no_null_pdate_df['p_date'] <= outer_date]
        null_pdate_df = unsorted_df.loc[unsorted_df['p_date'].isna()]
        null_pdate_df = null_pdate_df[null_pdate_df['s_date'] <= outer_date]
        no_null_pdate_df = no_null_pdate_df.sort_values(by=['p_date'])
        null_pdate_df = null_pdate_df.sort_values(by=['s_date'])
        return no_null_pdate_df, null_pdate_df

    """
    Format dataframe for excel output.
    """
    def _format_df(self, df_dict, df_key, df_key_list):
        concat_list = []
        formatted_key_list = []
        outer_date = self.padate + timedelta(days = int(self.day_count))
        for i in range(len(df_key_list)):
            if (df_dict[df_key][df_key_list[i]]['formatted_df'].empty):
                """
                Capture Quantity on Hand for item. Construct prelimenary dataframe for determining deficits.
                """
                self.qoh_state = df_dict[df_key][df_key_list[i]]['quantity_on_hand']
                unsorted_df = pd.DataFrame.from_dict(df_dict[df_key][df_key_list[i]]['balance_list'])
                unsorted_df.columns = ['order_quantity', 'p_date', 's_date']

                """
                Split dataframes by pick-date and ship-date. Dropping any values not within the desired range.
                """

                no_null_pdate_df, null_pdate_df = self._split_sort_dataframe_by_date(unsorted_df, outer_date)

                """
                Tally deficits using previously captured 'qoh' value. Drop any values that aren't negative.
                """
                no_null_pdate_df['order_quantity'] = no_null_pdate_df['order_quantity'].apply(self.calculate_deficit)
                null_pdate_df['order_quantity'] = null_pdate_df['order_quantity'].apply(self.calculate_deficit)

                """
                Drop non-negative values from dataframes
                """
                no_null_pdate_df = no_null_pdate_df[no_null_pdate_df['order_quantity'] > 0]
                null_pdate_df = null_pdate_df[null_pdate_df['order_quantity'] > 0]

                """
                Format Dataframe for readability
                """
                sorted_df = pd.concat([no_null_pdate_df, null_pdate_df]).reset_index(drop=True)
                sorted_df[3] = np.nan
                sorted_df.columns = ['deficit', 'p_date', 's_date', 'total']
                try:
                    new_sum= sorted_df['deficit'].sum()
                    sorted_df.iat[0, 3] = new_sum
                    concat_list.append(sorted_df)
                    formatted_key_list.append(df_key_list[i])
                    df_dict[df_key][df_key_list[i]]['formatted_df'] = sorted_df
                except:
                    pass
            else:
                sorted_df = df_dict[df_key][df_key_list[i]]['formatted_df']
                no_null_pdate_df, null_pdate_df = self._split_sort_dataframe_by_date(sorted_df, outer_date)
                sorted_df = pd.concat([no_null_pdate_df, null_pdate_df]).reset_index(drop=True)
                sorted_df.columns = ['deficit', 'p_date', 's_date', 'total']
                try:
                    new_sum= sorted_df['deficit'].sum()
                    sorted_df.iat[0,3] = new_sum
                    concat_list.append(sorted_df)
                    formatted_key_list.append(df_key_list[i])
                    df_dict[df_key][df_key_list[i]]['formatted_df'] = sorted_df
                except:
                    pass
        try:
            fin_df = pd.concat(concat_list, keys= formatted_key_list)
            fin_df.columns = ['deficit', 'pick date', 'ship date', 'TOTAL DEFICIT']
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





    def _total_table(self, full_table, half_table):
        try:
            total_dff = full_table['TOTAL DEFICIT'].dropna()
        except:
            total_dff = pd.Series()
        try:
            total_dfh = half_table['TOTAL DEFICIT'].dropna()
        except:
            total_dfh = pd.Series()
        if(total_dff.any() and total_dfh.any()):
            dft = pd.concat([total_dff, total_dfh])
        elif(total_dff.any()):
            dft = total_dff
        elif(total_dfh.any()):
            dft = total_dfh
        else:
            dft = None
        try:
            dft.rename(f'Deficits Over Next {self.day_count} days', inplace=True)
        except:
            pass
        return dft
