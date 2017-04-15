import unittest
import os.path
import pandas as pd


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

if __name__ == '__main__':
    unittest.main()
