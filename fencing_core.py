from pymongo import MongoClient
import pymongo
import requests
import time
from bs4 import BeautifulSoup
import numpy as np
import datetime as dt
import pandas as pd
import math
from datetime import datetime
import time
from collections import Counter, defaultdict

client = MongoClient()
db = client['fencing']
fencers = db['fencers']
results = db['results']

season_cutoff = datetime(2017, 7, 15)
next_season = datetime(2018, 7, 15)

categories = [
['A', 'B'],
['C', 'D'],
['E', 'U'],
]

ages = [
[1999, 2005],
[2002, 2005],
[2003, 2006],
[2005, 2008],
[2007, 2010]
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
}

cat_to_string = {
'A' : 'A + B',
'C' : 'C + D',
'E' : 'E + U'
}

sub = {'_id': 'No Competitor',
        'events': 0,
        'total': 0}

def award_points(place, size):
    """
    place and size are intergers
    calculates points from fencing events based
    on final standing and #rounds survived
    returns base and bonus as two separate numbers
    """

    place = int(place)
    size = int(size)

    bonus_max = int(math.log(size, 2)) + 1

    if math.log(place, 2) == int(math.log(place, 2)):
        bracket = int(math.log(place , 2))
    else:
        bracket = int(math.log(place , 2)) + 1

    bonus = (bonus_max - bracket)*2
    if bonus < 0:
        bonus = 0
    base = size-place + 1

    return bonus, base


def extract_details(line):
    """
    Takes a line from a Beautiful Soup object.
    While it's fed new information, returns nothing, just updates database
    Returns False when it encounters a dubplicate record
    """
    line = str(line).split('<')

    date = line[2][-10:]
    date = datetime.strptime(date, '%m/%d/%Y')
    event = line[8][27:]
    event_rating = line[10][-2:]
    name = line[15][4:]


    url_tourney = line[5] #gets line containing url and tournament name
    url = url_tourney[8:]
    url_end = url.index('"')
    event_start = url_tourney.index('>')+1 #prepping line for extract

    url = url[:url_end] #extracting url and event
    tourney = url_tourney[event_start:]


    place_size = line[12] #gets line w/place & size

    ps_start = place_size.index('>')+1 #prepping line for extract
    ps_splits = place_size[ps_start:].split(' ')

    size = ps_splits[2] #extracting
    place = ps_splits[0][:-2]

    club = line[20]
    club_start = club.index('>') + 1
    club = club[club_start:]

    new_rating = line[28]
    new_rating_start = new_rating.index('>') + 1
    new_rating = new_rating[new_rating_start:]

    weapon = 'Saber'
    if 'Epee' in event:
        weapon = 'Epee'
    elif 'Foil' in event:
        weapon = 'Foil'

    bonus, base = award_points(place, size)

    print(name, event, place)

    try:
        results.insert_one({
        'date':date,
        'tourney':tourney,
        'event_rating':event_rating,
        'name':name,
        'event':event,
        'weapon':weapon,
        'place':place,
        'size':size,
        'club':club,
        'url':url,
        'new_rating': new_rating,
        'bonus':bonus,
        'base': base,
        'total': bonus + base
        })
    except:
        return False


def scrape_page(num, club_id):

    """
    Num and club_id are both intergers
    Has no output as long as extract_details encounters new records
    Returns False when extract_details returns False
    """


    page = '''https://askfred.net/Results/search.php?
    ops%5Bfirst_name%5D=first_name&vals%5Bfirst_name%5D=&ops%
    5Blast_name%5D=last_name&vals%5Blast_name%5D=&f%5Bweapon%5D=&ops%
    5Bdate_1%5D=date_1_eq&vals%5Bdate_1%5D=&ops%5Bdate_2%
    5D=date_2_eq&vals%5Bdate_2%5D=&f%5Bclub_id%5D='''+str(club_id)+'''&f%
    5Bcompetitor_division_id%5D=&ops%5Bplace%5D=place_eq&vals%
    5Bplace%5D=&f%5Bevent_gender%5D=&f%5Bage_limit%5D=&f%
    5Bevent_rating_limit%5D=&ops%5Bevent_rating%5D=event_rating_eq&vals%
    5Bevent_rating%5D=&f%5Bis_team%5D=&ops%5Brating_earned%
    5D=eq&vals%5Brating_earned_letter%5D=&vals%5Brating_earned_year%
    5D=&f%5Btournament_name_contains%5D=&search_submit=
    Search&page_id=2&page_id=3&page_id=4&page_id=3&page_id=2&page_id='''+str(num)

    raw = requests.get(page)
    souped = BeautifulSoup(raw.content, 'html.parser')
    evens = souped.select('tr.evenrow')
    odds = souped.select('tr.oddrow')

    for i in range(len(odds)):
        try:
            extract_details(evens[i])
            extract_details(odds[i])
        except:
            return False

