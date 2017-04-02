# Moscow Marathon Stats

[Moscow Marathon](http://moscowmarathon.org/en/) is an annual marathon (42.195 km) that courses through the center of Moscow, Russia.

This repo contains combined, cleaned and anonymized results of this marathon for 2013-2016. You can find out these results at [data/all_results.csv](data/all_results.csv) file.

## Data sources

There are two datasources for past marathon results.

Results for *2014-2016* are available at official marathon site:
* http://moscowmarathon.org/en/moscowmarathon/2016/race-results/male-42km/
* http://moscowmarathon.org/en/moscowmarathon/2016/race-results/female-42km/
* http://2015.moscowmarathon.org/en/marathon/results-2015/42-km-men/
* http://2015.moscowmarathon.org/en/marathon/results-2015/42-km-women/
* http://2015.moscowmarathon.org/en/marathon/results/42-km-men/
* http://2015.moscowmarathon.org/en/marathon/results/42-km-women/

These results are available both in human and machine readable formats.

Results for *2013* are not available at official site, but you can get them from organizers parter site [newrunners.ru](https://newrunners.ru/) (pages are in Russian):
* http://newrunners.ru/race/moskovskij-marafon/past/results/?city=&gender=1&protocol=0&club=&distance=19&text=#mMenu
* http://newrunners.ru/race/moskovskij-marafon/past/results/?city=&gender=2&protocol=0&club=&distance=19&text=#mMenu

These results are available at human readable format only.

## How to fetch new data

You should install `Python 3` to use scripts from this repo.

```bash
# Python requirements installing
pip3 install -r requirements.txt

# Results loading from data sources
./input_data_loader.sh

# Loaded results processing and aggregation
./input_data_parser.py
```
