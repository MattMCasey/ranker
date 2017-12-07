from flask import Flask, request, render_template, session
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
@app.route('/')
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
        byRank.append([header, rating_groups(cat, 'foil', pull_club('MOE', 'Foil'))])

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
        byAge.append(age_groups(age, pull_club('MOE', 'Foil')))

    byAge=zip(ageGroups, byAge)

    pred = pull_club('MOE', 'Foil')
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
    return render_template('fencer.html',
                            name = name,
                            pred = preds
                            )


@app.route('/top100', methods=['GET'] )
def top100():
    user_id=session['user_id']
    #text = request.args[user_id]
    name, preds = model.display_top_100(user_id)
    return render_template('top100.html',
                            user_id = user_id,
                            pred = preds)


@app.route('/feedback', methods=['POST'])
def feedback():
    helpful = request.form['helpful']
    user_id = session['user_id']


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
