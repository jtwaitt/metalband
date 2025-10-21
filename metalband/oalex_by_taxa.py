import json
import csv


defined_taxa = {}
with open("../outputs/oalex/oalex.tsv", 'r') as f:
    reader = csv.reader(f, delimiter='\t')

    for line in reader:
        if line[4] in defined_taxa.keys():
            defined_taxa[line[4]].append(line[1])
        else:
            defined_taxa[line[4]] = [line[1]]


lines = []
with open("../outputs/oalex/oalex_papers.tsv", 'r') as f:
    reader = csv.reader(f, delimiter=' ')
    for line in reader:
        lines.append(line)

for key in defined_taxa:
    name = key.replace(" ", "_")
    with open(f"../outputs/oalex/taxa/{name}.tsv", 'w') as g:
        writer = csv.writer(g, delimiter=' ')
        for paper in defined_taxa[key]:
            index = 0
            for line in lines:
                if line[1] == paper:
                    print("FOUND IT")
                    lines.pop(index)
                    print(len(lines))
                    writer.writerow(line)
                    break
                index += 1
                
