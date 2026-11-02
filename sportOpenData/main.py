
from pyaxis import pyaxis
import pandas as pd
import matplotlib.pyplot as plt



PCAXIS_URL = (
    "https://ws.cso.ie/public/api.restful/"
    "PxStat.Data.Cube_API.ReadDataset/QLF65/PX/2013/en"
)

# pridobivanje podatkov, preverjanje njihove pravilnosti
#in pretvorbo v obliko, primerno za analizo
def pridobi_podatke():
    print("\nPridobivanje podatkov iz data.europa.eu ...")

    #branje datotek z različnimi kodiranju znakov
    for encoding in ("utf-8", "cp1252", "ISO-8859-1"):
        try:
            #pyaxis.parse prenese in razčleni PC-Axis datoteko
            px = pyaxis.parse(PCAXIS_URL, encoding=encoding)

            #pridobivanje podatkov in metapodatkov
            #data vsebuje dejanske podatkovne vrstice, ki se shranijo v pandas dataframe
            #copy ustvari samostojno kopijo dataframe, da lahko podatke spreminjamo
            podatki = px["DATA"].copy()
            #metadata vsebuje informacije ki opisujejo podatke (na primer naslove, kazalnike, merske enote)
            metapodatki = px["METADATA"]

            #je true če dataframe nima podatkovnih vrstic oziroma stolpcev
            if podatki.empty:
                raise ValueError("Podatkovna tabela je prazna.")

            #iskanje stolpca DATA
            #podatki.columns vrne imena stolpcev; izraz pregleda imena stolpcev in poišče tistega katerega ime je po pretvorbi v velike črke DATA
            #next vrne prvo najdeno vrednost, če je ni pa NONE
            vrednostni_stolpec = next((c for c in podatki.columns if c.upper() == "DATA"),None)

            if vrednostni_stolpec is None:
                raise ValueError("Stolpec DATA ni bil najden.")

            #zagotovi, da ima stolpec s številskimi vrednostmi vedno ime DATA
            #uporabno ker vse ostale funkcije pričakujejo da bodo statistične vrednosti dostopne s podatki["DATA"]
            podatki = podatki.rename(
                columns = {vrednostni_stolpec: "DATA"}
            )
            #Pretvorba podatkov v številke; matplotlib potrebuje številčne podatke
            #" 14,2" => 14.2
            podatki["DATA"] = pd.to_numeric(
                podatki["DATA"].astype(str)
                .str.strip()
                .str.replace(",", ".", regex=False),
                errors="coerce"
            )

            print("Podatki so uspešno pridobljeni!")
            print(f"Kodiranje: {encoding}")
            print(f"Število vrstic: {len(podatki)}")
            print(f"Stolpci: {podatki.columns.tolist()}")

            return podatki, metapodatki

        except (UnicodeError, UnicodeDecodeError):
            continue
        except Exception as e:
            print(f"Napaka pri pridobivanju podatkov: {e}")
            return None, None




# uporabniku foo omogoča , da izbere eno od vrednosti v določenem stolpcu
#npr sex ima vrednosti male,female in both sexes
def izberi_vrednost(podatki,stolpec):
    vrednosti = podatki[stolpec].dropna().unique().tolist()

    if not vrednosti:
        print("Ni razpoložljivih vrednosti.")
        return None
    print(f"\n Izberi vrednost za {stolpec}: ")

#enumerate omogoča da pri izpisu vsaki vrednosti dodelimo številko
    for i, vrednost in enumerate(vrednosti,1):
        print(f"{i}. {vrednost}")

    try:
        izbira = int(input("Izbira: "))

        #returna izbrano vrednost
        if 1 <= izbira <= len(vrednosti):
            return vrednosti[izbira -1]
    except ValueError:
        pass
    print("Neveljavna izbira")
    return None


#za filtiranje in izbiro osi grafikona
def izberi_stolpec(stolpci):
    if not stolpci:
        return None

    print("\nRazpoložljivi stolpci:")

    for i, stolpec in enumerate(stolpci,1):
        print(f"{i}. {stolpec}")
    try:
        izbira = int(input("Izbira: "))

        if  1<= izbira <= len(stolpci):
            return stolpci[izbira-1]

    except ValueError:
        pass
    print("Neveljavna izbira.")
    return None



