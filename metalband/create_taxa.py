import json
import csv
import argparse

"""
This script is used to generate categories of taxa and their given lists of papers and output them in a json format
"""





def create_taxa(input_file, output_file):
    categories = {}
    with open(input_file, 'r') as f:
        reader = list(csv.reader(f, delimiter='\t'))
        header = reader[0]
        body = reader[1:]
        for line in body:
            title = line[0]
            category = line[1].replace(" ", "_")
            if category not in categories.keys():
                categories[category] = [title]
            else:
                categories[category].append(title)

    with open(output_file, 'w') as o:
        json.dump(categories, o, indent=4)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Group elemnts and output papers based on defined taxa")
    parser.add_argument(
        "-json",
        "--json",
        help="Output .json file that defines taxa",
        default="../outputs/monperrus/taxa/taxa.json"
    )
    parser.add_argument(
        "-input",
        "--input",
        help="Input csv file containing paper names and categories",
        default="../outputs/monperrus/taxa/categorized_gemini.csv"

    )
    args = parser.parse_args()
    create_taxa(args.input, args.json)