##branje xml datotek
    ##nalaganje vseh pripravljenih xml datotek v program
    ##pretvarjanje podatkov v objekte ali strukture - deserializacija


# Branje XML datotek
# Deserializacija podatkov v Pythonove slovarje

import xml.etree.ElementTree as ET
import json
def preberi_tekmovanja():
    drevo1 = ET.parse("data/tekmovanja.xml")
    koren1 = drevo1.getroot()

    tekmovanja = {}

    for element1 in koren1.findall("tekmovanje"):
        #prebere atribut znotraj xml taga
        id_tekmovanja = element1.get("id")
        tekmovanja[id_tekmovanja] ={
            "id": id_tekmovanja, 
            "ime":element1.findtext("ime"),#prebere text znotraj podelementa
            "koda":element1.findtext("koda"),
            "tip":element1.findtext("tip"),
            "plan": element1.findtext("plan")
        }
    return tekmovanja

def preberi_tekme():
    drevo2 = ET.parse("data/tekme.xml")
    koren2 = drevo2.getroot()

    tekme ={}
    for element2 in koren2.findall("tekma"):
        id_tekme = element2.get("id")

        tekme[id_tekme]={
            "id": id_tekme,
            "tekmovanjeId": element2.get("tekmovanjeId"), 
            "datum": element2.findtext("datum"),
            "casUTC": element2.findtext("casUTC"),
            "status": element2.findtext("status"),
            "krog": element2.findtext("krog"),
            "faza":element2.findtext("faza"),
            "domacaEkipaId": element2.findtext("domacaEkipaId"),
            "gostujocaEkipaId": element2.findtext("gostujocaEkipaId"),
            "goliDomaci": element2.findtext("goliDomaci"),
            "goliGostje": element2.findtext("goliGostje")
        }
    return tekme



def preberi_ekipe():
    drevo = ET.parse("data/ekipe.xml")
    koren = drevo.getroot()

    # Slovar ekip
    ekipe = {}

    for element in koren.findall("ekipa"):

        id_ekipe = element.get("id")

        ekipe[id_ekipe] = {
            "id": id_ekipe,
            "ime": element.findtext("ime"),
            "kratkoIme": element.findtext("kratkoIme"),
            "kratica": element.findtext("kratica"),
            "drzava": element.findtext("drzava"),
            "naslov": element.findtext("naslov"),
            "letoUstanovitve": int(
                element.findtext("letoUstanovitve")
            ),
            "stadion": element.findtext("stadion"),
            "trener": element.findtext("trener"),
            "tekmovanja": [
                t.text
                for t in element.findall(
                    "tekmovanja/tekmovanjeId"
                )
            ]
        }

    return ekipe

def povezi_podatke(tekme, ekipe, tekmovanja):
    povezane_tekme=[]

    ##pregleda vse tekme v slovarju
    for tekma in tekme.values():
        #id-ji zapisani v tekme.xml
        domaca_id = tekma["domacaEkipaId"]
        gostujoca_id = tekma["gostujocaEkipaId"]
        tekmovanje_id = tekma["tekmovanjeId"]
        #poiščemo ustrezne podatke v drugih slovarjih
        domaca = ekipe[domaca_id]
        gostujoca = ekipe[gostujoca_id]
        tekmovanje = tekmovanja[tekmovanje_id]

        #ustvarimo združen zapis
        povezana_tekma = {
            "id": tekma["id"],
            "datum":tekma["datum"],
            "casUTC": tekma["casUTC"],
            "status":tekma["status"],
            "krog": tekma["krog"],
            "tekmovanje": tekmovanje["ime"],
            "domacaEkipa":domaca["ime"],
            "gostujocaEkipa":gostujoca["ime"],
            "stadion":domaca["stadion"],
            "goliDomaci":tekma["goliDomaci"],
            "goliGostje":tekma["goliGostje"],
            "tekmovanjeId": tekmovanje_id,
            "domacaEkipaId": domaca_id,
            "gostujocaEkipaId": gostujoca_id,

        }

        povezane_tekme.append(povezana_tekma)
    return povezane_tekme

