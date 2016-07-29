""""
 * ************* Google Scrapper ***************
 *
 * Ecrit par Yassir Karroum [ukarroum17@gmail.com]
 * Le 26 juillet 2016
 *
 * Un simple script qui permet de récuperer les résultats de google pour une requette donnée sans devoir passer par l'API
 * Il permet aussi de contrer la limite imposée par Google en passant par TOR.
 */
"""
from bs4 import BeautifulSoup
import urllib.request

def google_scrap(query, begin=0, n=10):

    links = []
    iterations = {"success": 0, "failure": 0}

    start = begin;

    while len(links) < n:
        req = urllib.request.Request("https://www.google.com/search?q="+query+"&gbv=1&sei=w6iXV-vWOdPwgAa8s62YDg&num=100&start="+str(start))
        req.add_header('User-agent', 'Mozilla/5.0')

        soup = BeautifulSoup(urllib.request.urlopen(req).read(), "html.parser")

        if len(soup.find_all('cite')):
            iterations["success"] += 1
        else:
            iterations["failure"] += 1

        for link in soup.find_all('cite'):
            links.append(link.string)

        #start += 100
        print(iterations)
        print(len(links))

    print(len(links))

    return links[:n]


    #print(soup)

if __name__ == "__main__":
    print(google_scrap("test"))

