import requests
import time
from bs4 import BeautifulSoup
import numpy as np
import datetime as dt
import pandas as pd
import math
from datetime import datetime, date, timedelta
import time
from collections import Counter, defaultdict
from constants import *


def award_points(place, size):
    """
    place = int, the final place that the fencer finished in
    size = int, the number of fencers in the event
    
    calculates the points awarded to a fencer based on their
    final standing, the number of victories they achieved
    and the number of fencers in the tournament
    
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
    line = Beautiful Soup object, a line from AskFred.net
    
    Extracts details form AskFred lines and enters them into the
    results database
    
    Returns nothing as its fed new information.
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
    if club in club_standards:
        club = club_standards[club]

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

    if results.find_one({'date': date, 'name':name, 'tourney':tourney, 'event':event }) == None:

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
    else:
        print(club, "updated")
        return False


def scrape_page(num, club_id):

    """
    num = int, the number of the page to be scraped
    club_id = int, the club's unqiue identifier
    
    Has no return as long as extract_details encounters new records
    
    Returns False when extract_details returns False
    """

    page = '''https://askfred.net/Results/search.php?
    ops%5Bfirst_name%5D=first_name&vals%5Bfirst_name%5D=&ops%
    5Blast_name%5D=last_name&vals%5Blast_name%5D=&f%5Bweapon%5D=&ops%
    5Bdate_1%5D=date_1_eq&vals%5Bdate_1%5D=&ops%5Bdate_2%
    5D=date_2_eq&vals%5Bdate_2%5D=&f%5Bclub_id%5D=''' + str(club_id) + '''&f%
    5Bcompetitor_division_id%5D=&ops%5Bplace%5D=place_eq&vals%
    5Bplace%5D=&f%5Bevent_gender%5D=&f%5Bage_limit%5D=&f%
    5Bevent_rating_limit%5D=&ops%5Bevent_rating%5D=event_rating_eq&vals%
    5Bevent_rating%5D=&f%5Bis_team%5D=&ops%5Brating_earned%
    5D=eq&vals%5Brating_earned_letter%5D=&vals%5Brating_earned_year%
    5D=&f%5Btournament_name_contains%5D=&search_submit=
    Search&page_id=2&page_id=3&page_id=4&page_id=3&page_id=2&page_id=''' + str(num)

    raw = requests.get(page)
    souped = BeautifulSoup(raw.content, 'html.parser')
    evens = souped.select('tr.evenrow')
    odds = souped.select('tr.oddrow')

    for i in range(len(odds)):
        try:
            if extract_details(evens[i]) == False or extract_details(odds[i]) == False:
                print("scrape_page try")
                return False
        except:
            print("scrape_page except")
            return False

def update_club_results(club_id):
    """
    club_id = int, the club's unique identifier
    
    returns Updated when extract_details and scrape_page return False
    """
    for i in range(1, 25):
        print(i)
        if scrape_page(i, club_id) == False:
            print("Updated")
            break



def create_fencers(list_of_names, club):
    """
    list_of_names = list, the list of fencers' names
    club = str, the club that the fencers belong to
    
    Extracts details of the fencers from the USA Fencing membership roster
    and enters them into the database
    
    Returns nothing, prints the name of the fencer if detail extraction fails
    """
    
    #Converts a single name to a list
    if type(list_of_names) != list:
        list_of_names = list(list_of_names)
    
    #For later DataFrame trimming
    tgtCols = [
                    'Last Name',
                     'First Name',
                     'Birthdate',
                     'Birthdate verified',
                     'Club 1 Name',
                     'Club 1 Abbreviation',
                     'Club 1 ID#',
                     'Club 2 Name',
                     'Club 2 Abbreviation',
                     'Club 2 ID#',
                     'Gender',
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
    membership = membership[tgtCols]
    membership = membership.set_index(['Last Name', 'First Name'])
    membership = membership.dropna(thresh=11)

    for name in list_of_names:
        lastFirst = name.split(',')
        #print(name)
        #print(lastFirst)
        #print(lastFirst)
        first = lastFirst[1][1:]
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
            
            #Handling inconsistent formatting from source doc
            if type(byear) == str:
                byear = byear[-4:]

            byear = int(byear)
            gender = truncated['Gender'][0]
            foil = truncated['Foil'][0][:1]
            saber = truncated['Saber'][0][:1]
            epee = truncated['Epee'][0][:1]

            #print(byear)
            fencers.insert_one({
            'gender' : gender,
            'name': name,
            'byear': byear,
            'foil': foil,
            'saber': saber,
            'epee': epee
            })

        except:
            print('Error on', name)

def daily_updater():
    """
    This function runs from the __name__ == '__main__' input
    It sits in a screen and checks for new results once per day
    
    No input, no return
    """
    print('updating')
    
    for club_id in club_ids:
        update_club_results(club_id)
    
    yesterday = datetime.today() - timedelta(5)
    
    for club in results.find({'date': {'$gte': yesterday}}).distinct('club'):
        fencers = results.find({'club': club, 'date': {'$gte': yesterday}}).distinct('name')
        create_fencers(fencers, club)
    
    print('update completed at', datetime.today())

    while True:
        
        hour = datetime.today().hour
        trigger_hour = 8
        
        print('hour:', hour, 'trigger hour:', trigger_hour)
        
        if hour == trigger_hour:
            print('updating')
            
            for club_id in club_ids:
                update_club_results(club_id)
            
            yesterday = datetime.today() - timedelta(5)
            
            for club in results.find({'date': {'$gte': yesterday}}).distinct('club'):
                fencers = results.find({'club': club, 'date': {'$gte': yesterday}}).distinct('name')
                create_fencers(fencers, club)
            
            print('update completed at', datetime.today())
            time.sleep(60**2)
            
        else:
            print('awaiting next update')
            time.sleep(60**2)

def create_club(club):
    """
    club = str, the club's name
    
    creates a default club entry in the club preferences database
    """
    month_dict = {month:0 for month in months_3}

    clubs.insert_one({
    'name':club, #to be str
    'club_ids':None, #list of ints
    'age_groups':[], #list of two-item lists - [[int1, int2], [int3, int4]]
    'age_group_names':{}, #dict with lower year in age range and name - {int1:'junior', int3:'senior'}
    'rating_groups':[], #list of lists with ratings in them
    'rating_group_names':{}, #dict of lowest rating in category to cat name
    'excluded_fencers':[], #list of strings, names of fencers not included in ladder
    'club_goals':month_dict #dict, months = keys, int = goal - {month:goal, month: goal}
    })

def stage_update(club, posted, delete=False):
    """
    club = str, club's name
    posted = dict, dictionary of updates for club preferences
    delete = boolean
    
    updates the club's preferences in the database
    """
    fields = ['age_groups', 'age_group_names', 'rating_groups',
                'excluded_fencers', 'club_goals']
    keys = list(posted.keys())
    club_dict = clubs.find_one({'name':club})

    print(posted)

    if 'delete' in keys:
        delete = True

    if 'year1' in keys:
        field1 = fields[0]
        years = [ posted['year1'], posted['year2'] ]
        for year in years:
            year = int(year)
        years.sort()
        for year in years:
            year = str(year)


        new_group = [years]
        print(new_group, type(new_group))
        old_group = club_dict['age_groups']
        entry = old_group + new_group
        if delete:
            entry = [x for x in old_group if x not in new_group]
        update_club(club, field1, entry)

        field2 = fields[1]
        name = posted['group_name']
        old_group = club_dict['age_group_names']
        new_group = {years[0]: name}
        entry = {**new_group, **old_group}
        if delete:
            entry = {k:v for k,v in old_group.items() if k not in new_group or v != new_group[k]}
        update_club(club, field2, entry)

    elif keys[0] in ratings:
        new_group = [[x for x in keys if x != 'delete']]
        old_group = club_dict['rating_groups']
        entry = old_group + new_group
        if delete:
            #entry = old_group.remove(new_group)
            print('old_group', old_group, 'new_group', new_group)
            entry = []
            for x in old_group:
                if set(x) != set(new_group[0]):
                    entry.append(x)

            print(new_group)
            print(entry)
        update_club(club, fields[2], entry)

    elif 'Jan' in keys:
        entry = {}
        for key in keys:
            if posted[key] != '':
                entry[key] = int(posted[key])
        old = club_dict['club_goals']
        entry = {**old, **entry}
        update_club(club, fields[4], entry)

    else:
        old = club_dict['excluded_fencers']
        if delete:
            new = posted['name']
            entry = [x for x in old if x != new]
        else:
            new = posted['last_name'].strip() + ', ' + posted['first_name'].strip()
            entry = old + [new]

        update_club(club, fields[3], entry)


def update_club(club, field, entry):
    """
    club = str, club's name
    field = str, the field to be updated
    entry = variable, the entries to add to the clubs database
    
    Update's the club's preferences in the database.
    Creates club preferences if the club is not already in the database
    """
    if clubs.find_one({'name':club}) == None:
        create_club(club)

    clubs.update_one({'name':club}, {'$set':{field : entry}})

if __name__ == '__main__':
    """
    Runs a constant loop. Updates from AskFred once per day.
    """
    daily_updater()
