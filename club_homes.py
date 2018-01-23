from flask import Flask, request, render_template, session, redirect
app = Flask(__name__)
from pymongo import MongoClient
import pymongo
import time
from pprint import pprint
from fencing_core import *

@app.route('/moe', methods=['GET'])
@app.route('/MOE', methods=['GET'])
def moe():
    weapons = results.find({'club':'MOE'}).distinct('weapon')
    weapons = '|'.join(weapons)
    return redirect("/test?club=MOE&weapons="+weapons)

@app.route('/riverside', methods=['GET'])
@app.route('/RIVERSIDE', methods=['GET'])
def riverside():
    weapons = results.find({'club':'RIVERSIDE'}).distinct('weapon')
    weapons = '|'.join(weapons)
    return redirect("/test?club=RIVERSIDE&weapons="+weapons)
