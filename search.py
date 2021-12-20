import urllib
import requests
from bs4 import BeautifulSoup
import re
import url_checker
import logging
import datetime
import sys
import time

import openpyxl
from pathlib import Path
import concurrent.futures

# Setup logging
now = datetime.datetime.now()
date_time = now.strftime("%Y-%m-%d %H-%M-%S")

logger = logging.getLogger()
handler = logging.FileHandler(
    mode="w", filename="logs/search_" + date_time + ".txt")
handler.setLevel(logging.INFO)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def getBingSearchResults(query):
    # desktop user-agent
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

    query = query.replace(' ', '+')
    URL = f"https://bing.com/search?q={query}"

    headers = {"user-agent": USER_AGENT}
    resp = requests.get(URL, headers=headers)

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, "html.parser")
        results = []
        for g in soup.find_all('ol', id='b_results'):
            anchors = g.find_all('a')
            for anchor in anchors:
                if 'href' in anchor.attrs:
                    href = anchor['href']
                    if '/search' not in href and 'http' in href:
                        results.append(href)
                        # print(str(href))
        return results
    else:
        print("invalid code")
        return []


def getGoogleSearchResults(query):
    # desktop user-agent
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

    query = query.replace(' ', '+')
    URL = f"https://google.com/search?q={query}"

    headers = {"user-agent": USER_AGENT}
    resp = requests.get(URL, headers=headers)

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, "html.parser")
        results = []
        for g in soup.find_all('div', 'tF2Cxc'):
            anchors = g.find_all('a')
            for anchor in anchors:
                if 'href' in anchor.attrs:
                    href = anchor['href']
                    if '/search' not in href and 'http' in href:
                        results.append(href)
                        # print(str(href))
        return results
    else:
        print("invalid code")
        return []


def getMatchingLink(query):
    links = getGoogleSearchResults(query)
    matchingLink = ""
    for link in links:
        if 'wikipedia' not in link and 'facebook' not in link:
            status = url_checker.getStatusCode(link)
            if status == 200:
                matchingLink = link
                break
    return matchingLink


def iterate(excel_filename, tab_name, column, output_file=None, fn=None,
            suffix="",
            header_exists=True, debug=False,
            startRow=1, parallel=True):
    xlsx_file = Path(excel_filename)
    wb_obj = openpyxl.load_workbook(xlsx_file)
    wsheet = wb_obj[tab_name]
    rowNumber = 1
    if header_exists:
        rowNumber = 2
    statusCodeMap = {}
    collection = []
    book = openpyxl.load_workbook(output_file)
    increment = 10
    start = time.time()
    if parallel:
        while rowNumber < startRow:
            rowNumber += 1

        while rowNumber < wsheet.max_row:
            entities = getEntities(
                rowNumber, wsheet, increment, column, suffix)
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                for index, (entityName, entityUrl) in enumerate(zip(entities, executor.map(fn, entities))):
                    book['Sheet1']['A' +
                                   str(index+rowNumber)].value = entityName
                    book['Sheet1']['B' +
                                   str(index+rowNumber)].value = entityUrl
                    # print("%s -- %s" % (entityName, entityUrl))
            book.save(output_file)
            elapsed = time.time() - start
            print("%d  (%.1f)" % (rowNumber, elapsed))
            rowNumber += increment
    else:
        for row in wsheet.iter_rows(max_row=wsheet.max_row):
            rowNumber += 1
            if rowNumber < startRow:
                continue
            nameCell = column + str(rowNumber)
            entityName = wsheet[nameCell].value + " " + suffix

            res = fn(entityName)
            book['Sheet1']['A' + str(rowNumber)].value = entityName
            book['Sheet1']['B' + str(rowNumber)].value = res
            if rowNumber % 10 == 0:
                elapsed = time.time() - start
                print("%d (%.1f)" % (rowNumber, elapsed))
                book.save(output_file)

    book.save(output_file)


def getEntities(start_row, wsheet, increment, column, suffix):
    max_row = min(start_row+increment, wsheet.max_row)
    entities = []
    for row in range(start_row, max_row+1, 1):
        nameCell = column + str(row)
        entityName = wsheet[nameCell].value + " " + suffix
        entities.append(entityName)
    return entities


iterate('Texas Local Governments.xlsx', 'Census of Govts',
        'D', output_file='texas_websites_1.xlsx', fn=getMatchingLink,
        suffix="Texas",
        debug=True, parallel=False, startRow=500)
