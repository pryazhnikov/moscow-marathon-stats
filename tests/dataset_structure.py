import unittest
import os.path
import pandas as pd
import re


class DatasetStructureTest(unittest.TestCase):
    VALID_GENDERS = ['Female', 'Male']

    def get_dataset_file(self):
        current_dir = os.path.dirname(__file__)
        return os.path.realpath(current_dir + '/../data/all_results.csv')

    def load_dataset(self):
        file_name = self.get_dataset_file()
        return pd.read_csv(file_name)

    def test_dataset_is_exist(self):
        df_file = self.get_dataset_file()
        self.assertIsNotNone(df_file, "Input file cannot be empty")

        is_file = os.path.isfile(df_file)
        self.assertTrue(is_file, "{} is not a regular file".format(df_file))

    def test_is_csv(self):
        df = self.load_dataset()
        self.assertIsNotNone(df, "Cannot load dataframe from file")

    def test_each_row_has_mandatory_values(self):
        df = self.load_dataset()
        for column in ('year', 'gender', 'status'):
            series = df[column]
            nan_values = df[series.isnull()]
            fail_message = "No records without {name} expected!".format(name=column)
            self.assertEqual(0, len(nan_values), fail_message)

    def test_each_row_has_valid_gender(self):
        df = self.load_dataset()
        found_genders = df['gender']
        unknown_genders = found_genders[~found_genders.isin(self.VALID_GENDERS)].unique()
        unknown_genders_str = ", ".join(unknown_genders)
        self.assertEqual(0, len(unknown_genders), "Unknown genders found: " + unknown_genders_str)

    def test_verify_finish_time(self):
        df = self.load_dataset()
        filter_is_finished = (df['status'] == 'Finished')
        filter_no_finish_time = df['resultTime'].isnull()
        finishers_without_finish_time = df[filter_is_finished & filter_no_finish_time]
        self.assertEqual(0, len(finishers_without_finish_time), "Each finisher should have finish time")

        non_finishers_with_finish_time = df[~filter_is_finished & ~filter_no_finish_time]
        self.assertEqual(0, len(non_finishers_with_finish_time), "Non finishers should not have finish time")

    def test_each_year_has_data_for_all_valid_gender(self):
        expected_genders = sorted(self.VALID_GENDERS)

        df = self.load_dataset()
        years_list = df['year'].unique()
        for year in sorted(years_list):
            year_data = df[df['year'] == year]
            year_genders = sorted(year_data['gender'].unique())
            fail_message = "Wrong genders found for year " + str(year)
            self.assertEqual(expected_genders, year_genders, fail_message)

    def test_gender_positions(self):
        df = self.load_dataset()
        years_list = sorted(df['year'].unique())
        for year in years_list:
            for gender in self.VALID_GENDERS:
                finishers = df[(df['year'] == year) & (df['gender'] == gender) & (df['status'] == 'Finished')]
                finishers_count = len(finishers)

                gender_positions = finishers['genderPosition'].dropna()
                positions_count = len(gender_positions)
                unique_positions_count = len(gender_positions.unique())

                info_args = {'year': year, 'gender': gender}
                fail_message = "Wrong number of filled gender positions ({year}, {gender})".format(**info_args)
                self.assertEqual(finishers_count, positions_count, fail_message)

                fail_message = "Wrong number of unique gender positions ({year}, {gender})".format(**info_args)
                self.assertGreaterEqual(finishers_count, unique_positions_count, fail_message)

    def test_country_should_be_trimmed(self):
        df = self.load_dataset()
        unique_countries = df['country'].dropna().unique()
        self.assert_trimmed_names(unique_countries, "Non trimmed countries found")

    def test_city_should_be_trimmed(self):
        df = self.load_dataset()
        unique_cities = df['city'].dropna().unique()
        self.assert_trimmed_names(unique_cities, "Non trimmed countries found")

    def assert_trimmed_names(self, values_list, fail_prefix):
        failed_names_list = self.get_non_trimmed_names(values_list)
        failed_names_count = len(failed_names_list)
        fail_message = "{}: {}".format(fail_prefix, failed_names_list)
        self.assertEqual(0, failed_names_count, fail_message)

    def get_non_trimmed_names(self, names_list):
        name_serie = pd.Series(names_list)
        bad_filter = name_serie.str.startswith(' ') | name_serie.str.endswith(' ')
        return name_serie[bad_filter].values

    def test_country_should_not_have_duplicates(self):
        df = self.load_dataset()
        unique_countries = df['country'].dropna().unique()
        countries_hash = map(self.get_name_hash, unique_countries)
        country_series = pd.Series(unique_countries, index=countries_hash)

        country_counters = country_series.groupby(country_series.index.tolist()).count()
        duplicated_hashes = country_counters[country_counters > 1].index.tolist()
        duplicated_countries = country_series.loc[duplicated_hashes].tolist()

        failed_names_count = len(duplicated_countries)
        fail_message = "Duplicated countries found: {}".format(duplicated_countries)
        self.assertEqual(0, failed_names_count, fail_message)

    def test_country_names_should_not_use_latin_symbols(self):
        df = self.load_dataset()
        unique_cities = df['country'].dropna().unique()
        unique_cities = pd.Series(unique_cities)

        latin_names_filter = unique_cities.str.match(r'[a-z]', flags=re.IGNORECASE)
        latin_city_names = unique_cities[latin_names_filter]

        failed_names_count = len(latin_city_names)
        fail_message = "Non latin country names found: {}".format(latin_city_names.values)
        self.assertEqual(0, failed_names_count, fail_message)

    def test_city_should_not_have_duplicates(self):
        df = self.load_dataset()
        unique_cities = df['city'].dropna().unique()
        cities_hash = map(self.get_name_hash, unique_cities)
        city_series = pd.Series(unique_cities, index=cities_hash)

        city_counters = city_series.groupby(city_series.index.tolist()).count()
        duplicated_hashes = city_counters[city_counters > 1].index.tolist()
        duplicated_cities = city_series.loc[duplicated_hashes].tolist()

        failed_names_count = len(duplicated_cities)
        fail_message = "Duplicated cities found: {}".format(duplicated_cities)
        self.assertEqual(0, failed_names_count, fail_message)

    def get_name_hash(self, name):
        name_hash = str(name)
        name_hash = name_hash.lower()
        name_hash = name_hash.replace(' ', '')
        name_hash = name_hash.replace("\'", '')
        return name_hash

    def test_city_should_not_be_uppercase(self):
        df = self.load_dataset()
        unique_cities = df['city'].dropna().unique()
        unique_cities = pd.Series(unique_cities)

        upper_case_cities = unique_cities[unique_cities == unique_cities.str.upper()]

        failed_names_count = len(upper_case_cities)
        fail_message = "Uppercase city names found: {}".format(upper_case_cities.values)
        self.assertEqual(0, failed_names_count, fail_message)


if __name__ == '__main__':
    unittest.main()
