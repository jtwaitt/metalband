import json 

"""UNIMPORATNT SCRIPT FOR PRINTING OUT NUMBERS FOR DEBUG"""




PATH = "./api_cache.json"

years = {
    2000: 0, 
    2001: 0, 
    2002: 0, 
    2003: 0, 
    2004: 0, 
    2005: 0, 
    2006: 0,
    2007: 0, 
    2008: 0, 
    2009: 0, 
    2010: 0, 
    2011: 0, 
    2012: 0, 
    2013: 0, 
    2014: 0, 
    2015: 0, 
    2016: 0, 
    2017: 0, 
    2018: 0, 
    2019: 0, 
    2020: 0, 
    2021: 0, 
    2022: 0, 
    2023: 0, 
    2024: 0, 
    2025: 0, 
    }

period = {2018: 0, 2019: 0}


with open(PATH, 'r') as f:
    data = json.load(f)

for key in data:
    for item in data[key]:
        if item <= 2018: 
            period[2018] += 1
        else:
            period[2019] += 1
        years[item] += 1
    print(key, years)
    print(period)
    period[2018] = 0
    period[2019] = 0
    for year in years:
        years[year] = 0
    if len(data[key]) > 0:
        print(key, "Number of cites:", len(data[key]), "Most Recent: ", max(data[key]))
    else:
        print(key, "none")

    
