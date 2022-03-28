from bs4 import BeautifulSoup
import requests

from models.listentry import ListEntry
import constants as c


def run():
    url = "https://www.imdb.com/search/title/?genres=sci-fi&sort=user_rating,desc&explore=title_type,genres&ref_=adv_nxt"
    pageStart = 1
    pageEnd = 3
    pageRange = pageEnd - pageStart

    uniqueEntries = []

    for page in range(pageRange + 1) : 
        print("Page number : % s / % s (% s/% s)" % (page + 1, pageRange + 1, (pageStart + page), pageEnd))

        startPosition = CalculateStartPosition(page, pageStart)
        doc = GetDocument(url + "&start=% s" % startPosition)
        parsedList = ParseListPage(doc)

        for listItem in parsedList:
            if listItem.title not in [x.title for x in uniqueEntries]:
                uniqueEntries.append(listItem)
                print("\t% s | % s (IMDB: % s)" % (listItem.title, listItem.votes, listItem.rating))

def CalculateStartPosition(currentPage, pageStart):
    return (currentPage * 50) + (pageStart * 50) + 1

def GetDocument(url):
    result = requests.get(url)
    return BeautifulSoup(result.text, "html.parser")

def ParseListPage(doc: BeautifulSoup):
    voteDivs = GetVoteDivs(doc)
    result = []

    for voteDiv in voteDivs:
        result.append(ParseVoteDiv(voteDiv))

    return result

def GetVoteDivs(doc: BeautifulSoup):
    voteDivs = doc.find_all(class_="sort-num_votes-visible")
    return list(dict.fromkeys(voteDivs))

def ParseVoteDiv(voteDiv):
    newDiv = ListEntry()
    newDiv.votes = voteDiv.contents[3].text
    newDiv.title = voteDiv.parent.find(class_="lister-item-header").find(["a"]).text.strip()
    newDiv.rating = voteDiv.parent.find(class_="inline-block ratings-imdb-rating").find(["strong"]).text
    return newDiv

if __name__ == '__main__':
    run()