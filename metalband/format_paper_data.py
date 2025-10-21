import csv
import argparse

"""Short script to reformat saved data that has doi and citation information and write it into the expected 3 / 4 columns wanted by LiteRate"""


# Function to Reformat data into the proper tsv
def format_data(input_path, output_path):
    """
    Rewrite data into the expected format for LiteRate 
    """
    
    #header = ["0", "DOI", "Year" , "Last_Cited_Year"]

    print(input_path, output_path)
    try:
        with (
        open(input_path, "r", newline="", encoding="utf-8") as input,
        open(output_path, "w", newline="", encoding="utf-8") as output
        ):
            reader = list(csv.reader(input, delimiter="\t"))
            writer = csv.writer(output, delimiter="\u0020")

            header = reader[0]
            body = reader[1:]
            #writer.writerow(header)
            death_count = 0
            born_count = 0

            for row in body:
                if row[4] == "NOT_FOUND":continue
                
                if row[3] != "last_cited_year" and int(row[5]) < 2020: 
                    
                    death_count += 1
                if int(row[3]) < 2020:
                    
                    born_count += 1   
                elements = ["0", row[4], row[3], row[5]]
                writer.writerow(elements)
            print(death_count)
            print(born_count)




    except FileNotFoundError:
        print(f"Error: File not found at {input_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    #for line in input_file:
    #    print(line)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reformat Data into the Expected Columns for output CSV"
    )
    parser.add_argument(
        "-i", 
        "--input", 
        help="Path to the input .tsv file. If not provided, default is ../data/monperrus/monperrus-queried.tsv", 
        default="../outputs/monperrus/monperrus-queried.tsv"
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to the output .tsv file to save results. If not provided, results are saved to ../outputs/monperrus/papers.tsv.",
        default="../outputs/monperrus/papers.tsv",
    )

    args = parser.parse_args()

    format_data(args.input, args.output)