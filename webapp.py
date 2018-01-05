from flask import Flask, request, render_template, session, redirect
app = Flask(__name__)
#import pandas as pd
#import numpy as np
#import graphlab as gl
from pymongo import MongoClient
import pymongo
import time
from pprint import pprint
from fencing_core import *
app.secret_key = 'datascience'

#Post Data Request:
#@app.route("/")
@app.route('/oldindex')
@app.route('/index')
def index():
    '''
    Creates an index page with plaintext submission.
    '''
    categories = [
    ['A', 'B'],
    ['C', 'D'],
    ['E', 'U'],
    ]

    byRank = []

    for cat in categories:
        header = " + ".join(cat)
        byRank.append([header, rating_groups(cat, 'foil', pull_club(club, 'Foil'))])

    ageGroups = [
    'Junior',
     'Cadet',
     'Y14',
      'Y12',
      'Y10']

    ages = [
    [1999, 2005],
    [2002, 2005],
    [2003, 2006],
    [2005, 2008],
    [2007, 2010]
    ]

    byAge = []

    for age in ages:
        byAge.append(age_groups(age, pull_club(club, 'Foil')))

    byAge=zip(ageGroups, byAge)

    pred = pull_club(club, 'Foil')
    #print(pred)
    return render_template('top100.html',
                            #user_id = user_id,
                            pred = pred,
                            byRank = byRank,
                            byAge = byAge)
# Register Submission into Database

@app.route('/fencer', methods=['GET'] )
def fencer():
    fencer = request.args.get('fencer')
    name, preds = pull_fencer(fencer)
    fencer = fencers.find_one({'name' : fencer})
    return render_template('fencer.html',
                            name = name,
                            fencer = fencer,
                            pred = preds
                            )

@app.route('/full_list', methods=['GET'] )
def by_rating():
    lookup = {'A B': ['A', 'B'],
              'C D': ['C', 'D'],
              'E U': ['E', 'U'],
              'Junior': [1999, 2005],
              'Cadet': [2002, 2005],
              'Y14': [2003, 2006],
              'Y12': [2005, 2008],
              'Y10': [2007, 2010],
              'Overall': 'Overall'
            }

    club = request.args.get('club')
    group = request.args.get('group')
    weapon = request.args.get('weapon')
    #print(weapon)
    group = lookup[group]

    if group == 'Overall':
        name = group
        preds = pull_club(club, weapon)
        return render_template('category.html',
                                club = club,
                                weapon = weapon,
                                rating = name,
                                preds = preds
                                )

    elif type(group[0]) == str:
        print(weapon)
        name = " + ".join(group)
        preds = rating_groups(group, weapon.lower(), pull_club(club, weapon))
        return render_template('category.html',
                                weapon = weapon,
                                club = club,
                                rating = name,
                                preds = preds
                                )

    elif type(group[0]) == int:
        year_to_name = {
        1999: 'Junior',
        2002: 'Cadet',
        2003: 'Y14',
        2005: 'Y12',
        2007: 'Y10',
        }

        name = year_to_name[group[0]]
        preds = age_groups(group, pull_club(club, weapon))
        print(weapon)
        return render_template('category.html',
                                weapon = weapon,
                                club = club,
                                rating = name,
                                preds = preds
                                )

# @app.route('/')
# def home5():
#     '''
#     Creates an index page with plaintext submission.
#     '''
#     club = request.args.get('club')
#     categories = [
#     ['A', 'B'],
#     ['C', 'D'],
#     ['E', 'U'],
#     ]
#
#     byRank = []
#
#     for cat in categories:
#         header = " + ".join(cat)
#         piece = rating_groups(cat, 'foil', pull_club(club, 'Foil'))
#         if len(piece) > 5:
#             piece = piece[:5]
#         byRank.append([header, piece])
#
#     ageGroups = [
#     'Junior',
#      'Cadet',
#      'Y14',
#       'Y12',
#       'Y10']
#
#     ages = [
#     [1999, 2005],
#     [2002, 2005],
#     [2003, 2006],
#     [2005, 2008],
#     [2007, 2010]
#     ]
#
#     byAge = []
#
#     for age in ages:
#         piece = age_groups(age, pull_club(club, 'Foil'))
#         if len(piece) > 5:
#             piece = piece[:5]
#         byAge.append(piece)
#
#     #byAge=zip(ageGroups, byAge)
#
#     allClub = ['Overall', pull_club(club, 'Foil')[:5]]
#     chunk2 = [[ageGroups[x], byAge[x]] for x in range(3)]
#     chunk3 = [[ageGroups[x], byAge[x]] for x in range(3,5)] + [allClub]
#     batch = [byRank, chunk2, chunk3]
#
#     return render_template('5home.html',
#                             batch = batch)


# @app.route('/feedback', methods=['POST'])
# def feedback():
#     helpful = request.form['helpful']
#     user_id = session['user_id']

@app.route('/test', methods=['GET'])
def monthlies():
    club = request.args.get('club')
    weapons = request.args.get('weapons').split('|')
    lastmonth = datetime.today().month - 1
    year = datetime.today().year
    if lastmonth == 0:
        lastmonth += 12
        year -=1

    month, batch1 = pull_month_winners(club, weapons, lastmonth, year)
    #print(batch1[0])
    col_width, batch2 = season_leaders(club, weapons)
    # for thing in batch2:
    #     print(thing, '\n')
    return render_template('club_home.html',
                            col_width = col_width,
                            club = club,
                            month = month,
                            batch1 = batch1,
                            batch2 = batch2)

@app.route('/month', methods=['GET'])
def current_month():
    club = request.args.get('club')
    year = request.args.get('year')
    month = request.args.get('month')
    weapons = results.find({'club':club}).distinct('weapon')


    #print(weapons)
    month, batch = pull_month(club, weapons, month, year)
    div = 1
    den = len(batch)
    if den == 0:
        den += 1
    col_width = 12//den
    return render_template('month_template.html',
                            col_width = col_width,
                            year = year,
                            club = club,
                            month = month,
                            batch = batch)

@app.route('/month_winners', methods=['GET'])
def month_winners():
    club = request.args.get('club')
    month_list = month_by_month(club)
    col_width = 12//len(results.find({'club' : club}).distinct('weapon'))
    return render_template('month_winners.html',
                            club = club,
                            col_width = col_width,
                            month_list = month_list)

"""
BELOW FOLLOWS CLUB-SPECIFIC PAGES
"""

@app.route('/', methods=['GET'])
@app.route('/moe', methods=['GET'])
@app.route('/MOE', methods=['GET'])
def moe():
    weapons = results.find({'club':'MOE'}).distinct('weapon')
    weapons = '|'.join(weapons)
    return redirect("/test?club=MOE&weapons="+weapons)

@app.route('/riverside', methods=['GET'])
def riverside():
    weapons = results.find({'club':'RIVERSIDE'}).distinct('weapon')
    weapons = '|'.join(weapons)
    return redirect("/test?club=RIVERSIDE&weapons="+weapons)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
