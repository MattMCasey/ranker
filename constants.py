from datetime import datetime
from pymongo import MongoClient
import pymongo

client = MongoClient()
db = client['fencing']
fencers = db['fencers']
results = db['results']
clubs = db['clubs']

season_cutoff = datetime(2017, 7, 15)
next_season = datetime(2018, 7, 15)

club_ids = [4160, 9986, 10033, 1745]

club_standards = {
'MOE FC' : 'MOE',
'MWFC' : 'MOE'
}

categories = [
# ['A', 'B'],
# ['C', 'D'],
# ['E', 'U'],
]

ages = [
# [1999, 2005],
# [2002, 2005],
# [2003, 2006],
# [2005, 2008],
# [2007, 2010]
[2004, 2018],
[1900, 2003]
]

weapons = [
'Foil',
'Epee',
'Saber'
]

months = {
    1:'January',
    2:'February',
    3:'March',
    4:'April',
    5:'May',
    6:'June',
    7:'July',
    8:'August',
    9:'September',
    10:'October',
    11:'November',
    12:'December'
}

month_to_num = {
    'January':1,
    'February':2,
    'March':3,
    'April':4,
    'May':5,
    'June':6,
    'July':7,
    'August':8,
    'September':9,
    'October':10,
    'November':11,
    'December':12
}

year_to_name = {
1999: 'Junior',
2002: 'Cadet',
2003: 'Y14',
2005: 'Y12',
2007: 'Y10',
2004: 'Youth',
1900: 'Senior'
}

cat_to_string = {
'A' : 'A + B',
'C' : 'C + D',
'E' : 'E + U'
}

sub = {'_id': 'No Competitor',
        'events': 0,
        'total': 0}
