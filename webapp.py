import argparse
from flask import Flask, request, render_template
import pandas as pd
import json as js
import sqlite3
import os

from utils import find_paths, compute_time, process_hunters, process_paths, augment_paths, compute_chances, \
    compute_chances_all, check_autonomy, define_graph_times, augment_all_paths, compute_chance, get_parameters

app = Flask(__name__)

# Initialize argparse to handle command-line arguments
parser = argparse.ArgumentParser(description="What are the chances the millenium falcon will escape?")
parser.add_argument("path1", type=str, help="First path")
parser.add_argument("path2", type=str, help="Second path")
args = parser.parse_args()

@app.route('/')
def compute():
    # get two positional arguments
    milleniumf_path = args.path1
    empire_path = args.path2
    # get data
    df, countdown, autonomy, hunters, departure, arrival = get_parameters(milleniumf_path, empire_path)
    # compute result
    result = compute_chance(df, countdown, autonomy, hunters, departure, arrival)
    #print result
    print(f"{result}")
    #return result in web browser
    return f"Result of computation: {result}"

if __name__ == '__main__':
    app.run(debug=False)


