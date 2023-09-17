# Millenium Falcon

## Intent

This in an attempt to resolve the pdoblem described here 
https://github.com/lioncowlionant/developer-test

## Invocation 

We give a sample invocation of the script below:
```
python3 webapp.py path-to-millenium-falcon.json path-to-empire.json
```

## Solution

### Frontend

We use Flask to create the web application part.

The code loads two .json file corresponding to the two input files.

We assume the input data are in the right format (ie no missing entry, swapped inputs etc..)

### Backend

Define a directed graph within the possible planets

Computing all possible  paths between origin and destination 

We then “augment” the obtained paths by adding all the possible stops.

We then filter all the possible paths by Keeping those

1. With total travel time below the  countdown value
   
3. Where the millenium falcon does not run out out of fuel

This gives us a set of possible paths, feasible paths.

From those paths, we compute the chance of getting caught by bounty hunters, and pick the maximum chance over the different feasible paths.
