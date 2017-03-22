import scrapy
import urllib.parse as up


class HumanReadableResulsSpider(scrapy.Spider):
    name = 'Moscow Marathon 2013 results'
    start_urls = [
        'http://newrunners.ru/race/moskovskij-marafon/past/results/?city=&gender=1&protocol=0&club=&distance=19&text=',
        'http://newrunners.ru/race/moskovskij-marafon/past/results/?city=&gender=2&protocol=0&club=&distance=19&text=',
    ]

    GENDER_LIST = {
        1: 'Male',
        2: 'Female',
    }

    def parse(self, response):
        result_gender = self._get_gender(response.url)
        for result_item in response.css('.result-list li'):
            name_raw = result_item.css('.name .title a::text').extract_first().strip()
            age_raw = result_item.css('.info .age::text').extract_first()
            city_raw = result_item.css('.info .city_link::text').extract_first()
            result_raw = result_item.css('.result::text').extract_first()
            bib_raw = result_item.css('.id::text').extract_first()
            gender_position_raw = result_item.css('.number span::text').extract_first()
            absolute_position_raw = result_item.css('.number span.from::text').extract_first()

            yield {
                'name': self._get_cleaned_text(name_raw),
                'result': self._get_cleaned_text(result_raw),
                'age': self._get_cleaned_age(age_raw),
                'city': self._get_cleaned_text(city_raw),
                'gender': result_gender,
                'gender_position': self._get_cleaned_text(gender_position_raw),
                'absolute_position': self._get_cleaned_text(absolute_position_raw),
                'number': self._get_cleaned_int(bib_raw),
            }

        next_page = response.css('.result-content .result-pages a.next::attr(href)').extract_first()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def _get_gender(self, source_url):
        o = up.urlparse(source_url)
        query_params = up.parse_qs(o.query)
        if not query_params or ('gender' not in query_params):
            return 'Error'

        num_gender_values = len(query_params['gender'])
        if num_gender_values != 1:
            return 'Error'

        gender_code = int(query_params['gender'][0])
        if gender_code in self.GENDER_LIST:
            return self.GENDER_LIST[gender_code]
        else:
            return 'Unknown'

    def _get_cleaned_age(self, value):
        value = value.replace(' years', '')
        return self._get_cleaned_int(value)

    def _get_cleaned_int(self, value):
        value_cleaned = self._get_cleaned_text(value)
        return int(value_cleaned)

    def _get_cleaned_text(self, text):
        if text:
            return text.strip()
        else:
            return None

    def _get_cleaned_bool(self, value):
        return value is not None
