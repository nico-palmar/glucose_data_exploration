import pandas as pd
from typing import List, Tuple
import math

def read_workbook_sheet(workbook_name: str, sheet_name: str, col_index: int, drop_cols: List[str] = ['carbs (g)', 'bolus (u)', 'basal (u)', 'protein (g)', 'photos']) -> pd.DataFrame:
    """Read an excel sheet from an excel workbook into a dataframe and shifts the data to be correct

    Args: 
        workbook_name: The name of the excel workbook
        sheet_name: The name of the excel sheet in the workbook to be read into a df  
        col_index: The index which contains the column names
        drop_cols: List of columns to drop from the df
    
    Returns: 
        The data from the excel sheet shifted with the column names and correct index values
    """
    df = pd.read_excel(workbook_name, sheet_name=sheet_name)
    df_column = df.iloc[col_index, :]
    # print(df_column.values)
    df.columns = df_column.values
    df = df.loc[col_index+1:, :]
    df.reset_index(inplace=True, drop=True)
    df.drop(columns=drop_cols, inplace=True)
    return df

def get_next_date(curr_date: str):    
    DAY_NAME = 0
    MONTH_NAME = 1
    DAY_NUMBER = 2
    YEAR = 3
    if len(curr_date) == 15:
        date_parts = [curr_date[: 3], curr_date[4: 7], curr_date[8: 10], curr_date[11:]]
    else:
        date_parts = [curr_date[: 3], curr_date[4: 7], curr_date[8: 11], curr_date[12:]]

    date_parts[DAY_NAME] = change_day_name(date_parts[DAY_NAME])
    date_parts[DAY_NUMBER], date_parts[MONTH_NAME], date_parts[YEAR] = change_date(date_parts[DAY_NUMBER], date_parts[MONTH_NAME], date_parts[YEAR])

    return ' '.join(date_parts)
    

def change_day_name(curr_day_name: str):
    day_list = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    # get the index for the next day
    day_list_index = day_list.index(curr_day_name) + 1

    # check if the values exceed those of the list; past sunday
    if day_list_index == 7:
                day_list_index = 0
            
    return day_list[day_list_index]

def change_date(curr_day_number: str, month: str, year: str):
    month_dict = {
        'Jan': 31, 
        'Feb': 28, 
        'Mar': 31, 
        'Apr': 30, 
        'May': 31, 
        'Jun': 30, 
        'Jul': 31, 
        'Aug': 31, 
        'Sep': 30, 
        'Oct': 31, 
        'Nov': 30, 
        'Dec': 31
    }
    month_list=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # get the new day number
    new_day_num = int(curr_day_number[0: curr_day_number.find(',')]) + 1

    # if beyond month limit, change day and month
    if new_day_num > month_dict[month]:
        new_day_num = 1
        new_month_index = month_list.index(month) + 1

        if new_month_index == 12:
            new_month_index = 0
        month = month_list[new_month_index]
    
    # change year if it is a new year
    if month == 'Jan' and new_day_num == 1:
        year = str(int(year) + 1)
    
    # reformat the date number back to original form
    new_day_num = str(new_day_num) + ','
    
    return (new_day_num, month, year)



def read_multiple_days(start_date: str, num_days: int, workbook_name: str = 'Sugarmate-Report-Lucas-04-21.xlsx', col_index: int = 13, drop_cols: List[str] = ['carbs (g)', 'bolus (u)', 'basal (u)', 'protein (g)', 'photos']) -> pd.DataFrame:
    """Reads information from multple days into a dataframe

    Args:
        start_date: A string in the form 'DDD MMM #, YYYY' to start reading info
        num_days: The total number of days to read from the start date (must be > 0)
        workbook_name: The name of the excel workbook
        col_index: The index which contains the column names
        drop_cols: List of columns to drop from the df

    Returns: 
        A new dataframe with all information in the range requested
    """

    # try:
    if num_days < 1:
        raise Exception('Number of days must be >= 1')
    elif num_days % 1 != 0:
        raise Exception('Number of days must be an int value')

    # initialize loop variables
    date_str = start_date
    df_list = []

    for i in range(num_days):
        curr_df = read_workbook_sheet(workbook_name, date_str, col_index, drop_cols=drop_cols)

        # clean the data before adding it to the list
        curr_df = convert_to_numerical(curr_df, ['exercise (mins)', 'mmol/L'])
        curr_df = clean_trends(curr_df)
        curr_df = extract_date_features(curr_df)

        df_list.append(curr_df)
        print('Added df for: ' + date_str)
        date_str = get_next_date(date_str)
    
    # create one large df from all the results
    full_df = pd.concat(df_list)
    full_df.reset_index(inplace=True, drop=True)
    return full_df

    # except Exception as e:
    #     print(f'Read multiple days error: {e}')

def convert_to_numerical(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    for col in cols:
        df[col] = df.loc[df[col].isna() == False, col].astype(float)
 
    return df

def extract_date_features(df: pd.DataFrame) -> pd.DataFrame:
    def split_date(row):
        """Parse the datetime field
        """
        month = row['time'].month
        day = row['time'].day
        year = row['time'].year
        min_time = row['time'].hour * 60 + row['time'].minute
        # for weekday, monday is 0 sunday is 6
        weekday = row['time'].weekday()
        return (day, month, year, min_time, weekday)
 
    # geet new features from the time feature
    df['day'], df['month'], df['year'], df['minutes_time'], df['weekday'] = zip(*df.apply(split_date, axis=1))
    df.drop(columns=['time'], inplace=True)
    return df

def clean_trends(df: pd.DataFrame) -> pd.DataFrame:
    trends_dict = {
        '↓↓': 0,
        '↓': 1,
        '➘': 2,
        '→': 3,
        '➚': 4,
        '↑': 5,
        '↑↑': 6
    }
    def map_trends(trend):
        if not pd.isnull(trend):
            trend = trends_dict[trend]
        return trend
    df['trend'] = df['trend'].apply(map_trends)
    return df


# print(get_next_date('Wed Dec 30, 2020'))
large_df = read_multiple_days('Sat Feb 27, 2021', 1)

print(large_df.head(20))
print(large_df.info())
