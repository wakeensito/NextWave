"""
This module is created by Dylan Sedeno to assist with cleaning and analyzing data for data analytics.
Started: 6/21/2024
Last Modified: 7/2024
"""

# Imports
import pandas as pd
#from googletrans import Translator
import builtins
import re

# Initialize the translator
#translator = Translator()

# Read a CSV file into a DataFrame
def read_csv(file_name: str) -> pd.DataFrame:
    """
    Reads a CSV file into a DataFrame.

    Parameters:
    file_name (str): The name of the CSV file.

    Returns:
    pd.DataFrame: The DataFrame containing the CSV data.
    """
    return pd.read_csv(file_name)

def read_ex(file_name: str) -> pd.DataFrame:
    """
    Reads a CSV file into a DataFrame.

    Parameters:
    file_name (str): The name of the CSV file.

    
    Returns:
    pd.DataFrame: The DataFrame containing the CSV data.
    """
    return pd.read_excel(file_name, header=1)
    

# Save a DataFrame as a CSV file
def save_csv(df: pd.DataFrame, file_name: str) -> None:
    """
    Saves a DataFrame as a CSV file.

    Parameters:
    df (pd.DataFrame): The DataFrame to save.
    file_name (str): The name of the output CSV file.
    """
    df.to_csv(file_name, index=False)

# Merge multiple DataFrames
def merge_files(*dfs: pd.DataFrame) -> pd.DataFrame:
    """
    Merges multiple DataFrames into one.

    Parameters:
    *dfs (pd.DataFrame): DataFrames to merge.

    Returns:
    pd.DataFrame: The merged DataFrame.
    """
    return pd.concat(dfs)

# Convert a column in a DataFrame to a list
def to_list(df: pd.DataFrame, column: str) -> list:
    """
    Converts a column in a DataFrame to a list.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the column.
    column (str): The name of the column to convert.

    Returns:
    list: The list of unique values from the column.
    """
    return df[column].drop_duplicates().tolist()

def merge_and_filter_dataframes(df1, df2):
    """
    Merge two dataframes and remove rows that have the same values in the 
    'close_date', 'unit_#', 'building_name', and 'street_#' columns.
    
    Parameters:
    df1 (pd.DataFrame): The first dataframe.
    df2 (pd.DataFrame): The second dataframe.
    
    Returns:
    pd.DataFrame: The merged and filtered dataframe.
    """
    # Step 1: Combine the dataframes
    combined_df = pd.concat([df1, df2])

    # Step 2: Drop duplicates where all four columns have the same values
    filtered_df = combined_df.drop_duplicates(
        subset=['close_date', 'unit_#'], 
        keep='first'
    )

    return filtered_df

