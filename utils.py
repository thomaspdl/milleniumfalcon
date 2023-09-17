import argparse
from flask import Flask, request, render_template
import pandas as pd
import json as js
import sqlite3
import os


# find all the possible paths between departure and arrival 
# arguments:
#  - G: adjacency dictionnary 
#  - s: starting point (element of G) 
#  - e: end point (arrival element of G)
def find_paths(G, s, e, path=[]):
    path = path + [s]
    if s == e:
        return [path]
    if s not in G:
        return []
    paths = []
    for neighbor in G[s]:
        if neighbor not in path:
            new_paths = find_paths(G, neighbor, e, path)
            for new_path in new_paths:
                paths.append(new_path)
    return paths

# compute the travel time for a path
# arguments: 
#  - path: list of planets 
#  - Times: travel time between two planets
def compute_time(path,Times):
    N = len(path)
    T = 0
    for i in range(N-1):
        o = path[i]
        d = path[i+1]
        if o == d:
            T += 1
        else:
            T += Times[(o,d)]
    return T

# put the hunter coordinates in the right format
# argument:
#  - hunters: list of dictionnary the position of hunters for each day 
#              typical input: [{'planet': 'Hoth', 'day': 6},{'planet': 'Hoth', 'day': 7}, {'planet': 'Hoth', 'day': 8}]
def process_hunters(hunters):
    H = set()
    for h in hunters:
        H.add((h['day'],h['planet'])) 
    return H

# from the paths, computes the possible positions at a different times
# arguments: 
#  - path: list of planets 
#  - Times: travel time between two planets
def process_paths(path,Times):
    T = 0
    pos = set()
    pos.add((T,path[0]))
    N = len(path)
    for i in range(N-1):
        s = path[i]
        d = path[i+1]
        if s == d:
            T += 1
        else:
            T += Times[(s,d)]
        pos.add((T,d))
    return pos

# function to compute all the possible paths if you add nbstops along the way
# arguments:
#  - path: original path (list)
#  - nbstops: maximum number of stops to add (integer)
def augment_paths(path,nbstops):
    if nbstops == 0:
        return [path]
    else:
        augmented = augment_paths(path,nbstops-1)
        toadd = []
        for aug in augmented:
            for i in range(len(path)-1):
                temp = aug[:i] + [aug[i]] + aug[i:]
                toadd.append(temp)
        result = augmented + toadd
        return  [list(x) for x in set(tuple(x) for x in result)]

# compute the  chance that a  path will get intercepted 
# arguments:
def compute_chances(path,Times,hunters):
    positions_hunters = process_hunters(hunters)
    positions_milleniumf = process_paths(path,Times)
    Ninter = len(positions_milleniumf.intersection(positions_hunters))
    chance = 100*(1 - 1/10*sum([(9/10)**i for i in range(Ninter)]))
    return chance
    
# compute the maximal chance that a list of path will get intercepted 
# arguments:
def compute_chances_all(path_relevant,Times,hunters):
    if len(path_relevant) == 0:
        return 0
    chances = [compute_chances(path,Times,hunters) for path in path_relevant]
    return int(max(chances))
    
# check if a path satisfies the autonomy constraint
# arguments:
def check_autonomy(path,autonomy,Times):
    N = len(path)
    distance = 0
    for i in range(N-1):
        o = path[i]
        d = path[i+1]
        if o == d:
            distance = 0
        else:
            distance += Times[(o,d)]
        if distance > autonomy:
            return False
    return True

# Define graph of possible paths 
# argument:
#  - df: dataframe of origin, destination, travel_time
def define_graph_times(df):
    G = {}
    Times = {}
    for ind in range(len(df)):
        origin = df['origin'].iloc[ind]
        destination = df['destination'].iloc[ind]
        time = df['travel_time'].iloc[ind]
        if origin in G:
            G[origin].append(destination)
        else:
            G[origin] = [destination]
        Times[(origin,destination)] = time
    return G, Times

def augment_all_paths(paths_se,countdown,Times):
    all_paths = []
    for path in paths_se:
        nbstops = max(0,countdown - compute_time(path,Times)) # number of stops allowed
        added = augment_paths(path,nbstops)
        all_paths += added
    return all_paths


def compute_chance(df, countdown, autonomy, hunters, departure, arrival):
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
    result = compute_chances_all(path_relevant,Times,hunters)
    return result

def get_parameters(milleniumf_path, empire_path):

    # load json files
    milleniumf = js.load(open(milleniumf_path))
    empire = js.load(open(empire_path))

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
    hunters = empire['bounty_hunters']
    departure = milleniumf['departure']
    arrival = milleniumf['arrival']

    return df, countdown, autonomy, hunters, departure, arrival