def prikazi_podatke(podatki):
    print("\n--- PODATKI ---")

    if podatki.empty:
        print("Ni podatkov za prikaz.")
        return

    print(podatki.to_string(index=False))
    print(f"\nŠtevilo vrstic: {len(podatki)}")

#omogoča izbiro kategorije po kateri želimo omejiti podatke
def filtriraj_podatke(podatki):
    print("\n--- FILTRIRANJE ---")

    #ustvari seznam vseh stolpcev razen DATA
    stolpci = [
        c for c in podatki.columns if c != "DATA"
    ]
    #npr sex
    stolpec = izberi_stolpec(stolpci)

    if stolpec is None:
        return podatki
    #npr female
    vrednost = izberi_vrednost(podatki,stolpec)

    if vrednost is None:
        return podatki

#pandas preveri vsako vrstico in obdrži samo tiste, kjer je vrednost izbranega stolpca enaka uporabnikovi izbiri
    rezultat = podatki[podatki[stolpec] == vrednost].copy()

    print(f"\nNajdenih vrstic: {len(rezultat)}")
    print(rezultat.to_string(index=False))

    return rezultat



def prikazi_graf(podatki):
    print("\n--- GRAFIČNI PRIKAZ ---")

    if podatki.empty:
        print("Ni podatkov za prikaz.")
        return

    df = podatki.dropna(subset=["DATA"]).copy()

#ustvari seznam vseh dimenzij podatkovne zbirke
    dimenzije = [
        c for c in df.columns if c != "DATA"
    ]

#izbira osi x
    print("\nIzberi dimenzijo za os X: ")
    x_stolpec = izberi_stolpec(dimenzije)

    if x_stolpec is None:
        return
    
    print("\nŽeliš primerjati več kategorij?")
    print("0. Ne")
    print("1. Da")

    izbira = input("Izbira: ")

    serija_stolpec = None

    if izbira == "1":
        moznosti = [
            c for c in dimenzije if c !=  x_stolpec
        ]
        print("\nIzberi primerjalno dimenzijo:")
        serija_stolpec = izberi_stolpec(moznosti)

        if serija_stolpec is None:
            return
    elif izbira !="0":
        print("Neveljavna izbira.")
        return
    #poišče vse dimenzije, ki niso bile uoprabljene kot os X ali primerjalna dimenzija
    ostale_dimenzije = [
        c for c in dimenzije if c not in (x_stolpec,serija_stolpec)
    ]
    for stolpec in ostale_dimenzije:
        vrednosti = df[stolpec].dropna().unique()

        if len(vrednosti) == 1:
            continue

        vrednost = izberi_vrednost(df,stolpec)

        if vrednost is None:
            return
        df = df[df[stolpec]== vrednost].copy()

    if df.empty:
        print("Za izbrane kriterije ni podatkov.")
        return

    indeksi = [x_stolpec]
    if serija_stolpec is not None:
        indeksi.append(serija_stolpec)