def update_club(club_id):
    """
    club_id is an interger
    this drives the update process
    returns Updated when extract_details and scrape_page return False
    """
    for i in range(1, 25):
        print(i)
        if scrape_page(i, club_id) == False:
            return "Updated"

def pull_club(club_set, weapon_set, start_date = season_cutoff, end_date = next_season):
    """
    club_set and weapon_set are str or list
    returns mongo aggregate of all fencers for the club ordered by total points
    """

    if type(club_set) != list:
        club_set = [club_set]

    if type(weapon_set) != list:
        weapon_set = [weapon_set]

    filt = [
        {"$match": {
        "club": {'$in' : club_set}}},
        {"$match": {
        "date": {'$gte' : start_date,
                '$lt': end_date}}},
        {"$match": {
        "weapon": {'$in' : weapon_set}}},

        {"$group":
            {
                "_id": "$name",
                "events": {"$sum": 1},
                "base" : {"$sum":{"$sum": "$base"}},
                "bonus" : {"$sum":{"$sum": "$bonus"}},
                "total" : {"$sum":{"$sum": "$total"}}
            }},

        {"$sort": {"total": -1} }
        ]
    return list(results.aggregate(filt))

def create_fencers(list_of_names, club):

    if type(list_of_names) != list:
        list_of_names = list(list_of_names)

    tgtCols = ['Last Name',
                         'First Name',
                         'Birthdate',
                         'Birthdate verified',
                         'Club 1 Name',
                         'Club 1 Abbreviation',
                         'Club 1 ID#',
                         'Club 2 Name',
                         'Club 2 Abbreviation',
                         'Club 2 ID#',
                         'Member #',
                         'Member Type',
                         'Competitive',
                         'Expiration',
                         'Saber',
                         'Epee',
                         'Foil']


    membershipeoy = pd.read_csv('EOY-2017.csv')
    membershipcrnt = pd.read_csv('current_members.csv')
    membership = pd.merge(membershipeoy, membershipcrnt, on=tgtCols, how='outer')
    membership = membership[['Last Name',
                             'First Name',
                             'Birthdate',
                             'Birthdate verified',
                             'Club 1 Name',
                             'Club 1 Abbreviation',
                             'Club 1 ID#',
                             'Club 2 Name',
                             'Club 2 Abbreviation',
                             'Club 2 ID#',
                             'Member #',
                             'Member Type',
                             'Competitive',
                             'Expiration',
                             'Saber',
                             'Epee',
                             'Foil']]
    membership = membership.set_index(['Last Name', 'First Name'])
    membership = membership.dropna(thresh=11)

    for name in list_of_names:
        lastFirst = name.split(',')
        #print(name)
        #print(lastFirst)
        #print(lastFirst)
        first = lastFirst[1][1:]
        if first == 'Alex':
            first = 'Alexander'
        last = lastFirst[0]
        #print(last)

        try:
            truncated = membership.loc[last, first]

            #print(len(truncated))

            if len(truncated) > 1:
                truncated = truncated.iloc[0]
                byear = truncated[0]
            else:
                byear = truncated['Birthdate'][0]

            if type(byear) == str:
                byear = byear[-4:]

            byear = int(byear)

            foil = truncated['Foil'][0][:1]
            saber = truncated['Saber'][0][:1]
            epee = truncated['Epee'][0][:1]

            #print(byear)
            fencers.insert_one({
            'name': name,
            'byear': byear,
            'foil': foil,
            'saber': saber,
            'epee': epee
            })

        except:
            print('Error on', name)

def rating_groups(category, weapon, fencers_list):
    """
    category = list
    weapon = str
    fencers_list = list
    returns a dict of
    """

    current = []

    for fencer in fencers_list:
        try:
            name = fencer['_id']
            record = fencers.find_one({'name': name})
            rating = record[weapon]

            if rating in category:
                current.append(fencer)
        except:
            pass

    while len(current) > 0 and len(current) < 3:
        current.append(sub)

    return current

def pull_fencer(fencer):
    """
    Takes a fencer (string), returns all results for fencer.
    """
    last, first = fencer.split(',')
    firstLast = first[1:] + ' ' + last

    # {'date': {'$gte': season_cutoff}},

    temp = list(results.find({'name':fencer, 'date': {'$gte': season_cutoff}},
                         {'_id':0,
                         'date': 1,
                         'tourney': 1,
                         'event':1,
                         'place': 1,
                         'size': 1,
                          'place': 1,
                          'base': 1,
                          'bonus':1,
                          'total':1,
                          'url':1
                         } ))

    for fencer in temp:
        tdate = fencer['date']
        fencer['date'] = str(tdate.month) + '/' + str(tdate.day) + '/' + str(tdate.year)

    return firstLast, temp

