from bs4 import BeautifulSoup
import requests
import json
import time

STEM = "https://en.wikipedia.org"
cleanTopic = lambda x: " ".join([y.lower() for y in x.split("_")])
pagesVisited = set()

def scrape_page(page):
    print(page)
    page = requests.get(page)
    soup = BeautifulSoup(page.content, "html.parser")
    results = []
    for p in soup.select("#mw-content-text")[0].find_all("p"):
        results.append(p.get_text())
    return "\n".join(results)

def scrape_page_links(topic):
    topic = "_".join(topic.split(" "))
    page = requests.get(STEM + "/wiki/" + topic)
    soup = BeautifulSoup(page.content, "html.parser")
    results = {cleanTopic(topic):scrape_page(STEM + "/wiki/" + topic)}

    #getting all href links: only look at links in the actual text content
    paragraphs = soup.select("#mw-content-text")[0].find_all("p")
    links = []
    for p in paragraphs:
        links.extend(p.find_all("a", href=True))

    for l in links:
        result = ""
        nextTopic = cleanTopic(l["href"].split("/")[-1])
        nextPage = STEM + l["href"]
        if l["href"] in pagesVisited or "cite_note-" in l["href"]: #skip if we've seen this page before
            continue
        else:
            pagesVisited.add(l["href"])

        try: #if requests can't find this page, just skip
            result = scrape_page(nextPage)
        except:
            print("SKIPPING: " + nextPage)
        results[nextTopic] = result
    
    return results

if __name__ == "__main__":
    start = time.time()
    topics = ["areas_of_mathematics", "branches_of_science", 
    "list_of_popular_music_genres", "politics", "history_of_the_united_states", "computer science"]
    results = {}
    for topic in topics:
        print("\n\n\n------------------")
        print("TOPIC: " + topic)
        result = scrape_page_links(topic)
        results[cleanTopic(topic)] = result
    
    print("Time taken: {}".format(time.time() - start))
    with open("fullListsData.json", "w") as f:
        json.dump(results, f)