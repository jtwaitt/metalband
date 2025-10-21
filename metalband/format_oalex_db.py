import csv
import sys
import argparse
import re
import os
import json
from lxml import etree
from collections import defaultdict
import pyalex
from tqdm import tqdm


"""This is a custom script to handle getting the necessary info (birth year, doi, etc) from a downloaded Open Alex Database"""

API_CACHE_FILE = "cache.json"
cache = {}


# --- Caching Functions ---
def load_api_cache():
    """Loads the API cache from a JSON file if it exists."""
    if os.path.exists(API_CACHE_FILE):
        print(f"Loading API cache from {API_CACHE_FILE}...")
        with open(API_CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def calculate_death_year(year_threshold, citation_threshold, citation_years, birth_year):
    "Uses a sliding window to check if a citation threshold is met over every set of year_thresholds."
    
    #create a list of citations per year before calculation
    citation_years = sorted(citation_years)
    final_citation = max(citation_years)
    if final_citation < birth_year:
        final_citation = birth_year
    citations_per_year = [0] * (final_citation - birth_year + 1)
    print(citations_per_year)
    
    for citation in citation_years:
        print("CITATION:", citation, "BIRTH_YEAR:", birth_year, end=" || ")
        
        year = citation - birth_year
        if year < 0:
            year = 0
        print(year)
        citations_per_year[year] += 1
    #print(citations_per_year)

    for i in range(year_threshold):
        citations_per_year.append(0)

    #build initial sliding window
    citation_count = 0
    for i in range(year_threshold):
        citation_count += citations_per_year[i]
    
    if citation_count < citation_threshold:
        print(birth_year + year_threshold)
        return birth_year 

    #move sliding window through rest of list
    for i in range(year_threshold, len(citations_per_year)):
        citation_count -= citations_per_year[i - year_threshold]
        citation_count += citations_per_year[i]
        if citation_count < citation_threshold:
            return birth_year + i
    print(birth_year + len(citations_per_year))
    return birth_year + len(citations_per_year)
        

def main_logic(args):
    with open(args.input_db, 'r') as f:
        with open(args.input, 'w') as g:
            file = csv.reader(f)
            output = csv.writer(g, delimiter="\t")
            count = 0
            #output.writerow([0, "ID", "Birth Year", "API_CALL", "TAXA"])
            for row in file:
                if count <= 40000:
                    count += 1
                    continue
                if count >= 55000:
                    break
                print(count)
                count += 1
                output.writerow([0, row[0], row[4], row[27], row[71]])
    


    cache = load_api_cache()

    if len(cache) < 1:
        with open(args.input, 'r') as f:
                
            file = csv.reader(f, delimiter = "\t")
            count = 0
            for row in file:
                if count == 0:
                    count += 1
                    continue
                elif count > 10000:
                    break 
                citation_years= []
                try:
                    print("Trying work:", row[1])
                    citing_works_iterator = (
                        pyalex.Works().filter(cites=row[1]).get(per_page=200)
                    )

                    for work in citing_works_iterator:
                        if work.get("publication_year"):
                            citation_years.append(work["publication_year"])
                    print("  Found latest date", max(citation_years))
                except Exception as e:
                    print("  Error with work")
                count += 1
                cache[row[1]] = [row[2], citation_years]



    with open(args.output, 'w') as f:
        output = csv.writer(f, delimiter = ' ')
        for key in cache:
            output.writerow([0, key, cache[key][0], calculate_death_year(args.years, args.cites, cache[key][1], int(cache[key][0]))])

    with open(API_CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get necessary information out of 10,000 samples from oalex Database")
    parser.add_argument(
        '-input_db',
        "--input_db",
        type = str,
        help = "Input Data to Be Processed",
        default = "../data/oalex/oalex_ai.csv"
    )
    parser.add_argument(
        "-input",
        "--input",
        help = "File that stores necessary info from DB",
        type = str,
        default = "../outputs/oalex/oalex.tsv"
    )
    parser.add_argument(
        "-output",
        "--output",
        help="Output File",
        type = str,
        default = "../outputs/oalex/oalex_papers.tsv"
    )
    parser.add_argument(
        "-years",
        "--years",
        help = "Number of years checked before death",
        type = int,
        default = 4
    )
    parser.add_argument(
        "-cites",
        "--cites",
        help = "Number of citations needed to be considered alive",
        type = int,
        default = 4
    )
    args = parser.parse_args()
    main_logic(args)