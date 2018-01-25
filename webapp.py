from flask import request, render_template, session, redirect
from flask import Flask
app = Flask(__name__)
#import pandas as pd
#import numpy as np
#import graphlab as gl
from pymongo import MongoClient
import pymongo
import time
from pprint import pprint
from page_utilities import *
from club_homes import *
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


    # lookup = {'A B': ['A', 'B'],
    #           'C D': ['C', 'D'],
    #           'E U': ['E', 'U'],
    #           'Junior': [1999, 2005],
    #           'Cadet': [2002, 2005],
    #           'Y14': [2003, 2006],
    #           'Y12': [2005, 2008],
    #           'Y10': [2007, 2010],
    #           'Overall': 'Overall'
    #         }

    club = request.args.get('club')
    club_dict = clubs.find_one({'name':club})
    rating_cats = d_categories
    age_cats = [d_year_to_name[k] for k in d_year_to_name]
    year_to_name = d_year_to_name

    if get_club_dict(club.lower())['rating_groups'] != []:
        rating_cats = get_club_dict(club.lower())['rating_groups']

    if get_club_dict(club.lower())['age_group_names'] != {}:
        age_cats = [get_club_dict(club.lower())['age_group_names'][k] for k in get_club_dict(club.lower())['age_group_names']]
        year_to_name ={get_club_dict(club.lower())['age_group_names'][k]:int(k) for k in get_club_dict(club.lower())['age_group_names']}


    group = request.args.get('group')
    weapon = request.args.get('weapon')
    weapons = [weapon]
    #print(weapon)
    # group = lookup[group]
    print(type(group))
    print(group)

    if group == 'Overall':
        name = group
        preds = pull_club(club, weapon)
        print(weapon)
        points = club_points(club, weapons)
        print(points)
        return render_template('category.html',
                                age_cats = age_cats,
                                rating_cats = rating_cats,
                                club = club,
                                weapon = weapon,
                                rating = name,
                                preds = preds,
                                points = points
                                )

    elif group[0] == '[':
        name = group[1:-1]
        bucket = []

        for rating in group:
            if rating in ['A', 'B', 'C', 'D', 'E', 'U']:
                bucket.append(rating)

        print(bucket)

        preds = rating_groups(bucket, weapon.lower(), pull_club(club, weapon))
        points = club_points(club, weapons)
        return render_template('category.html',
                                age_cats = age_cats,
                                rating_cats = rating_cats,
                                club = club,
                                weapon = weapon,
                                rating = name,
                                preds = preds,
                                points = points
                                )

    elif type(group) == str:
        print(weapon)
        name = group
        buckets = []

        age_cats = d_ages
        year_to_name = d_year_to_name
        print('age_cats1', age_cats)
        print('year_to_name1', year_to_name)

        if get_club_dict(club.lower())['age_group_names'] != {}:
            age_cats = get_club_dict(club.lower())['age_groups']
            year_to_name = get_club_dict(club.lower())['age_group_names']

        print('year_to_name2', year_to_name)
        print('age_cats2', age_cats)
        #print('group names dict', get_club_dict(club)['age_group_names'])

        for key in year_to_name:
            # print(key)
            # print('key', year_to_name[key])
            # print('group', group)
            if year_to_name[key] == group:
                buckets = [key]
                for thing in age_cats:
                    #print('thing', thing)
                    #print('age_cats', age_cats)
                    if buckets[0] == thing[0]:
                        buckets.append(thing[1])
        print(buckets)
        for x in range(len(buckets)):
            buckets[x] = int(buckets[x])

        #print('should be int', buckets)

        preds = age_groups(buckets, pull_club(club, weapon))
        points = club_points(club, weapons)
        age_cats = [year_to_name[x[0]] for x in age_cats]
        return render_template('category.html',
                                age_cats = age_cats,
                                rating_cats = rating_cats,
                                club = club,
                                weapon = weapon,
                                rating = name,
                                preds = preds,
                                points = points
                                )

    # elif type(group[0]) == int:
    #
    #     name = year_to_name[group[0]]
    #     preds = age_groups(group, pull_club(club, weapon))
    #     points = club_points(club, weapons)
    #
    #
    #
    #     return render_template('category.html',
    #                             age_cats = age_cats,
    #                             rating_cats = rating_cats,
    #                             club = club,
    #                             weapon = weapon,
    #                             rating = name,
    #                             preds = preds,
    #                             points = points
    #                             )




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

    print('MONTHLIES', weapons)
    month_total = club_points_month(club, weapons, lastmonth, year)
    season_total = club_points(club, weapons)
    month, batch1 = pull_month_winners(club, weapons, lastmonth, year)
    #print('from webapp', month_total)
    col_width, batch2 = season_leaders(club, weapons)
    # for thing in batch2:
    #     print(thing, '\n')
    return render_template('club_home.html',
                            month_total = month_total,
                            season_total = season_total,
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

    points = club_points_month(club, weapons, month, year)
    return render_template('month_template.html',
                            points = points,
                            col_width = col_width,
                            year = year,
                            club = club,
                            month = month,
                            batch = batch)

@app.route('/month_winners', methods=['GET', 'POST'])
def month_winners():
    club = request.args.get('club')
    club_dict = clubs.find_one({'name':club})
    month_list = month_by_month(club)
    col_width = 12//len(results.find({'club' : club}).distinct('weapon'))
    return render_template('month_winners.html',
                            club = club,
                            col_width = col_width,
                            month_list = month_list)

@app.route('/club_admin', methods=['GET'] )
def club_admin():
    club = request.args.get('club')
    club_dict = clubs.find_one({'name':club})

    return render_template('club_admin.html',
                            clubt = club.title(),
                            club = club,
                            years = years,
                            club_dict = club_dict)

@app.route('/club_update', methods=['GET', 'POST'] )
def club_update():
    club = request.args.get('club')
    posted = request.form
    keys = []
    print('club_update', posted)
    stage_update(club, posted)
    # print(list(posted.keys()))
    # print(posted)
    # for k in posted:
    #     print(k)
    #     print(request.form[k])

    return redirect( "/club_admin?club=" + club)

@app.route('/', methods=['GET'])
def home_page():
    return render_template('home.html')


    # return render_template('club_admin.html',
    #                         club = club.title(),
    #                         years = years,
    #                         club_dict = club_dict)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
