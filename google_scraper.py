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
import stem.process
from stem.util import term
import pycurl
import io
import sys

OKGREEN = '\033[92m'
BOLD = '\033[1m'
ENDC = '\033[0m'

SOCKS_PORT = 7000
CONTROL_PORT = 9051
nb_req_per_page = 100

tor_process = 0
use_tor = False #Si tor est utilisé le parametre devient true


def google_scrap(query, begin=0, n=10):

    links = []
    iterations = {"success": 0, "failure": 0}

    start = begin

    while len(links) < n:

        soup = BeautifulSoup(get_html("https://www.google.com/search?q="+query+"&gbv=1&sei=w6iXV-vWOdPwgAa8s62YDg&num="+str(nb_req_per_page)+"&start="+str(start)), "html.parser")
        #print(soup)

        if soup.find_all('div', class_="center_col"):
            print(term.format("Vous atteint la limite des résultats de recherche .\n", term.Color.RED))
            break

        if len(soup.find_all('div', class_="kv")):
            iterations["success"] += 1
        else:
            iterations["failure"] += 1
            new_identity()
            continue

        for div in soup.find_all('div', class_="kv"):
            links.append(div.cite.string)
            sys.stdout.write("\r" + OKGREEN + "Avancement : " + str(len(links)) + " / " + str(n) + ENDC)
            sys.stdout.flush()

        print()
        start += nb_req_per_page

    if use_tor:
        print(term.format("Arret de Tor.\n", term.Attr.BOLD))
        kill_tor()

    return links[:n]

def get_ip():

    soup = BeautifulSoup(get_html("http://whatismyipaddress.com/"), "html.parser")

    return soup.find(id="section_left").find_all('div')[1].a.string

""" ============== Tor ============== """

""" Ces 3 fonctions ont été "grandement" inspirés de : https://stem.torproject.org/tutorials/to_russia_with_love.html"""

def init_tor():

    #print(term.format("Starting Tor:\n", term.Attr.BOLD))

    global tor_process
    tor_process = stem.process.launch_tor_with_config(
        config={
            'SocksPort': str(SOCKS_PORT)
        }
    )

    global use_tor
    use_tor = True


def kill_tor():

    #print(term.format("Killing TOR", term.Color.BLUE))
    tor_process.kill()


def get_html(url):
  """
  Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  """

  output = io.BytesIO()

  query = pycurl.Curl()
  query.setopt(pycurl.URL, url)

  if use_tor:
    query.setopt(pycurl.PROXY, 'localhost')
    query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
    query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)

  query.setopt(pycurl.USERAGENT, 'Mozilla/5.0')
  query.setopt(pycurl.WRITEFUNCTION, output.write)

  try:
    query.perform()
    return output.getvalue()
  except pycurl.error as exc:
    return "Unable to reach %s (%s)" % (url, exc)

def new_identity():
    if use_tor:
        print(term.format("Nouvelle identite : "+get_ip()+"\n", term.Color.BLUE))
        kill_tor()
        init_tor()
    else:
        print(term.format("Lancement de Tor.\n", term.Attr.BOLD))
        init_tor()


if __name__ == "__main__":

    res = google_scrap("site:.ma", 0, 1000)
    print(len(res))
    print(res)
