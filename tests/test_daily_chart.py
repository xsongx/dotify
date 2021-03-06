import glob
import os
import csv, io
import unittest
from unittest.mock import patch

import pandas as pd
from pandas.util.testing import assert_frame_equal
import requests_mock

from dotify.top_songs import DailyChart
from dotify.resources.countries import countries


class TestDailyChart(unittest.TestCase):

    INVALID_COUNTRY_NAME = 'Xylophonia'
    VALID_COUNTRIES_LOOKUP = {
        'Abalonia': {'id': 1, 'abbrev': 'ab'},
        'Condominia': {'id': 2, 'abbrev': 'cd'},
        'Efravania': {'id': 3, 'abbrev': 'ef'},
    }
    VALID_DAILY_CHART_DATA_ROWS = [['Position', 'song', 'title'], [1, 'sorry', 'bieber']]
    EXPECTED_VALID_DAILY_CHART_DATAFRAME = pd.DataFrame(data={'song': 'sorry', 'title': 'bieber'}, index=pd.Index([1], name='Position'))

    COUNTRY_CODES_FOR_WHICH_DATA_IS_PRESENT = ['ab', 'cd']
    DAILY_CHART_BASE_URL = 'https://spotifycharts.com/regional/{}/daily/latest/download'

    VALID_COUNTRY_NAME_FOR_WHICH_NO_DATA_IS_PRESENT = 'Efravania'
    DAILY_CHART_URL_FOR_COUNTRY_CODE_FOR_WHICH_NO_DATA_IS_PRESENT = DAILY_CHART_BASE_URL.format('ef')

    VALID_COUNTRY_NAME_FOR_WHICH_DATA_IS_PRESENT = 'Abalonia'
    DAILY_CHART_URL_FOR_COUNTRY_CODE_FOR_WHICH_DATA_IS_PRESENT = DAILY_CHART_BASE_URL.format('ab')

    def tearDown(self):
        for file in glob.glob('tmp/*.csv'):
            os.remove(file)

    def _data_is_present_for_country_code(self, country_code):
        return country_code in self.COUNTRY_CODES_FOR_WHICH_DATA_IS_PRESENT

    def _extract_country_code_from_request(self, request):
        return request.path.split('/')[2]

    def _write_csv_rows(self, data_rows):
        string_io = io.StringIO()
        writer = csv.writer(string_io, quoting=csv.QUOTE_NONE, escapechar='')
        writer.writerows(data_rows)
        return string_io.getvalue()

    def _daily_chart_request_callback(self, request, context):
        country_code = self._extract_country_code_from_request(request)
        if self._data_is_present_for_country_code(country_code):
            context.status_code = 200
            context.headers['Content-Type'] = 'text/csv;charset=UTF-8'
            return self._write_csv_rows(self.VALID_DAILY_CHART_DATA_ROWS)

        context.status_code = 404
        context.headers['Content-Type'] = 'not a csv'
        return 'invalid data'

    @patch.dict(countries, values=VALID_COUNTRIES_LOOKUP, clear=True)
    def test_daily_chart_raises_key_error_for_invalid_country_name(self):
        self.assertRaises(KeyError, DailyChart, self.INVALID_COUNTRY_NAME)

    @patch.dict(countries, values=VALID_COUNTRIES_LOOKUP, clear=True)
    @requests_mock.mock()
    def test_daily_chart_empty_for_valid_country_code_where_no_data_is_present(self, mock_request):
        mock_request.get(
            self.DAILY_CHART_URL_FOR_COUNTRY_CODE_FOR_WHICH_NO_DATA_IS_PRESENT,
            text=self._daily_chart_request_callback
        )

        daily_chart = DailyChart(country_name=self.VALID_COUNTRY_NAME_FOR_WHICH_NO_DATA_IS_PRESENT)
        daily_chart.download()

        self.assertTrue(daily_chart.dataframe.empty)

    @patch.dict(countries, values=VALID_COUNTRIES_LOOKUP, clear=True)
    @requests_mock.mock()
    def test_daily_chart_for_valid_country_code_gives_correct_data(self, mock_request):
        mock_request.get(
            self.DAILY_CHART_URL_FOR_COUNTRY_CODE_FOR_WHICH_DATA_IS_PRESENT,
            text=self._daily_chart_request_callback
        )

        daily_chart = DailyChart(country_name=self.VALID_COUNTRY_NAME_FOR_WHICH_DATA_IS_PRESENT)
        daily_chart.download()

        assert_frame_equal(daily_chart.dataframe, self.EXPECTED_VALID_DAILY_CHART_DATAFRAME)
