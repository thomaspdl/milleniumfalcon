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

We use Flask to create the web application part.

The backend loads two .json file corresponding to the two input files.

We assume the input data are in the right format (ie no missing entry, swapped inputs etc..)
