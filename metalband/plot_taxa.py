import json
import csv
import argparse
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


"""Create Empirical Plots of births and deaths based on cached cited years"""





def load_json(file):
    with open(file, 'r') as f:
        data = json.load(f)
        return data


def load_tsv(file, taxa_dict):
    taxa_name = file.split('/taxa/')[1]
    #taxa_name = "papers"
    taxa_dict[taxa_name] = []
    with open(file, 'r',  encoding="UTF-8") as f:
        tsv_reader = csv.reader(f, delimiter=" ")
        for row in tsv_reader:
            #doi = "openalex_" + row[1]
            doi = row[1]
            taxa_dict[taxa_name].append((doi, row[2], row[3]))
    return taxa_dict


def process_data(taxas, json):
    taxa_dict = {}
    citations_dict = {}
    alive_dict = {}
    data = load_json(json)
    #print(data)
    for taxa in taxas:
        taxa_name = taxa.split("/taxa/")[1]
        #taxa_name = "papers"
        citations_dict[taxa_name] = {}
        alive_dict[taxa_name] = {}
        taxa_dict = load_tsv(taxa, taxa_dict)
    #print(taxa_dict)
    for key in taxa_dict:
        elements = taxa_dict[key]
        for paper in elements:
            #print(paper)
            for i in range(int(paper[1]), int(paper[2]) + 1):
                if i in alive_dict[key]:
                    alive_dict[key][i] += 1
                else:
                    alive_dict[key][i] = 1
            #print(paper[0])
   
    for taxa in taxa_dict:
        for paper in taxa_dict[taxa]:
            if paper[0] == "NOT_FOUND":
                continue
            for year in data[f"openalex_{paper[0]}"]:
            #for year in data[paper[0]]:
                
                if year in citations_dict[taxa]:
                    citations_dict[taxa][year] += 1
                else:
                    citations_dict[taxa][year] = 1

    for taxa in alive_dict:
        x = []
        y = []
        for year in sorted(alive_dict[taxa]):
            x.append(year)
            y.append(alive_dict[taxa][year])
        plt.plot(x, y, label=taxa)
        peak = max(y)
                
    plt.title("Number of Alive Papers by Taxa")
    plt.xlabel("Year")
    plt.ylabel("Number of Papers")
    plt.legend()
    plt.show()            
    
    largest_taxas = [(0, 'name'), (0, 'name'), (0, 'name')]
    for taxa in citations_dict:
        x = []
        y = []
        for year in sorted(citations_dict[taxa]):
            x.append(year)
            y.append(citations_dict[taxa][year])
        plt.plot(x, y, label=taxa)
 
        #print("Year:", year, "Count:", alive_dict[taxa][year])

    plt.title("Number of Citations per Year by Taxa")
    plt.xlabel("Year")
    plt.ylabel("Number of Citations")
    plt.legend()
    plt.show()    
    
    for taxa in citations_dict:
        x_1 = []
        y_1 = []
        x_2 = []
        y_2 = []
        for year in sorted(citations_dict[taxa]):
            x_1.append(year)
            y_1.append(citations_dict[taxa][year])
        plt.plot(x_1, y_1, label="Citations")
        for year in sorted(alive_dict[taxa]):
            x_2.append(year)
            y_2.append(alive_dict[taxa][year])
        plt.plot(x_2, y_2, label="Living Papers")
        plt.title(f"Number of Citations vs. Alive {taxa} Papers by Year")
        plt.xlabel = "Years"
        plt.ylabel = "Count"
        plt.legend()
        plt.show()




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Create empirical plots based on number of citations per year and current papers alive")
    parser.add_argument(
        "-json",
        "--json",
        help="Input .json file that contains all cited years,",
        default="./api_cache.json"
    )
    parser.add_argument(
        "-inputs",
        "--taxas",
        type=str,
        help="Input taxa files",
        nargs="+",
        default="../outputs/monperrus/papers.tsv"


    )
    args = parser.parse_args()
    process_data(args.taxas, args.json)