def combine_dataframes(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """
    Combine two data frames while avoiding duplicate rows based on 
    'street_#', 'building_name', 'close_date', and 'unit_number' columns.

    Parameters:
    df1 (pd.DataFrame): The first data frame to combine.
    df2 (pd.DataFrame): The second data frame to combine.

    Returns:
    pd.DataFrame: A new data frame with combined unique rows.
    """
    # Combine the two data frames
    combined_df = pd.concat([df1, df2], ignore_index=True)

    # Remove duplicate rows based on the specified columns
    combined_df = combined_df.drop_duplicates(
        subset=['street_#', 'building_name', 'close_date', 'unit_#'],
        keep='first'
    )
    
    return combined_df

# Strip white spaces from a specified column in a DataFrame
def strip_whitespace(df: pd.DataFrame, column: str) -> None:
    """
    Strips white spaces from a specified column in a DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the column.
    column (str): The name of the column to strip white spaces from.
    """
    df[column] = df[column].str.strip()

# Sort the DataFrame by a specified column
def sort_by_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Sorts the DataFrame by a specified column.

    Parameters:
    df (pd.DataFrame): The DataFrame to be sorted.
    column (str): The name of the column to sort by.

    Returns:
    pd.DataFrame: The sorted DataFrame.
    """
    return df.sort_values(by=column)

# Change all column names to lowercase
def lowercase_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Changes all column names to lowercase.

    Parameters:
    df (pd.DataFrame): The DataFrame to modify.

    Returns:
    pd.DataFrame: The DataFrame with lowercase column names.
    """
    df.columns = df.columns.str.lower()
    return df

def capitalize_first_letter(df, column_name):
    """
    Capitalizes the first letter of each string in the specified column of a DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to modify.
    column_name (str): The name of the column to modify.

    Returns:
    pd.DataFrame: The modified DataFrame with the column values updated.
    """
    if column_name in df.columns:
        df[column_name] = df[column_name].apply(lambda x: x.capitalize() if isinstance(x, str) else x)
    else:
        raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")
    
    return df

# Rename specified columns
def rename_columns(df: pd.DataFrame, new_names: list) -> pd.DataFrame:
    """
    Renames specified columns.

    Parameters:
    df (pd.DataFrame): The DataFrame to modify.
    new_names (list): The new column names.

    Returns:
    pd.DataFrame: The DataFrame with renamed columns.
    """
    df.columns = new_names
    return df

# Drop specified columns
def drop_columns(df: pd.DataFrame, columns_to_drop: list) -> None:
    """
    Drops specified columns from the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to modify.
    columns_to_drop (list): The list of columns to drop.
    """
    df.drop(columns=columns_to_drop, axis=1, inplace=True)

# Reorder columns
def reorder_columns(df: pd.DataFrame, column_order: list) -> pd.DataFrame:
    """
    Reorders columns in the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to modify.
    column_order (list): The list specifying the new column order.

    Returns:
    pd.DataFrame: The DataFrame with reordered columns.
    """
    return df[column_order]

# Print information about a specific column
def column_info(df: pd.DataFrame, column: str) -> None:
    """
    Prints information about a specific column in the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the column.
    column (str): The name of the column to describe.
    """
    print(f"\nUnique:\n{df[column].unique()}")
    print(f"\nDescribe:\n{df[column].describe()}")
    print(f"\nValue Counts:\n{df[column].value_counts()}")

# Print value counts of a specific column
def value_counts(df: pd.DataFrame, column: str) -> None:
    """
    Prints the value counts of a specific column in the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the column.
    column (str): The name of the column to describe.
    """
    print(f"\nValue Counts:\n{df[column].value_counts()}")
    
# This returns the average of a column, it asks for the column
# and you specify if the data frame has nan's
def calculate_mean(df: pd.DataFrame, column: str, nan_yn: str) -> float:
    try:
           # Convert the column to numeric type
        df[column] = pd.to_numeric(df[column], errors='coerce')

        if nan_yn.lower() in ['yes', 'y', 'true', '1']:
            average = df[column].mean(skipna=True)
        else:
            average = df[column].mean()
        return average
    except KeyError:
        print(f"Error: Column '{column}' not found in the DataFrame.")
        return None

# takes in a data frame, a column name and a type class, and changes the columns data
# type to the specified type
def change_column_type(df: pd.DataFrame, column: str, dtype: str) -> None:
    """
    Changes the data type of a specified column.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the column.
    column (str): The name of the column to change.
    dtype (str): The new data type (as a string).

    """
    type_obj = getattr(builtins, dtype)
    df[column] = df[column].astype(type_obj)

# Shows if there is and duplicated rows and if there are null values.
def dup_nul(df: pd.DataFrame) -> None:
    """
    Displays the number of duplicate rows and null values in the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to check.
    """
    print(f"Duplicate Rows: {df.duplicated().sum()}")
    print(f"Null Values:\n{df.isnull().sum()}")

# Return rows with duplicate values in the DataFrame
def get_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns rows with duplicate values in the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to check.

    Returns:
    pd.DataFrame: The DataFrame containing duplicate rows.
    """
    return df[df.duplicated(keep=False)]

def get_duplicates_by_column(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Returns rows with duplicate values based on specific columns in the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to check.
    columns (list): The list of columns to check for duplicates.

    Returns:
    pd.DataFrame: The DataFrame containing duplicate rows based on specific columns.
    """
    return df[df.duplicated(subset=columns, keep=False)]

def drop_duplicates(df: pd.DataFrame) -> None:
    """
    Drops duplicate rows from the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to modify.
    """
    df.drop_duplicates(inplace=True)

# Drop duplicate rows based on specific columns
def drop_duplicates_by_column(df: pd.DataFrame, columns: list) -> None:
    """
    Drops duplicate rows based on specific columns in the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to modify.
    columns (list): The list of columns to check for duplicates.
    """
    df.drop_duplicates(subset=columns, inplace=True)

def drop_na_rows(df: pd.DataFrame, column: str) -> None:
    """
    Drops rows with NaN values in a specified column from the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to modify.
    column (str): The name of the column to check for NaN values.
    """
    df.dropna(subset=[column], inplace=True)

# Fill NaN values in a column with a specified value
def fill_na(df: pd.DataFrame, column: str, value: any) -> None:
    """
    Fills NaN values in a specified column with a given value.

    Parameters:
    df (pd.DataFrame): The DataFrame to modify.
    column (str): The name of the column to fill NaN values in.
    value (any): The value to replace NaN values with.
    """
    df[column].fillna(value, inplace=True)

# Removes characters you dont want in a column.
def clean_column(df: pd.DataFrame, column: str, away: str) -> pd.DataFrame:
    chars_to_remove = str.maketrans("", "", away)  # create a translation table
    df[column] = df[column].str.translate(chars_to_remove)
    return df

# Takes in a data frame, column name and a list of words and then removes 
# the words from the data frame column
def remove_words(df: pd.DataFrame, column: str, words: list) -> pd.DataFrame:
    pattern = '|'.join(re.escape(word) for word in words)
    df[column] = df[column].str.replace(pattern, '', regex=True)
    return df

# Removes whitespaces from a column in a data frame
def remove_space(df: pd.DataFrame, column: str) -> None:
    df[column] = df[column].str.strip()

def remove_nans(df, column_name):
    """
    Remove rows from the DataFrame where the specified column has NaN values.

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    column_name (str): The column name to check for NaN values.

    Returns:
    pd.DataFrame: A DataFrame with the rows containing NaN values in the specified column removed.
    """
    return df.dropna(subset=[column_name])

# Replaces a specified value in a column with another value
def replace_val(df: pd.DataFrame, column: str, old: any, replace: any) -> pd.DataFrame:
    df[column] = df[column].str.replace(old, replace)
    return df

def fill_specific_nan(df, index, column, value):
    """
    Fill a NaN value for a specific index in a specific column in a DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to be modified.
    index (int): The index of the row.
    column (str): The name of the column.
    value: The value to fill in the NaN.

    Returns:
    pd.DataFrame: The DataFrame with the NaN value filled.
    """
    if pd.isna(df.at[index, column]):
        df.at[index, column] = value

def fill_nan_from_another_column(df, source_column, target_column):
    """
    Fill NaN values in the target column with values from the source column 
    if the target column has NaN and the source column has a value.

    Parameters:
    df (pd.DataFrame): The DataFrame to be modified.
    source_column (str): The name of the source column.
    target_column (str): The name of the target column.

    Returns:
    pd.DataFrame: The DataFrame with the NaN values filled.
    """
    for index, row in df.iterrows():
        if not pd.isna(row[source_column]) and pd.isna(row[target_column]):
            df.at[index, target_column] = row[source_column]
    #return df


def reset_index(df, drop=True):
    """
    Reset the index of a dataframe.

    Parameters:
    - df (pd.DataFrame): The dataframe to reset the index of.
    - drop (bool, optional): Whether to drop the index column. Default is False.

    Returns:
    - pd.DataFrame: The dataframe with the reset index.
    """
    df = df.reset_index(drop=drop)
    return df

# , default_value='Unknown'

# Maps values in a column based on a dictionary.
def map_values(df: pd.DataFrame, column: str, mapping_dict: dict) -> pd.DataFrame:
    """
    Maps values in a column based on a dictionary.

    Parameters:
    - df (pandas.DataFrame): The DataFrame containing the column to be mapped.
    - column (str): The name of the column to be mapped.
    - mapping_dict (dict): A dictionary where keys are the original values and values are the mapped values.
    - default_value (str, optional): The value to return if the original value is not found in the mapping_dict. Defaults to 'Unknown'.

    Returns:
    - pandas.Series: The mapped values as a Series.
    """
    def map_value(x):
        for key, value in mapping_dict.items():
            if x.startswith(key):
                return value
        # return default_value

    return df[column].apply(map_value)

def remove_nan_2_col_look(df: pd.DataFrame, col_1: str, col_2: str) -> pd.DataFrame:
    return df.drop(df[(df[col_1].isnull()) & (df[col_2].isnull())].index)

def remove_nan_3_col_look(df: pd.DataFrame, col_1: str, col_2: str, col_3: str) -> pd.DataFrame:
    return df.drop(df[(df[col_1].isnull()) & (df[col_2].isnull())& (df[col_3].isnull())].index)

def remove_nan_4_col_look(df: pd.DataFrame, col_1: str, col_2: str, col_3: str, col_4: str) -> pd.DataFrame:
    return df.drop(df[(df[col_1].isnull()) & (df[col_2].isnull()) & (df[col_3].isnull()) & (df[col_4].isnull())].index)

def remove_rows_by_value(df: pd.DataFrame, column: str, value: any) -> None:
    df.drop(df[df[column] == value].index, inplace=True)

def get_null_rows(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    if col_name not in df.columns:
        raise ValueError(f"Column '{col_name}' does not exist in the dataframe")
    
    null_rows = df[df[col_name].isnull()]
    return null_rows

def fill_values_based_on_condition(df, col1, col2, condition_value):
    """
    Fills values in col1 with values from col2 if col1 has the condition_value.

    Parameters:
    df (pd.DataFrame): The DataFrame to modify.
    col1 (str): The name of the first column to check and fill.
    col2 (str): The name of the second column to take values from.
    condition_value: The specific value to check for in col1.

    Returns:
    pd.DataFrame: The modified DataFrame.
    """
    if col1 in df.columns and col2 in df.columns:
        df[col1] = df.apply(lambda row: row[col2] if row[col1] == condition_value else row[col1], axis=1)
    else:
        raise ValueError(f"One or both columns '{col1}' or '{col2}' do not exist in the DataFrame.")
    
    return df

def sort_dataframe_by_two_columns(df, primary_col, secondary_col, primary_ascending=True, secondary_ascending=True):
    """
    Sorts a DataFrame by two columns.

    Parameters:
    df (pd.DataFrame): The DataFrame to sort.
    primary_col (str): The name of the primary column to sort by.
    secondary_col (str): The name of the secondary column to sort by.
    primary_ascending (bool): Sort order for the primary column. Default is True (ascending).
    secondary_ascending (bool): Sort order for the secondary column. Default is True (ascending).

    Returns:
    pd.DataFrame: The sorted DataFrame.
    """
    if primary_col in df.columns and secondary_col in df.columns:
        sorted_df = df.sort_values(by=[primary_col, secondary_col], 
                                   ascending=[primary_ascending, secondary_ascending])
    else:
        raise ValueError(f"One or both columns '{primary_col}' or '{secondary_col}' do not exist in the DataFrame.")
    
    return sorted_df

def filter_rows_by_value(df, column_name, value):
    """
    Filter rows in the DataFrame based on a specific value in a given column.
    
    Parameters:
    df (pd.DataFrame): The DataFrame to filter.
    column_name (str): The name of the column to filter by.
    value: The value to filter by.
    
    Returns:
    pd.DataFrame: A DataFrame containing only the rows where the specified column has the given value.
    """
    filtered_df = df[df[column_name] == value]
    return filtered_df

def filter_rows_by_substring(df, column_name, substring):
    """
    Filter rows in the DataFrame based on whether a given column contains a specific substring.
    
    Parameters:
    df (pd.DataFrame): The DataFrame to filter.
    column_name (str): The name of the column to filter by.
    substring (str): The substring to look for in the column.
    
    Returns:
    pd.DataFrame: A DataFrame containing only the rows where the specified column contains the given substring.
    """
    filtered_df = df[df[column_name].str.contains(substring, case=False, na=False)]
    return filtered_df

def show_rows_for_value(df, column_name, value):
    """
    Show all rows where a specific column contains a given value.
    
    Parameters:
    df (pd.DataFrame): The DataFrame to search.
    column_name (str): The name of the column to search.
    value: The value to search for in the specified column.
    
    Returns:
    pd.DataFrame: A DataFrame containing the rows that match the search criteria.
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")
        
    return df[df[column_name] == value]

def delete_row(df, index):
    """
    Delete a specific row from the DataFrame given its index.
    
    Parameters:
    df (pd.DataFrame): The DataFrame to delete the row from.
    index (int): The index of the row to delete.
    
    Returns:
    pd.DataFrame: A DataFrame with the specified row deleted.
    """
    if index not in df.index:
        raise ValueError(f"Index '{index}' does not exist in the DataFrame.")
        
    return df.drop(index)


def replace_value_in_row(df, row_index, column_name, new_value):
    """
    Replace the value in a specific row and column of a DataFrame.
    
    Parameters:
    df (pd.DataFrame): The DataFrame to modify.
    row_index (int): The index of the row to modify.
    column_name (str): The name of the column to modify.
    new_value: The new value to set in the specified row and column.
    
    Returns:
    None
    """
    if row_index in df.index and column_name in df.columns:
        df.at[row_index, column_name] = new_value
    else:
        raise ValueError("Invalid row index or column name.")


# specific rows function
def fill_missing_value_sr(df: pd.DataFrame, numerator_col: str, denominator_col: str, result_col: str, row1: int, row2: int, row3: int) -> pd.DataFrame:
    """
    Fill a missing value in a third row by dividing a value from one column in row1 by a value from another column in row2.

    Args:
        df (pd.DataFrame): The input dataframe
        numerator_col (str): The column name for the numerator value
        denominator_col (str): The column name for the denominator value
        result_col (str): The column name for the result value
        row1 (int): The row index for the numerator value
        row2 (int): The row index for the denominator value
        row3 (int): The row index for the result value

    Returns:
        pd.DataFrame: The updated dataframe with the filled missing value
    """
    numerator = df.loc[row1, numerator_col]
    denominator = df.loc[row2, denominator_col]
    result = numerator / denominator
    df.loc[row3, result_col] = round(result, 2)  # Round to 2 decimal points
    #return df


# the one to put in final cleaner file
def fill_missing_values(df: pd.DataFrame, numerator_col: str, denominator_col: str, result_col: str) -> pd.DataFrame:
    """
    Fill missing values in a column by dividing values from two other columns.

    Args:
        df (pd.DataFrame): The input dataframe
        numerator_col (str): The column name for the numerator values
        denominator_col (str): The column name for the denominator values
        result_col (str): The column name for the result values

    Returns:
        pd.DataFrame: The updated dataframe with filled missing values
    """
    for index, row in df.iterrows():
        if pd.isnull(row[result_col]):
            numerator = row[numerator_col]
            denominator = row[denominator_col]
            if denominator != 0:  # Avoid division by zero
                result = numerator / denominator
                df.loc[index, result_col] = round(result, 2)  # Round to 2 decimal points
    #return df

def replace_nan_with_avg(df: pd.DataFrame, column: str) -> pd.DataFrame:
    avg_value = df[column].mean(skipna=True)
    df[column].fillna(avg_value, inplace=True)
    #return df

def print_unique_values(df: pd.DataFrame, column: str) -> None:
    """
    Print the unique values from a specified column in a DataFrame,
    each prefixed with a number.

    Parameters:
    df (pd.DataFrame): The DataFrame to operate on.
    column (str): The name of the column from which to extract unique values.

    Returns:
    None
    """
    if column in df.columns:
        unique_values = df[column].value_counts().index
        for num, value in enumerate(unique_values, start=1):
            print(f"{num}. {value}")
    else:
        print(f"Column '{column}' not found in DataFrame")



def create_column_based_on_dict(df: pd.DataFrame, target_column: str, new_column: str, dict_column: dict, delimiter=',') -> pd.DataFrame:
    """
    Creates a new column based on the values in the target column and a dictionary.

    Parameters:
    - df (pandas.DataFrame): The DataFrame containing the "Target" column.
    - target_column (str): The name of the "Target" column.
    - new_column (str): The name of the new column to be created.
    - dict_column (dict): A dictionary where keys are the values in the target column and values are the corresponding values for the new column.
    - delimiter (str): The delimiter used to separate multiple values in the target column.

    Returns:
    - pandas.DataFrame: The DataFrame with the new column.
    """
    def get_value(x):
        if delimiter is None:
            if x in dict_column:
                return dict_column[x]
            else:
                return 'Unknown'
        else:
            for value in x.split(delimiter):
                value = value.strip()
                if value in dict_column:
                    return dict_column[value]
            return 'Unknown'

    df[new_column] = df[target_column].apply(get_value)
    return df

def get_last_valid_building_info(df: pd.DataFrame, street_column: str, building_name_column: str, address_column: str) -> dict:
    """
    Creates a dictionary with unique street numbers as keys and the last valid instance of building names and addresses as values.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the data.
    street_column (str): The name of the column containing the street numbers.
    building_name_column (str): The name of the column containing the building names.
    address_column (str): The name of the column containing the addresses.

    Returns:
    dict: A dictionary with street numbers as keys and the last valid instance of building names and addresses as values.
    """
    # Initialize the result dictionary
    street_dict = {}

    # Iterate through unique street numbers
    unique_streets = df[street_column].unique()
    for street in unique_streets:
        # Filter rows for the current street and get the last valid instance
        valid_rows = df[(df[street_column] == street) & df[building_name_column].notna() & df[address_column].notna()]
        if not valid_rows.empty:
            last_instance = valid_rows.iloc[-1]
            street_dict[street] = {
                'building_name': last_instance[building_name_column],
                'address': last_instance[address_column]
            }

    return street_dict

def map_building_info(df: pd.DataFrame, street_column: str, building_name_column: str, address_column: str, street_dict: dict) -> pd.DataFrame:
    """
    Maps building name and address in a DataFrame based on street number using a provided dictionary.
    Ensures building names are lowercase with the start of the name capitalized.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the data.
    street_column (str): The name of the column containing the street numbers.
    building_name_column (str): The name of the column to update with building names.
    address_column (str): The name of the column to update with addresses.
    street_dict (dict): A dictionary with street numbers as keys and dictionaries with building names and addresses as values.

    Returns:
    pd.DataFrame: The updated DataFrame.
    """
    def capitalize_building_name(name: str) -> str:
        return name.lower().title() if pd.notna(name) else name

    df[building_name_column] = df[street_column].map(lambda x: capitalize_building_name(street_dict.get(x, {}).get('building_name', None)))
    df[address_column] = df[street_column].map(lambda x: street_dict.get(x, {}).get('address', None))

    return df

def get_property_type(df: pd.DataFrame, prop_col: str, street_col: str) -> pd.DataFrame:
    """
    Fill missing property types in the DataFrame based on the most recent non-NaN value for the same street number.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the data.
    prop_col (str): The name of the property type column.
    street_col (str): The name of the street number column.

    Returns:
    pd.DataFrame: The updated DataFrame with filled property types.
    """
    # Sort the DataFrame by street number and another column (e.g., date or index) to ensure correct ordering
    df.sort_values(by=[street_col], inplace=True)

    # Iterate through the DataFrame and fill missing property types
    last_valid = {}

    for index, row in df.iterrows():
        street_num = row[street_col]
        if pd.notna(row[prop_col]):
            last_valid[street_num] = row[prop_col]
        elif street_num in last_valid:
            df.at[index, prop_col] = last_valid[street_num]

    return df
"""
#translator = Translator()
 
# Function to translate text to english for df do df['col_name'].apply(cleaner.text_to_en)
def text_to_en(text: str, src='auto', dest: str ='en') -> str:
    if pd.isna(text):
        return text
    try:
        translated = translator.translate(text, src=src, dest=dest)
        return translated.text
    except Exception as e:
        print(f"Error translating text: {e}")
        return text
"""