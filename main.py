import csv
import re
import sys
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

def main():
    """Run the election scraper."""
    base_url = "https://www.volby.cz/pls/ps2017nss/"
    check_arguments(base_url)
    url = sys.argv[1]
    file_name = sys.argv[2]
    session = requests.Session()
    first_soup = get_response(session, url)
    results, header = get_municipality_links(
        session,
        first_soup,
        base_url
    )
    print(f"Saving election results to: {file_name}")
    save_to_csv(results, header, file_name)
    print("Scraping completed successfully.")

def check_arguments(base_url: str) -> None:
    """Check whether the required command-line arguments are valid."""
    if len(sys.argv) != 3:
        print(
            "Arguments were not entered correctly. "
            "Please check README and try it again."
        )
        sys.exit(1)
    if base_url not in sys.argv[1]:
        print(
            "You have entered wrong URL. "
            "Please check README and try it again."
        )
        sys.exit(1)
    if not sys.argv[2].endswith(".csv"):
        print(
            "You have entered wrong file name. "
            "Please check README and try it again."
        )
        sys.exit(1)
    print(f"Starting download from: {sys.argv[1]}")

def get_response(
    session: requests.Session,
    url: str
) -> BeautifulSoup:
    """Download a webpage and return it as BeautifulSoup."""
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Network error fetching {url}: {error}")
        sys.exit(1)
    return BeautifulSoup(response.text, "html.parser")

def get_municipality_links(
    session,
    first_soup,
    base_url: str
) -> tuple[list[list[str]], list[str]]:
    
    """Find municipality links and collect election results."""
    results = []
    header = []
    municipalities = first_soup.find_all(
        "td",
        {"class": "cislo"}
    )
    for td_code in municipalities:
        # Find the municipality name in the same table row
        # as the municipality code.
        row = td_code.find_parent("tr")
        if not row:
            continue
        td_name = row.find(
            "td",
            {"class": "overflow_name"}
        )
        if not td_name:
            continue
        code = td_code.get_text(strip=True)
        location = td_name.get_text(strip=True)
        link = td_code.find("a")
        if not link or not link.has_attr("href"):
            print(
                f"Skipping entry (no link) for "
                f"{location} ({code})"
            )
            continue
        detail_url = urljoin(base_url, link["href"])
        second_soup = get_response(session, detail_url)
        if not header:
            header = create_header(second_soup)

        numbers = collect_numbers(second_soup)
        results.append([code, location] + numbers)

    return results, header

def collect_numbers(second_soup) -> list[str]:
    """Collect election statistics and party votes."""
    data = []

    def get_td_text(soup, headers_value):
        element = soup.find(
            "td",
            {"headers": headers_value}
        )
        if element:
            return clean_numbers(element.get_text())

        return ""
    data.append(get_td_text(second_soup, "sa2"))
    data.append(get_td_text(second_soup, "sa5"))
    data.append(get_td_text(second_soup, "sa6"))
    data.extend(collect_votes(second_soup))
    return data

def create_header(second_soup) -> list[str]:
    """Create the CSV header from party names."""
    header = [
        "code",
        "location",
        "registered",
        "envelopes",
        "valid"
    ]
    party_cells = second_soup.find_all(
        "td",
        {"class": "overflow_name"}
    )
    for party in party_cells:
        header.append(party.get_text(strip=True))

    return header

def collect_votes(second_soup) -> list[str]:
    """Collect the number of votes for each party."""
    votes = []
    pattern = re.compile(r"\bt\d+sa2\b")
    party_cells = second_soup.find_all(
        "td",
        {"class": "overflow_name"}
    )
    for party_td in party_cells:
        row = party_td.find_parent("tr")
        vote_cell = None

        if row:
            for cell in row.find_all("td"):
                headers = cell.get("headers", "")

                if isinstance(headers, (list, tuple)):
                    headers = " ".join(headers)

                if pattern.search(str(headers)):
                    vote_cell = cell
                    break
        if vote_cell:
            votes.append(
                clean_numbers(vote_cell.get_text())
            )
        else:
            votes.append("")
    return votes

def clean_numbers(number: str) -> str:
    """Remove non-breaking spaces and extra whitespace."""
    if number is None:
        return ""
    return number.replace("\xa0", "").strip()

def save_to_csv(
    results: list,
    header: list,
    file: str
) -> None:
    """Save election results to a CSV file."""
    if not header and results:
        header = [
            "Col" + str(i)
            for i in range(1, len(results[0]) + 1)
        ]
    with open(
        file,
        "w",
        encoding="utf-8",
        newline=""
    ) as csv_file:
        writer = csv.writer(csv_file, dialect="excel")
        writer.writerow(header)
        writer.writerows(results)

if __name__ == "__main__":
    main()
