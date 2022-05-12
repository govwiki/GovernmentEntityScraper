## Overview

The goal is to find the appropriate website for each government entity in the United States by using a Google search.
The main script is located at `search.py`.

### Program Flow

We read the Texas government entities from the first tab of `data/Texas Local Governments.xlsx`, perform a Google search query using the entity name, and use some domain-specific logic to either return a suitable url or no url. The results are written to a `data/texas_websites_...xlsx` file (the most recent is `texas_websites_01_10_22.xlsx`).

### Algorithm

At a high-level, we use a two-pass algorithm where on the first pass we look for entities that contain their own website, and in the second pass we look for directory listings that come from a list of websites specified from `overrides/valid_urls.csv`.

### Manual Overrides

If there is a government entity that returns an incorrect url under the current algorithm, you can override the url returned by adding an entry to the csv file `overrides/overriden_entities.csv`. Provide the entity name _exactly_ as it appears in column A of the resultant `data/texas_websites_...xlsx` file.

### Set Up

To install the necessary dependencies, run:

```
pip install -r requirements.txt
```

### Running the Script

The main script is located at `search.py`, and the main method is `iterate`. There are a few tunable parameters to the main method that are worth mentioning.

1. `parallel` - A flag indicating whether we should run the urllib requests in parallel. Although this is faster, after a few hundred calls, Google usually blocks requests because of high load.
2. `match_correct` - A flag when set to true only finds urls for entities that have a labelled correct url (as indicated by having an entry in column `C` of the `texas_websites_...xlsx` spreadsheet). Updates column `D` as to whether the generated url matches the correct url. If the flag is false, the script finds urls for all 5000+ entities.
3. `access_url` - A flag indicating whether we should perform a http request on each website returned by the Google result. If false, we just rely on the url itself and the page title to determine the validity of a link. We've found experimentally that results are better when this flag is set to `False`.

## Locating files on Government Entity Websites

A second script in this repository conducts user-specified searches against each government website. This script is named `main.py`, and the main method is `get_url`. There are a few tunable parameters to the main method that are worth mentioning.

1. `input_file` - A flag points to the file where the urls for requests are located. (required)
2. `sheet_name` - A flag indicating name of sheet in `input_file` - excel book. (required)
3. `column_number` - A flag points to the column in `input_file` in which the required urls are located. (required)
4. `output_file` - A flag points to the file where the results will be saved. (required)
5. `config_file` - A flag points to the file with templates of requests. (required)
6. `startRow` - A flag indicating from which line in the `input_file` script execution will begin. (optional, default = 2)
7. `endRow` - A flag indicating up to which line in the `input_file` the script will be executed. (optional, default = 6)
8. `year` - A flag points to year for templates. (optional, default = 2021)

For example:
```
python main.py ./data/Local_Education_Authority_Web_Addresses.xlsx Sheet1 4 new.xlsx config.txt startRow=2 endRow=6 year=2021
```
