import csv
import argparse
import json




def cap_deaths(input, output, cap, start):
    lines = []
    with open(input, 'r') as f:
        input = csv.reader(f, delimiter=" ")
        print("HERE")
        for line in input:
            print(line)
            if int(line[3]) <= cap and int(line[2]) >= start:
                print(line)
                lines.append(line)
    with open(output, 'w') as f:
        output = csv.writer(f, delimiter =" ")
        for line in lines:
            output.writerow(line)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cap death date year by given year")
    parser.add_argument(
        '-input',
        "--input",
        type = str,
        help = "Input File",
        default = "../outputs/oalex/oalex_papers.tsv"
    )
    parser.add_argument(
        "-output",
        "--output",
        help = "Output File",
        type = str,
        default = "../outputs/oalex/oalex_papers.tsv"
    )
    parser.add_argument(
        "-year",
        "--year",
        help="Death year cap",
        type = int,
        default = 2010
    )
    parser.add_argument(
        "-start",
        "--start",
        help="Start of paper births",
        type=int,
        default=1980
    )

    args = parser.parse_args()
    cap_deaths(args.input, args.output, args.year, args.start)