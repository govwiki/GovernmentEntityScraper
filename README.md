## Overview

The goal is to find the appropriate website for each government entity in the United States by using a Google search.
Currently, it is limited to Texas government entities. The main script is located at `search.py`.

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