def filtriraj_po_ekipi(povezane_tekme, ekipa_id):
    filtrirane = []
    for tekma in povezane_tekme:
        if (tekma["domacaEkipaId"]== ekipa_id or
            tekma["gostujocaEkipaId"] == ekipa_id
            ):
            filtrirane.append(tekma)
    return filtrirane

def filtriraj_po_datumu(povezane_tekme, datum):
    filtrirane=[]
    for tekma in povezane_tekme:
        if tekma["datum"] == datum:
            filtrirane.append(tekma)
    return filtrirane

def izvozi_json(filtrirane_tekme):
    #with open("output/filtrirano.json", "w",encoding="utf-8") as datoteka:
    with open("data/filtrirano.json", "w",encoding="utf-8") as datoteka:
        json.dump(filtrirane_tekme, datoteka, indent=4, ensure_ascii=False)

def izvozi_xml(filtrirane_tekme):
    #ustvari korenski element
    koren3 = ET.Element("tekme")

    for tekma in filtrirane_tekme:
        element_tekme = ET.SubElement(
            koren3, "tekma", id=tekma["id"]# ustvari element za posamezno tekmo z atributom ID
        )
        # pregleda vse podatke posamezne tekme in iz njih ustvari xml elemente
        for kljuc, vrednost in tekma.items():
            if kljuc == "id":
                continue
            podatek = ET.SubElement(element_tekme, kljuc)

            #če vrednost none element ostane prazen
            if vrednost is not None:
                podatek.text = str(vrednost)
    drevo3 = ET.ElementTree(koren3)

    ET.indent(drevo3, space="    ")

    drevo3.write(
        "data/filtrirano.xml",
        encoding="utf-8",
        xml_declaration=True
    )

def main():

    # Klic funkcije
    ekipe = preberi_ekipe()
    tekmovanja= preberi_tekmovanja()
    tekme = preberi_tekme()

    #povezovanje prek ID-jev:
    povezane_tekme = povezi_podatke(tekme, ekipe, tekmovanja)
    # Preizkus
    #print(ekipe["57"])
    #print(tekmovanja["2021"])
    #print(tekme["560603"])

    print("stevilo tekmovanj:", len(tekmovanja))
    print("stevilo tekem:", len(tekme))
    print("Stevilo ekip:", len(ekipe))
    print("stevilo povezanih tekem:", len(povezane_tekme))
    for tekma in povezane_tekme:
        print(
            tekma["datum"], 
            tekma["domacaEkipa"],
            "-",
            tekma["gostujocaEkipa"],
            "|",
            tekma["tekmovanje"]

        )

    print("\nIzberi način filtriranja:")
    print("1 - Filtriranje po ekipi")
    print("2 - Filtriranje po datumu")
    izbira = input("Tvoja izbira: ")
    if izbira == "1":
        ekipa_id = input("Vnesi ID ekipe: ")
        filtrirane_tekme = filtriraj_po_ekipi(povezane_tekme, ekipa_id)
        for tekma in filtrirane_tekme:
            print(
                tekma["datum"],
                tekma["casUTC"],
                "|",
                tekma["domacaEkipa"],
                "-",
                tekma["gostujocaEkipa"]
            )
    elif izbira == "2":
        datum = input("Vnesi datum (YYYY-MM-DD): ")
        filtrirane_tekme = filtriraj_po_datumu(povezane_tekme, datum)
        print(datum)
        for tekma in filtrirane_tekme:
            print(
                tekma["datum"],
                tekma["casUTC"],
                "|",
                tekma["domacaEkipa"],
                "-",
                tekma["gostujocaEkipa"]
            )

    else:
        print("neveljavna izbira")
        return
    
    izvozi_json(filtrirane_tekme)
    izvozi_xml(filtrirane_tekme)
    print("\nRezultati so shranjeni v:")
    print("data/filtrirano.json")
    print("data/filtrirano.xml")

if __name__ == "__main__":
    main()
