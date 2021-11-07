import os
cate_list=['ANDROID_WEAR', 'ART_AND_DESIGN', 'AUTO_AND_VEHICLES', 'BEAUTY',
'BOOKS_AND_REFERENCE',
'BUSINESS',
'COMICS',
'COMMUNICATION',
'DATING',
'EDUCATION',
   'ENTERTAINMENT',
   'EVENTS',
   'FINANCE',
   'FOOD_AND_DRINK',
   'HEALTH_AND_FITNESS',
   'HOUSE_AND_HOME',
   'LIBRARIES_AND_DEMO',
  'LIFESTYLE',
   'MAPS_AND_NAVIGATION',
   'MEDICAL',
   'MUSIC_AND_AUDIO',
   'NEWS_AND_MAGAZINES',
   'PARENTING',
   'PERSONALIZATION',
   'PHOTOGRAPHY',
   'PRODUCTIVITY',
   'SHOPPING',
   'SOCIAL',
   'SPORTS',
   'TOOLS',
   'TRAVEL_AND_LOCAL',
   'VIDEO_PLAYERS',
   'WEATHER',]

script="var gplay = require('google-play-scraper');\
const util = require('util');\
a=gplay.list({\
    category: gplay.category.$,\
    collection: gplay.collection.TOP_FREE,num: 500}).then((value) => {\
    console.log(util.inspect(value, { maxArrayLength: null }))});"
for cat in cate_list:
	content=script.replace("$",cat)
	f=open("top_list.js","w")
	f.write(content)
	f.close()
	os.system("node top_list.js > "+cat+".json")
