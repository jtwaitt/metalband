import sys
import csv
import argparse
import re
import os
import json
from lxml import etree
from collections import defaultdict
import pyalex
from tqdm import tqdm

# --- Configuration ---
# A list of DBLP record types we consider to be citable publications.
PUBLICATION_TAGS = {
    "article",
    "inproceedings",
    "proceedings",
    "book",
    "incollection",
    "phdthesis",
    "mastersthesis",
}
API_CACHE_FILE = "api_cache.json"


# --- Caching Functions ---
def load_api_cache():
    """Loads the API cache from a JSON file if it exists."""
    if os.path.exists(API_CACHE_FILE):
        print(f"Loading API cache from {API_CACHE_FILE}...")
        with open(API_CACHE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_api_cache(cache):
    """Saves the API cache to a JSON file."""
    print(f"\nSaving API cache to {API_CACHE_FILE}...")
    with open(API_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


# --- API Query Functions ---
def get_openalex_citation_years(doi, cache):
    """
    Finds the publication years of all works that cite a given DOI using pyalex.
    Handles pagination automatically and uses the cache.
    """
    if not doi:
        return []

    # Check cache first
    cache_key = f"openalex_{doi}"
    if cache_key in cache:
        return cache[cache_key]

    print(f"  [API] Querying OpenAlex for citations of DOI: {doi}")
    citation_years = []
    try:
        # Use pyalex to find works that cite the given DOI.
        # The .get() method returns an iterator that handles all pagination.
        id = pyalex.Works()[f"https://doi.org/{doi}"]["id"]
        print("ID IS:", id)
        citing_works_iterator = (
                pyalex.Works().filter(cites=id).get(per_page=200)
        )

        ignore_title = "The Living Review on Automated Program Repair"
        count = 0
        for work in citing_works_iterator:

            if work.get("publication_year"):
                citation_years.append(work["publication_year"])

    except Exception as e:
        # Catch potential API errors from pyalex
        print(
            f"    [WARN] PyAlex API request failed for DOI {doi}: {e}", file=sys.stderr
        )
        return []

    # Store result in cache
    cache[cache_key] = citation_years
    return citation_years


# --- DBLP Processing Functions ---
def normalize_title(title):
    """Normalizes a title for robust matching."""
    if not title:
        return ""
    return re.sub(r"[\W_]+", "", title.lower())


def build_citation_database(dblp_xml_path):
    """Parses the DBLP XML to build in-memory lookup tables."""
    print("Phase 1: Building citation database from DBLP XML...")
    doi_to_key_map = {}
    title_to_key_map = {}
    citations_map = defaultdict(list)

    try:
        context = etree.iterparse(
            dblp_xml_path,
            events=("end",),
            tag=PUBLICATION_TAGS,
            load_dtd=True,
            encoding="ISO-8859-1",
        )
    except etree.XMLSyntaxError:
        print(
            "Error: DBLP XML is malformed. Ensure dblp.dtd is in the same directory.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Approximate records in DBLP for a nice progress bar
    total_records = 70000000
    with tqdm(
        total=total_records, desc="Parsing DBLP", unit=" records", unit_scale=True
    ) as pbar:
        for event, elem in context:
            pbar.update(1)
            dblp_key = elem.get("key")
            if not dblp_key:
                elem.clear()
                while elem.getprevious() is not None:
                    del elem.getparent()[0]
                continue

            title_elem = elem.find("title")
            if title_elem is not None and title_elem.text:
                normalized = normalize_title(title_elem.text)
                if normalized:
                    title_to_key_map[normalized] = dblp_key

            for ee in elem.findall("ee"):
                if ee.text and "doi.org/" in ee.text:
                    doi = ee.text.split("doi.org/")[-1]
                    doi_to_key_map[doi] = dblp_key
                    break

            year_elem = elem.find("year")
            if year_elem is not None and year_elem.text:
                try:
                    citing_year = int(year_elem.text)
                    for citation in elem.findall("cite"):
                        if citation.text and citation.text != "...":
                            citations_map[citation.text].append(citing_year)
                except (ValueError, TypeError):
                    pass

            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

    print("\nFinished Phase 1. DBLP database built.")
    return doi_to_key_map, title_to_key_map, citations_map

def calculate_death_year(year_threshold, citation_threshold, citation_years, birth_year):
    "Uses a sliding window to check if a citation threshold is met over every set of year_thresholds."
    
    #create a list of citations per year before calculation
    citation_years = sorted(citation_years)
    final_citation = max(citation_years)
    citations_per_year = [0] * (final_citation - birth_year + 1)
    #print(citations_per_year)
    
    for citation in citation_years:
        #print("CITATION:", citation, "BIRTH_YEAR:", birth_year, end=" || ")
        #print(citation - birth_year)
        year = citation - birth_year
        if year < 0:
            year = 0
        citations_per_year[year] += 1
    #print(citations_per_year)

    for i in range(year_threshold):
        citations_per_year.append(0)

    #build initial sliding window
    citation_count = 0
    for i in range(year_threshold):
        citation_count += citations_per_year[i]
    
    if citation_count < citation_threshold:
       
        return birth_year
    
    #move sliding window through rest of list
    for i in range(year_threshold, len(citations_per_year)):
        citation_count -= citations_per_year[i - year_threshold]
        citation_count += citations_per_year[i]
        if citation_count < citation_threshold:
            return birth_year + i
    
    return birth_year + len(citations_per_year)
    
"""
OUTDATED CALCULATE DEATH6

#REWORK - This isn't quite the defined threshold. Implmenet a sliding window to do the calculations.
def calculate_death_year(year_threshold, citation_threshold, citation_years, birth_year):
    #Goes through list of cited years and returns the death year based on threshold definition
    citation_years = sorted(citation_years)
    final_year = citation_years[-1]
    
    citation_count = 0
    year_count = 0
    for year in range(birth_year, final_year):
        while (citation_years[0]) == year:
            citation_count += 1
            citation_years.pop(0)
        year_count += 1
        if citation_count >= citation_threshold:
            citation_count = 0
            year_count = 0
        if year_count >= year_threshold:
            if citation_count < citation_threshold:
                return year - (year_count - 1)
            else:
                year_count = 0
                citation_count = 0
    return final_year #this kills all papers on the final year they are cited. Works fine for papers who die on last citation, terribly for papers makikng it to 2025

"""

# --- Main Processing Logic ---
def process_papers(args):
    """Main function to process papers from TSV and find last cited year."""

    # --- Step 1: Configure APIs and Load data sources ---
    pyalex.config.email = args.email  # Configure pyalex with your email
    pyalex.config.api_key = "hVyPpgPKaOnAAKMpRGZVNI"
    api_cache = load_api_cache()

    doi_map, title_map, dblp_citations = {}, {}, defaultdict(list)
    if not args.no_dblp:
        if not os.path.exists(args.dblp_xml) or not os.path.exists("dblp.dtd"):
            print(
                "Warning: dblp.xml or dblp.dtd not found. Skipping DBLP analysis.",
                file=sys.stderr,
            )
            args.no_dblp = True
        else:
            doi_map, title_map, dblp_citations = build_citation_database(args.dblp_xml)

    # --- Step 2: Process the input TSV ---
    print("\nPhase 2: Processing input TSV and querying APIs...")
    try:
        with open(args.input_tsv, "r", encoding="utf-8") as infile:
            reader = list(csv.reader(infile, delimiter="\t"))
            header = reader[0]
            rows = reader[1:]

        doi_idx = header.index("DOI")
        title_idx = header.index("title")
        birth_idx = header.index("year")

        output_rows = []
        for row in tqdm(rows, desc="Processing papers"):
            paper_doi = row[doi_idx].strip()
            paper_title = row[title_idx].strip()
            all_citation_years = []

            # 1. Get citations from DBLP
            if not args.no_dblp:
                dblp_key = doi_map.get(paper_doi) or title_map.get(
                    normalize_title(paper_title)
                )
                if dblp_key and dblp_key in dblp_citations:
                    all_citation_years.extend(dblp_citations[dblp_key])

            # 2. Get citations from OpenAlex using pyalex
            if not args.no_openalex:
                openalex_years = get_openalex_citation_years(paper_doi, api_cache)
                all_citation_years.extend(openalex_years)

            if all_citation_years:
                last_cited_year = calculate_death_year(args.years, args.citations, all_citation_years, int(row[birth_idx]))
                #last_cited_year = max(all_citation_years) #last cited definition, currently using the threshold definition
            else:
                last_cited_year = int(row[birth_idx])
                #last_cited_year = "NOT_CITED" #We will be killing papers year they are born instead if no citations are found.

            output_rows.append(row + [str(min(last_cited_year, 2023))])

        # Write output file
        with open(args.output_tsv, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.writer(outfile, delimiter="\t")
            writer.writerow(header + ["last_cited_year"])
            writer.writerows(output_rows)

        print(f"\nFinished Phase 2.")
        print(f"Output with augmented citation data written to '{args.output_tsv}'.")

    except FileNotFoundError:
        print(f"Error: Input file not found at '{args.input_tsv}'", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Missing required column in TSV header: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Always save the cache, even if the script is interrupted
        save_api_cache(api_cache)


def main():
    parser = argparse.ArgumentParser(
        description="Find the last year a paper was cited using DBLP and OpenAlex (via pyalex).",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "input_tsv", help="Path to the input TSV file with paper metadata."
    )
    parser.add_argument(
        "--email",
        required=True,
        help="Your email address. Required for 'polite' API access to OpenAlex.",
    )
    parser.add_argument(
        "--output_tsv",
        help="Path for the output TSV file (default: [input_filename]_with_citations.tsv).",
    )
    parser.add_argument(
        "--dblp_xml",
        default="dblp.xml",
        help="Path to the DBLP XML file (default: dblp.xml).",
    )
    parser.add_argument(
        "--no-dblp", action="store_true", help="Do not use the DBLP data source."
    )
    parser.add_argument(
        "--no-openalex", action="store_true", help="Do not use the OpenAlex API."
    )
    parser.add_argument(
        "-years",
        "--years",
        type=int,
        default=3,
        help="The number of years a paper can go wihtout meeting citation requirements before dying"
    )
    parser.add_argument(
        "-cites",
        "--citations",
        type=int,
        default=5,
        help="The number of citations needed to be considered alive"
    )

    args = parser.parse_args()

    if not args.output_tsv:
        base, ext = os.path.splitext(args.input_tsv)
        args.output_tsv = f"{base}_with_citations.tsv"

    process_papers(args)


if __name__ == "__main__":
    main()
