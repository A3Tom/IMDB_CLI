from bs4 import BeautifulSoup
import requests

from models.listentry import ListEntry
import constants as c

def run():
    RunUntilResultCountMet()

def RunUntilResultCountMet():
    url = CalculateBaseUrl()

    targetCount = 10
    voteThreshold: int = 1000
    uniqueEntries = []

    currentPage = 1
    while(len(uniqueEntries) < targetCount) :
        print("Parsing page % s | Unique Entries found so far : % s" % (currentPage, len(uniqueEntries)))
        startPosition = CalculateStartPosition(currentPage, 1)
        doc = GetDocument(url + "&start=% s" % startPosition)
        parsedList = ParseListPage(doc)

        for entry in parsedList:
            if (int(entry.votes) >= voteThreshold and
                entry.title not in [x.title for x in uniqueEntries]):
                    uniqueEntries.append(entry)
        
        currentPage += 1
    
    for entry in uniqueEntries:
        PrettifyListItemLine(entry)
        

def RunForXPages():
    url = CalculateBaseUrl()
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
                PrettifyListItemLine(listItem)

def PrettifyListItemLine(listItem):
    print("\t% s | % s (IMDB: % s) [% s]" % (listItem.title, listItem.votes, listItem.rating, ", ".join(listItem.genres)))

def CalculateBaseUrl(type = "title", genre = "sci-fi", sort = "user_rating", order = "desc"):
    baseUrl = "https://www.imdb.com/search"
    sort = "sort=% s,% s" % (sort, order)
    genres = "genres=% s" % (genre)
    return baseUrl + "/% s/?% s&% s&explore=title_type,genres" % (type, genres, sort)

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
    newDiv.votes = int(voteDiv.contents[3].text.replace(",", ""))
    newDiv.title = voteDiv.parent.find(class_="lister-item-header").find(["a"]).text.strip()
    newDiv.rating = voteDiv.parent.find(class_="inline-block ratings-imdb-rating").find(["strong"]).text
    newDiv.genres = voteDiv.parent.find(class_="genre").text.strip().split(",")
    return newDiv

if __name__ == '__main__':
    run()