#duplicated poišče vrstice, ki imajo enake vrednosti v izbranih dimenzijah, 
#any preveri ali obstaja vsaj ena takšna podvojitev
#kontrola preprečuje napačno združevanje statističnih podatkov
    if df.duplicated(subset=indeksi).any():
        print("Za izbrane kategorije obstaja več podatkov.")
        print("Grafikona ni mogoče enolično izdelati")
        return
    if serija_stolpec is not None:
        #pivot preoblikuje podatke iz dolge v široko tabelo
        graf = df.pivot(
            index=x_stolpec,
            columns=serija_stolpec,
            values="DATA"  
        )
    else:
        #če uporabnik ne izbere primerjalne dimenzije uporabimo tole
        #set index nastavi izbrano kategorijo za indeks tabele
        # dvojni oglati oklepaji - rezultat ostane dataframe
        graf = df.set_index(x_stolpec)[["DATA"]]

    #graf empty preveri ali je tabela prazna;
    #graf is na preveri manjkajoče vrednost
    # prvi all preveri ali so vse vrednosti posameznega stolpca manjkajoče
    #drugi pa ali to velja za vse stolpce
    if graf.empty or graf.isna().all().all():
        print("Ni veljavnih vrednosti za grafikon.")
        return

    print("\nIzberi vrsto grafikona:")
    print("1. Stolpčni grafikon")
    print("2. Črtni grafikon")
    print("3. Vodoravni stolpčni grafikon")

    vrsta = input("Izbira: ")
    tipi = {
        "1": "bar",
        "2": "line",
        "3": "barh"
    }
    if vrsta not in tipi:
        print("Neveljavna izbira.")
        return
    
    if vrsta == "2":
        ax = graf.plot(
            kind="line",
            figsize=(11, 6),
            marker="o"
        )
    else:
        ax = graf.plot(
            kind=tipi[vrsta],
            figsize=(11, 6)
        )
    ax.set_title("Sport participation - SPQ65")

    if vrsta == "3":
        ax.set_xlabel("Statistična vrednost")
        ax.set_ylabel(x_stolpec)
    else:
        ax.set_xlabel(x_stolpec)
        ax.set_ylabel("Statistična vrednost")

    if vrsta != "3":
        plt.xticks(rotation=45, ha="right")

    #če primerjamo več kategorij, program prikaže legendo
    #če imamo na primer primerjavo med spoloma legenda pove katera serija predstavlja moške in katera ženske
    #če uporabljamo samo eno serijo, program legendo ostrani ker ni posebej potrebna
    if serija_stolpec is not None:
        plt.legend(title=serija_stolpec)
    else:
        legend = ax.get_legend()
        if legend:
            legend.remove()

    plt.tight_layout()
    plt.show()



def analiziraj_podatke(podatki):
    print("\n--- STATISTIČNA ANALIZA ---")

#funkcija vzame statistične vrednosti iz trenutne, lahko že filtrirane podatkovne tabele in odstrani manjkajoče verdnosti
    vrednosti = podatki["DATA"].dropna()

    if vrednosti.empty:
        print("Ni številskih podatkov.")
        return

#.2f dve decimalni mesti
    print(f"Število vrednosti: {len(vrednosti)}")
    print(f"Minimum: {vrednosti.min():.2f}")
    print(f"Maksimum: {vrednosti.max():.2f}")
    print(f"Mediana: {vrednosti.median():.2f}")
    print(f"Neuteženo povprečje: {vrednosti.mean():.2f}")

    print("\nPozor: statistika velja za trenutni izbor.")
    print("Različnih merskih enot ali skupnih vrednosti")
    print("ne smemo nekritično povprečiti.")



def prikazi_meni():
    print("\n========== ODPRTI PODATKI EU - SPORT ==========")
    print("1. Prikaži vse podatke")
    print("2. Filtriraj podatke")
    print("3. Prikaži grafikon")
    print("4. Statistična analiza")
    print("5. Ponastavi filtre")
    print("6. Prikaži metapodatke")
    print("7. Osveži podatke")
    print("0. Izhod")



def main():
    podatki, metapodatki = pridobi_podatke()

    if podatki is None:
        return

    filtrirani= podatki.copy()

    while True:
        prikazi_meni()

        izbira = input("\nIzberi možnost: ")

        if izbira == "1":
            prikazi_podatke(filtrirani)

        elif izbira == "2":
            filtrirani = filtriraj_podatke(
                filtrirani
            )

        elif izbira == "3":
            prikazi_graf(filtrirani)

        elif izbira == "4":
            analiziraj_podatke(filtrirani)

        elif izbira == "5":
            filtrirani = podatki.copy()
            print("Filtri so ponastavljeni.")

        elif izbira == "6":
            print("\n--- METAPODATKI ---")
            print(metapodatki)

        elif izbira == "7":
            novi_podatki, novi_metapodatki = pridobi_podatke()

            if novi_podatki is not None:
                podatki = novi_podatki
                metapodatki = novi_metapodatki
                filtrirani = podatki.copy()
                print("Podatki so posodobljeni.")

        elif izbira == "0":
            print("Izhod iz programa.")
            break

        else:
            print("Neveljavna izbira.")


if __name__ == "__main__":
    main()
