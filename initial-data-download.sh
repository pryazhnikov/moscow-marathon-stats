#!/bin/bash

DATA_DIR=./data/temporary
CURL=`which curl`
SCRAPY=`which scrapy`

# 2016
$CURL 'http://moscowmarathon.org/media/filer_public/16/20160925_mosmarathon_m_42km.json' > $DATA_DIR/2016_male_42km.json
$CURL 'http://moscowmarathon.org/media/filer_public/16/20160925_mosmarathon_f_42km.json' > $DATA_DIR/2016_female_42km.json

# 2015
$CURL 'http://2015.moscowmarathon.org/static/protocols/2015/moscowmarathon/42km-men.json' > $DATA_DIR/2015_male_42km.json
$CURL 'http://2015.moscowmarathon.org/static/protocols/2015/moscowmarathon/42km-women.json' > $DATA_DIR/2015_female_42km.json

# 2014
$CURL 'http://2015.moscowmarathon.org/static/protocols/42km-male.json' > $DATA_DIR/2014_male_42km.json
$CURL 'http://2015.moscowmarathon.org/static/protocols/42km-female.json' > $DATA_DIR/2014_female_42km.json

# 2013
# There is no machine readable results for this year
$SCRAPY runspider scripts/human-results-loader.py -o $DATA_DIR/2013_42km.json
