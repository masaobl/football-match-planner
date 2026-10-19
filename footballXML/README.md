
# NogometXML

## Opis projekta
Konzolna aplikacija za obdelavo nogometnih podatkov,
pridobljenih iz football-data.org API-ja.

Aplikacija omogoča:
- Branje XML podatkov o tekmovanjih, tekmah in ekipah.
- Povezovanje podatkov preko ID-jev.
- Filtriranje nogometnih tekem.
- Izvoz rezultatov v JSON in XML.

Izvorne xml datoteke in filrirane datoteke se nahajajo v /data folderju
## Tehnologije
- Python 3
- XML (ElementTree)
- JSON

## Zagon
V terminalu se premaknemo v mapo projekta /footballXML in zaženemo:

python .\main.py

## Primer uporabe
Uporabnik izbere filter po ekipi in vnese ID 57
(Arsenal FC).
Ali uporabnik izbere filter  po datumu in dobi tekme na določen datum

Program izpiše ustrezne tekme in rezultate
shrani v:
- data/filtrirano.json
- data/filtrirano.xml

## Vir podatkov
https://www.football-data.org/
