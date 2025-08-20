# Research code for the Metal Band Project

Structure of this repo

```
├── data
│   ├── dblp.dtd                            # DBLP metadata, source this yourself
│   ├── dblp.xml                            # Huge DBLP dump, source this yourself
│   ├── monperrus
│   │   └── monperrus.tsv                   # Raw transcription of the monperrus dataset
│   └── survey
│       ├── conf_auth_name_year.tsv         # Manually cleaned up survey
│       ├── papers.tsv                      # Raw survey dump
│       └── papers.txt                      # Raw survey dump
├── flake.nix                               # Reproducibly set up build environment using nix
├── metalband
│   ├── doi_search_openalex.py              # Find DOI from openalex/crossref
│   ├── find_last_cited_dblp.py             # Find last citation from DBLP dump
│   ├── find_last_cited_paper_openalex.py   # Find last citation from openalex/crossref
│   └── parse_dblp_papers.py                # Parse DBLP dump
├── outputs
│   ├── monperrus
│   │   ├── monperrus-last_cited.tsv        # Monperrus dataset + time of last citation
│   │   ├── monperrus-queried.tsv           # Monperrus dataset + DOI
│   │   └── monperrus-queried_with_citations.tsv # Merge the two files above
│   └── survey                              # Script outputs from RR survey
│       ├── death_times.tsv
│       ├── doi.tsv
│       ├── main.tsv
│       ├── merged.tsv
│       ├── output_citations.tsv
│       └── output_papers.tsv
├── pyproject.toml                          # Python dependencies (use uv!)
└─── README.md                              # This file
```