def age_groups(category, fencers_list):
    """
    category = age group, a list of intergers
    fencers_list = a mongo aggregate of all fencers for the club ordered by total points
    returns a list of dicts. Each dict contains a fencer's aggregate details
    """

    current = []

    for fencer in fencers_list:
        try:
            name = fencer['_id']
            record = fencers.find_one({'name': name})
            byear = record['byear']

            if byear >= category[0] and byear <= category[1]:
                current.append(fencer)
        except:
            pass

    while len(current) > 0 and len(current) < 3:
        current.append(sub)

    #print(current, '\n')
    return current

def pull_month_winners(club, weapons, month, year):
    """
    club is a string or list
    weapons is a list
    returns a list of dicts
    """
    #month = datetime.today().month - 1
    #year = datetime.today().year

    endmonth = month +1
    endyear = year
    if endmonth == 13:
        endmonth -= 1
        endyear += 1

    start = datetime(year, month, 1)
    end = datetime(endyear, endmonth, 1)
    agg = []
    for weapon in weapons:
        temp = []
        for cat in categories:
            raw = pull_club(club, weapon, start_date = start, end_date = end)
            try:
                temp.append([cat_to_string[cat[0]], weapon, rating_groups(cat, weapon.lower(), raw)[0]])
            except:
                temp.append([cat_to_string[cat[0]], weapon, sub])




        for age in ages:
            raw = pull_club(club, weapon, start_date = start, end_date = end)
            try:
                temp.append([year_to_name[age[0]], weapon, age_groups(age, raw)[0]])
            except IndexError:
                temp.append([year_to_name[age[0]], weapon, sub])

        agg.append(temp)

    return months[month], agg

def season_leaders(club, weapons=['Foil', 'Epee', 'Saber']):
    col_width = 12 / len(weapons)

    # sub = {'_id': 'No Competitor',
    #         'events': 0,
    #         'total': 0}

    agg = []

    for weapon in weapons:
        temp = []
        for cat in categories:
            raw = pull_club(club, weapon)
            filtered = rating_groups(cat, weapon.lower(), raw)

            if len(filtered) > 0:
                temp.append([cat_to_string[cat[0]], weapon, filtered[0:3]])


        # while len(temp) < 3:
        #     temp.append([cat_to_string[cat[0]], weapon, sub])


        #if len(temp) > 0:
            #rating_output.append(temp)
            #agg.append(temp)

        #temp = []

        for age in ages:
            raw = pull_club(club, weapon)
            filtered = age_groups(age, raw)
            if len(filtered) > 0:
                temp.append([year_to_name[age[0]], weapon, filtered[0:3]])

        # while len(temp) < 6:
        #     temp.append([year_to_name[age[0]], weapon, sub])

        #print(temp, '\n')
        if len(temp) > 0:
            #age_output.append(temp)
            agg.append(temp)

    #print(agg)
    return int(col_width), agg

def pull_month(club, weapons, month, year):
    #print('XXXXXXXX\n\n\n\n', month)
    if type(month) == str or type(month) == unicode:
        month = month_to_num[month]
    month = int(month)
    year = int(year)
    #:print('month', month, 'year', year)
    print('month', type(month), 'year', type(year))
    start = datetime(year, month, 1)
    endmonth = month + 1
    endyear = year

    if endmonth > 12:
        endmonth -= 12
        endyear += 1
    end = datetime(endyear, endmonth, 1)
    #print(end)
    agg = []

    for weapon in weapons:
        temp = []
        for cat in categories:
            raw = pull_club(club, weapon, start, end)
            filtered = rating_groups(cat, weapon.lower(), raw)

            if len(filtered) > 0:
                temp.append([cat_to_string[cat[0]], weapon, filtered])

        for age in ages:
            raw = pull_club(club, weapon, start, end)
            filtered = age_groups(age, raw)

            if len(filtered)> 0:
                temp.append([year_to_name[age[0]], weapon, filtered])

        if len(temp) > 0:
            agg.append(temp)

    return months[month], agg

def month_by_month(club):
    """
    club is string or int
    output is list of dicts
    """
    weapons = results.find({'club' : club}).distinct('weapon')
    span = (datetime.today().year - season_cutoff.year) * 12 + (datetime.today().month - season_cutoff.month)
    month_list = []

    year = season_cutoff.year
    month = season_cutoff.month

    for i in range(span, 0, -1):
        this_month = []
        lyear = year
        lmonth = month + i
        if lmonth > 12:
            lmonth -= 12
            lyear += 1

        #print(pull_month_winners(club, weapons, 2017, 11), year, month)
        month_list.append(pull_month_winners(club, weapons, lmonth, lyear))
    for thing in month_list:
        for other_thing in thing:
            for yet_another_thing in other_thing:
                print(yet_another_thing, '\n')

    print(month_list)

    return month_list
