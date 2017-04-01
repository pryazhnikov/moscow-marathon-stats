#!/usr/bin/env python3
import numpy as np
import pandas as pd
import sys
import json
import glob
import re
import os.path

INPUT_FILE_NAMES_PATTERN = 'data/temporary/*_42km.json'
OUTPUT_FILE_NAME = 'data/all_results.csv'

GENDER_MALE    = 'Male'
GENDER_FEMALE  = 'Female'
GENDER_UNKNOWN = 'Unknown'

STATUS_FINISHED = 'Finished'
STATUS_DNS = 'Did not started'
STATUS_DNF = 'Did not finished'
STATUS_DSQ = 'Disqualified'

def get_gender_by_code(code):
    code = int(code)
    if code == 1:
        return GENDER_MALE
    elif code == 2:
        return GENDER_FEMALE
    else:
        return GENDER_UNKNOWN

def get_cleaned_time(value):
    if value == '':
        return np.nan
    else:
        return value.strip()

def get_cleaned_team(value):
    if value is None:
        return np.nan

    value = value.strip()
    if value == '':
        return np.nan

    # todo implement additional cleaning rules
    return value

def get_full_name(runner_info):
    first_name = runner_info['first_name']
    last_name = runner_info['last_name']
    if (first_name is None) and (last_name is None):
        return np.nan
    elif first_name is None:
        return last_name
    elif last_name is None:
        return first_name
    else:
        return str(first_name) + ' ' + str(last_name)

def get_file_info(file_name):
    year = None
    gender = GENDER_UNKNOWN
    distance = None

    base_name = os.path.basename(file_name)
    print(base_name)
    match = re.search(r'^(\d+)(?:_(male|female))?_(\d+)km.json$', base_name)
    if match is not None:
        year = int(match.group(1))
        distance = int(match.group(3))
        gender_code = match.group(2)
        if gender_code == 'male':
            gender = GENDER_MALE
        elif gender_code == 'female':
            gender = GENDER_FEMALE

    return {
        'year': year,
        'gender' : gender,
        'distance' : distance,
    }

def load_new_format_file_frame(file_name):
    '''
    Data loading in new JSON format (valid for 2015-2016)
    '''
    file_meta = get_file_info(file_name)

    # We cannot use pd.read_json() due to data files structure
    f = open(file_name, 'r')
    raw_data = f.read()
    file_data = json.loads(raw_data)
    if 'meta' in file_data:
        # ["genderPosition","absolutePosition","number","last_name", "first_name","age","country","city","team","resultTime","realStartTime","5000","10000","15000","21100","25000","30000","35000", "ageGroup", "agPlace"]
        data_columns = file_data['meta']
    elif file_meta['year'] == 2014:
        # There is no meta info at 2014 data files
        data_columns = [
            "genderPosition",
            "number",
            "last_name",
            "first_name",
            "age",
            "country",
            "city",
            "team",
            "resultTime",
            "realStartTime",
            "ageGroup",
            "agPlace",
            "5000",
            "10000",
            "21100",
            "30000",
            "35000"
        ]
    else:
        return None

    result_df = pd.DataFrame(file_data['data'], columns=data_columns)

    result_df['first_name'] = result_df['first_name'].str.strip()
    result_df['last_name'] = result_df['last_name'].str.strip()
    result_df['name'] = result_df.apply(get_full_name, axis=1)

    result_df['year'] = file_meta['year']
    result_df['gender'] = file_meta['gender']

    return get_processed_data_frame(result_df)

def get_processed_data_frame(result_df):
    result_df['team'] = result_df['team'].map(get_cleaned_team)

    result_df['resultTime'] = result_df['resultTime'].map(get_cleaned_time)
    time_columns = ['5000', '10000', '15000', '21100', '25000', '30000', '35000', '40000']
    for column in time_columns:
        if column in result_df.columns:
            result_df[column] = result_df[column].map(get_cleaned_time)

    # Data cleaning for runners without finish time
    result_df['status'] = STATUS_FINISHED
    special_statuses = {
        'DNF': STATUS_DNF,
        'DNS': STATUS_DNS,
        'DSQ': STATUS_DSQ,
    }
    result_times = result_df['resultTime']
    for time_value, status_value in special_statuses.items():
        status_filter = (result_times == time_value)
        result_df.loc[status_filter, 'genderPosition'] = np.nan
        result_df.loc[status_filter, 'resultTime'] = np.nan
        result_df.loc[status_filter, 'status'] = status_value

    # Wrong result times are removed, we have to use int only values for the rest
    # This conversion is used as a doublecheck
    result_df['genderPosition'] = result_df['genderPosition'] \
        .dropna() \
        .apply(lambda x: int(x))

    fields = ['year', 'gender', 'status', 'resultTime', 'genderPosition', 'country', 'city', 'team']
    return result_df[fields]

def load_old_format_file_frame(file_name):
    file_info = get_file_info(file_name)

    result_df = pd.read_json(file_name)
    result_df['year'] = file_info['year']
    result_df['team'] = None # There is no such data at old format

    result_df = result_df.apply(add_country_to_runner, axis=1)

    return get_processed_data_frame(result_df)

def add_country_to_runner(runner_row):
    (city, country) = split_long_city_name(runner_row['city'])
    runner_row['city'] = city
    runner_row['country'] = country
    return runner_row

def split_long_city_name(full_city_name):
    if full_city_name is None:
        return (np.nan, np.nan)

    full_city_name = str(full_city_name).strip()
    if not full_city_name:
        return (np.nan, np.nan)

    parts_list = full_city_name.split(',', 1)
    if len(parts_list) == 1:
        return (full_city_name, np.nan)
    else:
        city, country = map(str.strip, parts_list)
        return (city, country)

def main():
    files_list = glob.glob(INPUT_FILE_NAMES_PATTERN)

    race_results_df = None
    for file_name in files_list:
        print("File {} processing start...".format(file_name))
        if '2013' in file_name:
            file_df = load_old_format_file_frame(file_name)
        else:
            file_df = load_new_format_file_frame(file_name)

        if file_df is not None:
            tpl_vars = {'name': file_name, 'rows': len(file_df)}
            print("File {name} has been processed. {rows} records found".format(**tpl_vars))
            if race_results_df is None:
                race_results_df = file_df
            else:
                race_results_df = race_results_df.append(file_df)

    if race_results_df is None:
        print("No results found!")
        return False

    print("Saving parsed results data into {}".format(OUTPUT_FILE_NAME))
    race_results_df.to_csv(OUTPUT_FILE_NAME, encoding='utf-8', index=False)
    print("Success!")

    return True

if __name__ == '__main__':
    result = main()
    exit_code = 0 if result else 1
    sys.exit(exit_code)
