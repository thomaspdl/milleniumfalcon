import argparse
from flask import Flask, request, render_template
import pandas as pd
import json as js
import sqlite3
import os

from utils import find_paths, compute_time, process_hunters, process_paths, augment_paths, compute_chances, \
    compute_chances_all, check_autonomy, define_graph_times, augment_all_paths

app = Flask(__name__)

# Initialize argparse to handle command-line arguments
parser = argparse.ArgumentParser(description="What are the chances the millenium falcon will escape?")
parser.add_argument("path1", type=str, help="First path")
parser.add_argument("path2", type=str, help="Second path")
args = parser.parse_args()

@app.route('/')
def compute():

    # get two positional arguments
    milleniumf_js = args.path1
    empire_js = args.path2

    # load json files
    milleniumf = js.load(open(milleniumf_js))
    empire = js.load(open(empire_js))

    # get db
    directory = os.path.dirname(milleniumf_js)
    dbfile = directory + '/' + milleniumf['routes_db']

    # Create a SQL connection to our SQLite database
    con = sqlite3.connect(dbfile)
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    # load into pandas df
    df = pd.read_sql_query("SELECT * from routes", con)
    # close connection
    con.close()

    # get parameters 
    countdown = empire['countdown']
    autonomy = milleniumf['autonomy']
    Hunters = empire['bounty_hunters']
    departure = milleniumf['departure']
    arrival = milleniumf['arrival']

    # define graph of paths and travel times 
    G, Times = define_graph_times(df)

    # find all the possible paths between departure (Tatooine) and arrival (Endor)
    paths = find_paths(G, departure, arrival, path=[])

    # add all the potential stops to the existing paths
    all_paths = augment_all_paths(paths,countdown,Times)

    # keep the unique paths only 
    all_paths_unique = [list(x) for x in set(tuple(x) for x in all_paths)]

    # get the paths with 
    # 1) travel time lower than countdown 
    # 2) autonomy constraint respected
    path_relevant = [path for path in  all_paths_unique if compute_time(path,Times) <= countdown and check_autonomy(path,autonomy,Times)]

    # get the final chance
    result = compute_chances_all(path_relevant,Times,Hunters)

    #return results
    print(f"{result}")

    return f"Result of computation: {result}"

if __name__ == '__main__':
    app.run(debug=False)


