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
    # USER_AGENT = "my bot"

    
    no_missing = "SCH DIST" in query
    # no_missing = False

    query = query.replace(' ', '+')
    URL = f"https://google.com/search?q={query}"

    headers = {"user-agent": USER_AGENT}
    resp = requests.get(URL, headers=headers)

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, "html.parser")
        results = []
        
        topResults = 6
        count = 0
        for g in soup.find_all('div', 'tF2Cxc'):
            anchors = g.find_all('a')
            missingDivs = g.find_all('div', 'TXwUJf')
            count += 1
            if count > topResults:
                break
            for anchor in anchors:
                if 'href' in anchor.attrs:
                    href = anchor['href']
                    if '/search' not in href and 'http' in href:
                        if len(missingDivs) == 0 or no_missing:
                            results.append(href)
                        else:
                            logger.info("missing div: " + str(href))
                            # results.append(href)
                        # print(str(href))

        return results
    else:
        print("bad request: " + str(resp.headers))
        return []


def getMatchingLink(query):
    print("   ")
    links = getGoogleSearchResults(query)
    matchingLink = ""
    # logger.info(" --- " + str(query) + " ---")
    # for link in links:
    #     print(link)
    # print("   ")
    for link in links:
        if is_valid_link1(link, query):
            status = url_checker.getStatusCode(link)
            logger.info(link + " --- " + str(status))
            if is_valid_status(status):
                matchingLink = link
                break
        else:
            logger.info(link + "--- invalid")
    if matchingLink == '':
        print("--------")
        for link in links:
            if is_valid_link2(link):
                status = url_checker.getStatusCode(link)
                logger.info("2nd pass: " + link + " --- " + str(status))
                if is_valid_status(status):
                    matchingLink = link
                    break
    logger.info("   ")
    return matchingLink


def is_valid_status(status):
    return status == 200 or status == 406 or status == 403


invalid_urls = ['wikipedia', 'facebook',
                'books.google', 'city-data', 'mapquest', 'manta', 'yellowpages']

valid_suffixes = ['home', 'index', 'main', 'en.html']

valid_entities = ['county', 'town', 'city']


def is_valid_link1(link, query):
    slashes = num_slashes(link)
    words = query.split(" ")
    if len(words) >= 3:
        entityType = words[0].lower()
        if entityType in valid_entities:
            entityName = words[2].lower()
            if entityName not in link.lower():
                return False

    if slashes >= 4:
        return False
    if slashes == 3:
        suffix = getPage(link)
        for valid_suffix in valid_suffixes:
            if valid_suffix in suffix:
                return True
        return False
    for invalid_url in invalid_urls:
        if invalid_url in link:
            return False
    return True


valid_2_urls = ['tsswcb.texas.gov']


def is_valid_link2(link):
    slashes = num_slashes(link)
    for valid_url in valid_2_urls:
        if valid_url in link:
            return True
    return False
    # if '.gov' in link:
    #     return True
    # return False


def num_slashes(link):
    count = 0
    for letter in link[:-1]:
        if letter == '/':
            count += 1
    return count


def getPage(link):
    count = 0
    for i, letter in enumerate(link[:-1]):
        if letter == '/':
            count += 1
        elif count >= 3:
            return link[i:]
    return ''


def iterate(excel_filename, tab_name, column, output_file=None, fn=None,
            suffix="",
            header_exists=True, debug=False,
            startRow=1, parallel=True, match_correct=False, endRow=1):
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

        while rowNumber < wsheet.max_row and rowNumber < endRow:
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
        if match_correct:
            count = 0
            num_correct = 0
            num_filled = 0
            saved = False
            for row in wsheet.iter_rows(max_row=wsheet.max_row):
                rowNumber += 1
                if rowNumber < startRow:
                    continue

                nameCell = column + str(rowNumber)
                # print(rowNumber)
                if wsheet[nameCell].value is None:
                    continue
                entityName = wsheet[nameCell].value + " " + suffix

                correct_url = book['Sheet1']['C' + str(rowNumber)].value
                if correct_url is not None:
                    logger.info(entityName + ": \"" + str(correct_url) + "\"")
                    res = fn(entityName)
                    book['Sheet1']['A' + str(rowNumber)].value = entityName
                    book['Sheet1']['B' + str(rowNumber)].value = res
                    if res == correct_url or (res == '' and correct_url == 'None'):
                        book['Sheet1']['D' + str(rowNumber)].value = 'Yes'
                        num_correct += 1
                        num_filled += 1
                    elif (res == '' and correct_url != 'None'):
                        book['Sheet1']['D' + str(rowNumber)].value = 'Blank'
                    else:
                        book['Sheet1']['D' + str(rowNumber)].value = 'No'
                        num_filled += 1
                    count += 1
                    saved = False
                if count % 10 == 0 and not saved:
                    elapsed = time.time() - start
                    # logger.info("%d (%.2f)" %
                    #             (rowNumber, num_correct / (num_filled + 0.01)))
                    logger.info("%d correct: %d, filled: %d, total: %d",
                                rowNumber, num_correct, num_filled, count)
                    logger.info("accuracy: %.3f " %
                                (num_correct / (num_filled + 0.01)))
                    book.save(output_file)
                    saved = True

            logger.info("%d correct: %d, filled: %d, total: %d",
                        rowNumber, num_correct, num_filled, count)
            book.save(output_file)

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
                    logger.info("%d (%.1f)" % (rowNumber, elapsed))
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
        'D', output_file='texas_websites_01_05_22_MJ.xlsx', fn=getMatchingLink,
        suffix="Texas",
        debug=True, parallel=False, match_correct=False, startRow=1, endRow=500)
