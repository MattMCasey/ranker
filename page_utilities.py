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
from constants import *

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

def month_getter(month, year):
        if type(month) == str: #or type(month) == unicode:
            month = month_to_num[month]
        month = int(month)
        year = int(year)
        #:print('month', month, 'year', year)
        #print('month', type(month), 'year', type(year))
        start = datetime(year, month, 1)
        endmonth = month + 1
        endyear = year

        if endmonth > 12:
            endmonth -= 12
            endyear += 1
        end = datetime(endyear, endmonth, 1)
        return start, end

def pull_month(club, weapons, month, year):
    start, end = month_getter(month, year)
    #print('XXXXXXXX\n\n\n\n', month)
    # if type(month) == str or type(month) == unicode:
    #     month = month_to_num[month]
    # month = int(month)
    # year = int(year)
    # #:print('month', month, 'year', year)
    # print('month', type(month), 'year', type(year))
    # start = datetime(year, month, 1)
    # endmonth = month + 1
    # endyear = year
    #
    # if endmonth > 12:
    #     endmonth -= 12
    #     endyear += 1
    # end = datetime(endyear, endmonth, 1)
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
    #print(month, months)
    return month, agg

def club_points(club, start=season_cutoff, end=next_season):

    pipeline = [
    {
    '$match':{
    '$and': [
        { 'date': { '$gte': start } },
        { 'date': { '$lt': end } }
    ]
} },
    {'$group': {
        '_id': '$club',
        'total': {
            '$sum': "$total"
        }
    } }
    ]
    for result in results.aggregate(pipeline):
        return result['total']

def club_points_month(club, month, year):
    start, end = month_getter(month, year)
    return club_points(club, start, end)

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
        mnth, agg = pull_month_winners(club, weapons, lmonth, lyear)
        points = club_points_month(club, lmonth, lyear)
        month_list.append((mnth, agg, points))
        #print((mnth, agg))
        # month, agg = pull_month_winners(club, weapons, lmonth, lyear)

        # month_list.append((month, agg))
    # for thing in month_list:
    #     for other_thing in thing:
    #         for yet_another_thing in other_thing:
    #             print(yet_another_thing, '\n')

    #print(month_list)

    return month_list
