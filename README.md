# Google Scrapper

Un petit script qui permet de récuperer les résultats de recherche depuis les moteurs les plus utilisés

# Technologies Utilisés

* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/): Une bibliothéque de scrapping qui permet de naviguer 
facilement dans une page html.
* [Stem](https://stem.torproject.org/) : Une bibliotehque qui permet d'intégrer TOR à Python.
* [PyCUrl](http://pycurl.io/): Une bibliotehque pour récuperer le code HTML des pages, URLLib m'a posé pas mal de problèmes pour passer par TOR.

# Dependances

``` 
# apt-get install python3-bs4
# pip3 install stem
# apt-get install python3-pycurl
```

# Utilisation

``` 
$ python3 google_scraper.py --help
 
Usage: python3 google-scraper [OPTION] ... [FILE] {QUERY}
Un petit script qui permet de récuperer les résultats de recherche des moteurs connues .

Options : 
	 QUERY : La requette en question ex : program, site:.ma, inurl:index.php, etc.
	--searchEngine=SEARCH ENGINE	 Le moteur de recherche en à utiliser : Google, Bing
	--begin=X	 Par où commencer la recherche 
	--number=Y	 Nombre de résultats souhaités
	--fileout=FILE	 Le fichier ou le texte en sortie sera stoké (par défaut sortie standard
```

# Support

## Google

Pour le moment Google ne donne pas des résultats trés satisfaisants, il bloque TOR (souvent) et s'arrete aprés un nombre de résultats 
relativement petit (~100 à 400)
A moins donc d'utiliser une liste de proxies privés je recommanderai Bing pour n > 200.

## Bing

Je ne l'ai pas tésté de facon intensive mais il semble marcher sans problème.
Bing ne semble pas bloquer les requettes en provenance de TOR et offre un quota beaucoup plus important que Google.

