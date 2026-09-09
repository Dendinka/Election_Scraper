# Election Scraper 

This project is a web scraper for the 2017 Czech parliamentary elections.
It downloads election results from the official Czech election results website and saves them into a CSV file.

The scraper collects election results for all municipalities within a selected territorial unit.

## Installation

Make sure Python 3 is installed on your computer.

It is recommended to create and activate a virtual environment for the project.

Install the required libraries using:

```bash
pip install -r requirements.txt
```

## How to run

The program is run from the terminal using two command-line arguments.

The first argument is the URL of the selected territorial unit.
The second argument is the name of the output CSV file.

```bash
python main.py "TERRITORIAL_UNIT_URL" vysledky.csv
```

For example, to scrape election results for the Prachatice district:

```bash
python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=3&xnumnuts=3105" vysledky_prachatice.csv
```

The output file name must end with `.csv`.

The program does not use the `input()` function. All required information is entered through command-line arguments.

## Output

The scraper creates a CSV file containing one row for each municipality.

The output includes:

- municipality code
- municipality name
- number of registered voters
- number of issued voting envelopes
- number of valid votes
- number of votes received by each political party

The first row of the CSV file contains the column names.

## Error handling

The program checks whether:

- exactly two command-line arguments were provided
- the entered URL belongs to the 2017 Czech parliamentary election results website
- the output file has a `.csv` extension
- the website can be accessed successfully

If the arguments are invalid or a network error occurs, the program displays an error message and terminates.

## Project structure

```text
.
├── main.py
├── requirements.txt
├── README.md
└── vysledky_prachatice.csv
```