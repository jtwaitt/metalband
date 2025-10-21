import json
import csv
import argparse


"""Create several formatted TSVs seperating papers by Taxa described in an input json file"""

defined_taxa = {
    "Program Repair of Dynamic Errors" : [],
    "Program Repair of Static Errors": [], 
    "Empirical Studies for Program Repair": [], 
    "Domain-Specific Repair": [], 
    "Optimization & Integration": [], 
    "Position Papers": [], 
    "Miscellaneous": []
    }

output=["dynamic_errors.tsv", "static_errors.tsv", "empirical_studies.tsv", "domain_specific.tsv", "optimization.tsv", "position_paper.tsv", "misc.tsv"]

#Split papers by taxa 
def split_by_taxa(file_name):
    global defined_taxa
    with open(file_name, 'r', encoding="utf-8") as f:
        data = json.load(f)
        for key in data: 
            taxa = data[key]["taxa-name"].split("--")[0]
            print(data[key]["taxa-name"].split("--")[0])
            cite = data[key]["cite"].split("\u201c")[1].split("\u201d")[0]
            print(cite)
            defined_taxa[taxa].append(cite)


#Create .tsv files by taxa
def create_output(input_file, output_file, taxa):
    #header = ["0", "DOI", "Year" , "Last_Cited_Year"]

    try:
        with (
        open(input_file, "r", newline="", encoding="utf-8") as input,
        open(output_file, "w", newline="", encoding="utf-8") as output
        ):
            reader = csv.reader(input, delimiter="\t")
            writer = csv.writer(output, delimiter="\u0020")

            #writer.writerow(header)

            for row in reader:
                #if row[4] == "NOT_FOUND" or row[5] == "NOT_CITED" : continue
                if row[2] not in defined_taxa[taxa]: continue 
                elements = ["0", row[4], row[3], row[5]]
                writer.writerow(elements)



    except FileNotFoundError:
        print(f"Error: File not found at {input_file}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Group elemnts and output papers based on defined taxa")
    parser.add_argument(
        "-json",
        "--json",
        help="Input .json file that defines taxa",
        default=""
    )
    parser.add_argument(
        "-input",
        "--input",
        help="Input tsv file",
        default="../outputs/monperrus/monperrus-queried_with_citations.tsv"

    )
    parser.add_argument(
        '-skip',
        '--skip',
        help='"True/False, Skip the seperate by taxa step',
        default=True
    )


    args = parser.parse_args()
    if not args.skip:
        split_by_taxa(args.json)
        count = 0
        for key in defined_taxa:
            create_output(args.input, output[count], key)
            count+=1
            print("Papers made")
    else:
        with open(args.json, 'r') as f:
           defined_taxa = json.load(f)
        file_location = "../outputs/monperrus/taxa/"
        for key in defined_taxa:
            create_output(args.input, file_location+key+".tsv", key)
        print("Papers Made")