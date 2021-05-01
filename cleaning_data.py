import pandas as pd
import numpy as np
from typing import List, Tuple
import math
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer

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

def get_next_date(curr_date: str) -> str:
    """Gets the next string value of the date in form DDD MMM #, YYYY
    """    
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
    """Change the day of the week to the next day
    """
    day_list = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    # get the index for the next day
    day_list_index = day_list.index(curr_day_name) + 1

    # check if the values exceed those of the list; past sunday
    if day_list_index == 7:
                day_list_index = 0
            
    return day_list[day_list_index]

def change_date(curr_day_number: str, month: str, year: str):
    """Change the date value to the next date 
    """
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



def read_multiple_days(start_date: str, num_days: int, workbook_name: str = 'Sugarmate-Report-04-21.xlsx', col_index: int = 13, drop_cols: List[str] = ['carbs (g)', 'bolus (u)', 'basal (u)', 'protein (g)', 'photos']) -> pd.DataFrame:
    """Reads information from multple days into a dataframe and cleans the dataframe

    Args:
        start_date: A string in the form 'DDD MMM #, YYYY' to start reading info
        num_days: The total number of days to read from the start date (must be > 0)
        workbook_name: The name of the excel workbook
        col_index: The index which contains the column names
        drop_cols: List of columns to drop from the df

    Returns: 
        A new dataframe with all information in the range requested with clean data
    """

    try:
        if num_days < 1:
            raise Exception('Number of days must be >= 1')
        elif num_days % 1 != 0:
            raise Exception('Number of days must be an int value')

        # initialize loop variables
        date_str = start_date
        df_list = []

        for i in range(num_days):
            # read the current excel spreadsheet and append it to the list of dfs for each sheet
            curr_df = read_workbook_sheet(workbook_name, date_str, col_index, drop_cols=drop_cols)
            
            # perform imputations on trends and glucose levels
            curr_df = impute_data_pipeline(curr_df)
            df_list.append(curr_df)

            print('Added df for: ' + date_str)
            # change to the next date to read in the next excel sheet
            date_str = get_next_date(date_str)
        
        # get the fine dataframe by applying a data cleaning pipeline
        full_df = assemble_final_df(df_list)
        return full_df

    except Exception as e:
        print(f'Read multiple days error: {e}')

        if len(df_list) > 0:
            full_df = assemble_final_df(df_list)
            # return the results up to point of failure if something fails
            return full_df

def assemble_final_df(df_list: List[pd.DataFrame]) -> pd.DataFrame:
    """Put each of the dfs together to create a final clean df 

    Args: 
        df_list: A list of dataframes to be concatenated

    Returns: 
        The final version of the clean and full dataframe
    """
    # create one large df from all the results
    full_df = pd.concat(df_list)
    full_df.reset_index(inplace=True, drop=True)

    # clean the data using a pipeline 
    cleaning_pipe = Pipeline(steps=[
        # ('obj_to_num', FunctionTransformer(convert_to_numerical)),
        # ('clean_trends', FunctionTransformer(clean_trends)),
        ('extract_date_features', FunctionTransformer(extract_date_features)),
        ('clean_activity', FunctionTransformer(clean_activity)),
        ('oh_encode', FunctionTransformer(one_hot_encode))
    ])
    # fit the pipeline
    full_df = cleaning_pipe.fit_transform(full_df)
    return full_df

