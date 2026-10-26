import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json #pretvori pythonove podatke v format json
from pathlib import Path #omogoča delo s potmi in datotekami
URL = "https://www.skysports.com/football/news"


def pridobi_html():
    #pridobi HTML iz SkySports
    response = requests.get(URL, timeout=15) #get request
    response.raise_for_status()# preverba statusa
    
    return response.text
    

def razcleni_novice(html):
    #izlušči naslove, povezave
    soup = BeautifulSoup(html, "html.parser") #html besedilo pretvori v strukturo, po kateri lahko iscemo posamezne elemente
    novice = []
    ze_dodane = set()

    naslovi = soup.find_all("h3") #poišče vse elemente h3 ki lahko predstavljajo naslove novic

    for naslov in naslovi:
        povezava = naslov.find("a") #

        if povezava is None:
            povezava = naslov.find_parent("a")# poisceta povezavo znotraj naslova ali povezavo ki obdaja naslov

        if povezava is None:
            continue
        besedilo = naslov.get_text(strip=True) #iz naslova pridobi samo besedilo brez html oznak in odvečnih presledkov
        href = povezava.get("href")

        if not besedilo or not href:
            continue
        url = urljoin(URL, href) #relativno povezavo pretvori v absolutno povezavo

        if url in ze_dodane: # preprecuje da bi isto povezavo shranili večkrat
            continue
        ze_dodane.add(url)

        novice.append({
            "title": besedilo,
            "url": url
        })
    return novice
def shrani_json(novice):
    #shrani podatke v json
    pot = Path(__file__).parent / "data" / "football_news.json" #določi pot do JSON datoteke glede na lokacijo main.py
    pot.parent.mkdir(parents=True, exist_ok=True) #če direktorij data ne obstaja ga python samodejno ustvari; ustvarjanje direktorija
    with open(pot, "w", encoding="utf-8") as datoteka: #w odpre datoteko za pisanje, če že obstaja prepiše njeno vsebino, encoding omogoča pravilno shranjevanje posebnih znakov, with po zaključku samodejno zapre datoteko
        json.dump(novice, datoteka, ensure_ascii=False, indent=4)#novice-seznam novic ki ga vrne funkcija razcleni_novice(), ensure_ascii = false - ohrani znake kot so č,ž,... , indent za boljšo berljivost
    print(f"Uspešno shranjenih: {len(novice)} novic")
    pass

def main():
    html = pridobi_html()
    novice = razcleni_novice(html)
    print(f"Najdenih novic: {len(novice)}")
    for novica in novice:
        print("Naslov: ", novica["title"])
        print("Povezava: ", novica["url"])
        print()
    if novice:
        shrani_json(novice)
    else: 
        print("Ni najdenih novic.")

if __name__ == "__main__":
    main()