""""
 * ************* Google Scrapper ***************
 *
 * Ecrit par Yassir Karroum [ukarroum17@gmail.com] [https://github.com/ukarroum]
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
import getopt

OKGREEN = '\033[92m'
BOLD = '\033[1m'
ENDC = '\033[0m'

SOCKS_PORT = 7000
nb_req_per_page = 10

tor_process = 0
use_tor = False   # Si tor est utilisé le parametre devient true

# En choisissant de passer par les relais d'un meme pays
# Les résultats deviennent plus cogérents entre eux.

use_contry_code = True
country_code = "fr"  # Un choix arbitraire qui est du à un nombre plutot elevé des relais francais.


g_opts = {'searchEngine': 'Bing',
          'begin': 0,
          'number': 10,
          'fileout': sys.stdout}


def print_help():
    """Affiche l'aide du script """

    print("Usage: python3 google-scraper [OPTION] ... [FILE] {QUERY}")
    print(
        "Un petit script qui permet de récuperer les résultats de recherche des moteurs connues .\n")

    print("Options : ")
    print("\t QUERY : La requette en question ex : program, site:.ma, inurl:index.php, etc.")
    print("\t--searchEngine=SEARCH ENGINE\t Le moteur de recherche en à utiliser : Google, Bing, StartPage (Proxy Google)")
    print("\t--begin=X\t Par où commencer la recherche ")
    print("\t--number=Y\t Nombre de résultats souhaités")
    print("\t--fileout=FILE\t Le fichier ou le texte en sortie sera stoké (par défaut sortie standard")


def start_page_scrap(query, begin=0, n=10):
    """
        StartPage Scrap : Permet de récupérer le résultat depuis le moteur google en passant par startpage.

    :param query: La requette de recherche, par example : python, site:.ma, inurl:index.php
    :param begin: Par où commencer la recherche .
    :param n: Nombre de résultats souhaités
    :return: Liste contenant les liens.
    """

    links = []
    iterations = {"success": 0, "failure": 0}

    start = begin

    while len(links) < n:

        # Les parametres dont je connais l'utilité sont :
        # prf : Contient les préférences de recherche (nombre de résutats par page) sans passer par les cookies.
        # language : permet de fixer le language en anglais quelquesoit l'ip source.
        #            pratique pour utiliser des phrases anglaises dans les conditions au lieu de chercher des balises.
        # Les autres devront etre enlevés par la suite.
        soup = BeautifulSoup(get_html("https://www.startpage.com/do/search?cmd=process_search&language=english&qid=NBLORKMNPMTQ989HVWJUE&rcount=&rl=NONE&abp=-1&t=air&query="+query+"&cat=web&engine0=v1all&startat"+str(start)), "html.parser")

        if "Sorry, there are no Web results for this search!" in soup:
            print(term.format("Vous atteint la limite des résultats de recherche .\n", term.Color.RED))
            break

        if len(soup.find_all('span', class_="url")):
            iterations["success"] += 1
        else:
            iterations["failure"] += 1
            new_identity()
            continue

        for span in soup.find_all('span', class_="url"):
            links.append(span.string)
            sys.stdout.write("\r" + OKGREEN + "Avancement : " + str(len(links)) + " / " + str(n) + ENDC)
            sys.stdout.flush()

        print()
        start += nb_req_per_page

    if use_tor:
        print(term.format("Arret de Tor.\n", term.Attr.BOLD))
        kill_tor()

    return links[:n]


def google_scrap(query, begin=0, n=10):
    """ google scrap : Permet de récuperer le résultat depuis le moteur de recherche google .

        query : La requette de recherche, par example : python, site:.ma, inurl:index.php
        begin : Par où commencer la recherche .
        n     : Nombre de résultats souhaités"""

    links = []
    iterations = {"success": 0, "failure": 0}

    start = begin

    while len(links) < n:

        soup = BeautifulSoup(get_html("https://www.google.com/search?q="+query+"&gbv=1&sei=w6iXV-vWOdPwgAa8s62YDg&num="+str(nb_req_per_page)+"&start="+str(start)), "html.parser")

        if soup.find_all('div', id="resultStats") and soup.find_all('div', id="resultStats")[0].string == None:
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


def bing_scrap(query, begin=0, n=10):

    links = []
    iterations = {"success": 0, "failure": 0}

    start = begin

    while len(links) < n:

        soup = BeautifulSoup(get_html("http://www.bing.com/search?q="+query+"&go=Submit+Query&qs=ds&first"+str(start)), "html.parser")

        if soup.find_all('div', class_="b_no"):
            print(term.format("Vous atteint la limite des résultats de recherche .\n", term.Color.RED))
            break

        if len(soup.find_all('div', class_="b_attribution")):
            iterations["success"] += 1
        else:
            iterations["failure"] += 1
            new_identity()
            continue

        for div in soup.find_all('div', class_="b_attribution"):
            links.append(div.cite.get_text())
            sys.stdout.write("\r" + OKGREEN + "Avancement : " + str(len(links)) + " / " + str(n) + ENDC)
            sys.stdout.flush()

        print()
        start += 10

    if use_tor:
        print(term.format("Arret de Tor.\n", term.Attr.BOLD))
        kill_tor()

    return links[:n]


def save_file(links, file):
    if file == sys.stdout:
        f = sys.stdout
    else:
        f = open(file, 'w')

    for link in links:
        if link == None:
            continue
        f.write(link + '\n')

""" ============== Tor ============== """

""" Ces 3 fonctions ont été "grandement" inspirés de : https://stem.torproject.org/tutorials/to_russia_with_love.html"""


def init_tor():

    global tor_process

    if use_contry_code:
        tor_process = stem.process.launch_tor_with_config(
            config={
                'SocksPort': str(SOCKS_PORT),
                'ExitNodes': '{'+country_code+'}'
            }
        )
    else:
        tor_process = stem.process.launch_tor_with_config(
            config={
                'SocksPort': str(SOCKS_PORT)
            }
        )

    global use_tor
    use_tor = True


def kill_tor():

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

    query.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0')
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


def get_ip():

    soup = BeautifulSoup(get_html("http://whatismyipaddress.com/"), "html.parser")

    return soup.find(id="section_left").find_all('div')[1].a.string


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print_help()
        sys.exit(-1)
    try:
        opts, query = getopt.getopt(sys.argv[1:], "", ["help", "searchEngine=", "fileout=", "number=", "begin="])
        query = query[0]
    except:
        print_help()
        sys.exit(-1)

    for opt, arg in opts:

        if opt == '--help':
            print_help()
            sys.exit(0)
        if opt == '--searchEngine':
            g_opts['searchEngine'] = arg
        if opt == '--number':
            g_opts['number'] = arg
        if opt == '--begin':
            g_opts['begin'] = arg
        if opt == '--fileout':
            g_opts['fileout'] = arg

    if g_opts['searchEngine'] == 'Google':
        links = google_scrap(query, int(g_opts["begin"]), int(g_opts["number"]))
    elif g_opts['searchEngine'] == 'Bing':
        links = bing_scrap(query, int(g_opts["begin"]), int(g_opts["number"]))
    elif g_opts['searchEngine'] == 'StartPage':
        links = start_page_scrap(query, int(g_opts["begin"]), int(g_opts["number"]))

    save_file(links, g_opts['fileout'])