def impute_data_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Impute missing trend and glucose data based on time series interpolation
    """
    trend_transformer = Pipeline(steps=[
        ('map_trends', FunctionTransformer(map_trends_outer)),
        ('obj_to_num', FunctionTransformer(convert_to_numerical)),
    ])

    # transform to numerical data
    df = trend_transformer.fit_transform(df)
    # use pandas linear imputation for time series data and round the new trend values 
    df['trend'] = df['trend'].interpolate().round()
    df['mmol/L'] = df['mmol/L'].interpolate().round(2)
    return df


def one_hot_encode(df: pd.DataFrame, cols: List[str] = ['activity']) -> pd.DataFrame:
    """One hot encodes a list of columns in a dataframe
    """

    all_dfs = [df]
    for col in cols:
        # one hot encode the data and add it to a list to later be concatenated
        oh_df = pd.get_dummies(df[col])
        all_dfs.append(oh_df)

    df = pd.concat(all_dfs, axis=1)

    # fill the exercise times prior to dropping
    df = fill_exercise_times(df)

    # drop all parent columns (of the OH encoding)
    df.drop(columns=cols, inplace=True)
    return df

def fill_exercise_times(df: pd.DataFrame) -> pd.DataFrame:
    """Fill in the one hot encoded exercise values to contain a 1 when exercise was occuring
    """
    df = df.copy()
    MEASUREMENT_INTERVAL = 5
    # iterate through df to keep track of exercise time between rows
    curr_exercise =  {'exercise': None, 'time': 0}
    for index, row in df.iterrows():
        # check if there is any current exercise 
        if curr_exercise['exercise'] != None and curr_exercise['time'] > 0 and pd.isnull(row['activity']):
            # rows are copies from the dataframe, use .loc to modify elements from the df  
            df.loc[index, curr_exercise['exercise']] = 1
            # print(curr_exercise['exercise'], df.loc[index, curr_exercise['exercise']])
            curr_exercise['time'] -= MEASUREMENT_INTERVAL

            # if the time has been updated to a negative number, reset the time to zero and reset the exercise
            if curr_exercise['time'] < 0:
                # check if the majortiy of the interval was spent not exercizing and remove it if so  
                if curr_exercise['time'] <= -3:
                    df.loc[index, curr_exercise['exercise']] = 0
                curr_exercise['exercise'] = None
                curr_exercise['time'] = 0
        
        # check if there is a new activity for the row 
        if not pd.isnull(row['activity']):
            # print('Activity: ' + row['activity'])
            curr_exercise['exercise'] = row['activity']
            curr_exercise['time'] = row['exercise (mins)'] - MEASUREMENT_INTERVAL  

    return df   


def convert_to_numerical(df: pd.DataFrame, cols: List[str] = ['exercise (mins)', 'mmol/L']) -> pd.DataFrame:
    """Converts a list of columns to numerical types in a dataframe
    """
    for col in cols:
        df[col] = df.loc[df[col].isna() == False, col].astype(float)
 
    return df

def extract_date_features(df: pd.DataFrame) -> pd.DataFrame:
    """Parse the datetime feature into multiple features
    """
    def split_date(row):
        """Parse the datetime field
        """
        month = row['time'].month
        day = row['time'].day
        year = row['time'].year
        h_time = row['time'].hour + row['time'].minute / 60
        # for weekday, monday is 0 sunday is 6
        weekday = row['time'].weekday()
        return (day, month, year, h_time, weekday)
 
    # geet new features from the time feature
    df['day'], df['month'], df['year'], df['hours_time'], df['weekday'] = zip(*df.apply(split_date, axis=1))
    df.drop(columns=['time'], inplace=True)
    return df

def clean_activity(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the activity column to only contain acitivty names
    """
    df['activity'] = df.loc[df['activity'].isna() == False, 'activity'].apply(lambda activity: activity[:activity.find('(')].strip())
    return df


def map_trends_outer(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the trends column to only contain numerical data; label encode the trend data
    """
    trends_dict = {
        '↓↓': 0,
        '↓': 1,
        '➘': 2,
        '→': 3,
        '➚': 4,
        '↑': 5,
        '↑↑': 6
    }

    def map_trends_inner(trend: str) -> int:
        # convert weird trend to later impute with better values
        if trend == '⌛︎':
            trend = np.nan

        elif trend in trends_dict.keys():
            trend = trends_dict[trend]
        return trend
    
    df['trend'] = df['trend'].apply(map_trends_inner)
    return df

# large_df = read_multiple_days('Fri Apr 16, 2021', 5)

# print(large_df.loc[70: 120])
# print(large_df.info())
