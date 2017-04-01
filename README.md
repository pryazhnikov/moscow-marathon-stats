# Moscow Marathon Stats

[Moscow Marathon](http://moscowmarathon.org/en/) is an annual marathon (42.195 km) that courses through the center of Moscow, Russia.

This repo contains combined, cleaned and anonymized results of this marathon for 2013-2016. You can find out these results at [data/all_results.csv](moscow-marathon-stats/blob/master/data/all_results.csv) file.

## Data sources

There are two datasources for past marathon results.

Results for 2014-2016 are available at official marathon site (it's even possible to load these results in machine readable format):
* http://moscowmarathon.org/en/moscowmarathon/2016/race-results/male-42km/
* http://moscowmarathon.org/en/moscowmarathon/2016/race-results/female-42km/
* http://2015.moscowmarathon.org/en/marathon/results-2015/42-km-men/
* http://2015.moscowmarathon.org/en/marathon/results-2015/42-km-women/
* http://2015.moscowmarathon.org/en/marathon/results/42-km-men/
* http://2015.moscowmarathon.org/en/marathon/results/42-km-women/

Results for 2013 are not available at official site, but you can get them from organizers parter site [newrunners.ru](https://newrunners.ru/) (pages are in Russian):
* http://newrunners.ru/race/moskovskij-marafon/past/results/?city=&gender=1&protocol=0&club=&distance=19&text=#mMenu
* http://newrunners.ru/race/moskovskij-marafon/past/results/?city=&gender=2&protocol=0&club=&distance=19&text=#mMenu

These results are available at human readable format only.

# How to fetch new data

> pip3 install -r requirements.txt
> ./input_data_loader.sh
> ./input_data_parser.py
