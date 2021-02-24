import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import traceback
import time
import dateutil.parser
import xml.etree.cElementTree as ET


# ŠTOPARICA
start = time.time()

# izklopi opozorila glede nevarne povezave
requests.packages.urllib3.disable_warnings()
# odprem sejo requests
s = requests.session()

razpon_od = int(input("Razpon od: "))
razpon_do = int(input("Razpon od: "))

razpon = "od" + str(razpon_od) + "do" + str(razpon_do)

# PREBEREM mbs za parsanje
#df_csv_ms = pd.read_csv("vse_mbs.csv", header=0, sep=";")
df = pd.read_csv("xml/od2007-01-01do2020-12-20_vsa_leta.csv", header=0, sep=";", index_col=0)
df = df.set_index("FBIH_id")
df = df[['MBS', 'Naziv', 'Naziv_kratki', 'Naslov', 'Datum', 'Link']]

# odprem file za morebitne napake pri deležih ali generalne napake
error_csv = open("xml/" + razpon + "error.csv", "w", encoding="utf-8")

url = "https://bizreg.pravosudje.ba/pls/apex/f?p=183:20:::NO::P20_SEKCIJA_TIP,P20_POMOC:PRETRAGA,FALSE"
r= s.get(url, verify=False)
r.encoding = "utf-8"
soup = BeautifulSoup(r.text, "html.parser")

sifra = str(soup.find(id="pInstance")['value'])
#print(sifra)

counter = 0

root = ET.Element('Subjekti')

for i in df.iloc[razpon_od:razpon_do].itertuples():
    counter = counter + 1
    zap_st = str(counter)
    mat_st = str(i[1])
    fbih_id = str(i[0])
    datum = str(i[5])

    print("Obdelujem zap.st.: " + zap_st + "\n")

    regex = r"183:13:(\d+)"
    osnovni_link = i[6]
    subst = "183:13:" + sifra
    novi_link = re.sub(regex, subst, osnovni_link, 0, re.MULTILINE)

    try:
        #mat_st = "65-01-0542-10"
        #mat_st = "1-4502-00"
        #mat_st = "1-1187-00 int. 1357"


        subjekt = ET.SubElement(root, "Subjekt")
        subjekt.attrib['MBS'] = mat_st
        subjekt.attrib['FBIH_ID'] = fbih_id
        subjekt.attrib['datum'] = datum

        osnovni_podatki = ET.SubElement(subjekt, "Osnovni_podatki")
        ustanovitelji = ET.SubElement(subjekt, "Ustanovitelji")
        zastopniki = ET.SubElement(subjekt, "Zastopniki")
        kapital_skupno = ET.SubElement(subjekt, "Kapital")
        kapital_podrobno = ET.SubElement(subjekt, "Kapital_podrobno")
        dejavnosti = ET.SubElement(subjekt, "Dejavnosti")
        podruznice = ET.SubElement(subjekt, "Podruznice")
        zunanja_trgovina = ET.SubElement(subjekt, "Zunanja_trgovina")
        opombe = ET.SubElement(subjekt, "Opombe")


        #OSNOVNI PODATKI

        url_4 = "https://bizreg.pravosudje.ba/pls/apex/" + novi_link

        r_4= s.get(url_4, verify=False)
        r_4.encoding = "utf-8"
        soup_4 = BeautifulSoup(r_4.text, "html.parser")

        osnovni_podatki_raw = soup_4.find_all(class_="vertical2")[1].find_all("td")
        # osnovni_podatki_ = []
        #
        # #loopam samo skozi sode elemente
        # for i in range(1, len(osnovni_podatki_raw),2):
        #     osnovni_podatki.append(osnovni_podatki_raw[i].text.replace("\xa0", ""))
        #
        # print(osnovni_podatki)

        ET.SubElement(osnovni_podatki, "MBS").text = osnovni_podatki_raw[1].text
        ET.SubElement(osnovni_podatki, "Naziv").text = osnovni_podatki_raw[3].text
        ET.SubElement(osnovni_podatki, "Naziv_kratki").text = osnovni_podatki_raw[5].text
        ET.SubElement(osnovni_podatki, "Naslov").text = osnovni_podatki_raw[7].text
        ET.SubElement(osnovni_podatki, "Oblika").text = osnovni_podatki_raw[9].text
        ET.SubElement(osnovni_podatki, "Status").text = osnovni_podatki_raw[11].text
        ET.SubElement(osnovni_podatki, "JIB").text = osnovni_podatki_raw[13].text.replace("\xa0", "")
        ET.SubElement(osnovni_podatki, "Carinski_broj").text = osnovni_podatki_raw[15].text.replace("\xa0", "")


        #USTANOVITELJI
        url_5 = "https://bizreg.pravosudje.ba/pls/apex/f?p=183:21:" + sifra + "::NO::"

        r_5= s.get(url_5, verify=False)
        r_5.encoding = "utf-8"
        soup_5 = BeautifulSoup(r_5.text, "html.parser")

        # ustanovitelji = []

        fizicne_osebe = soup_5.find_all(text=re.compile("Ime osnivača"))

        for oseba in fizicne_osebe:
            oseba_podatki = oseba.find_parent("table").find_all("td")
            # ustanovitelj = []

            f_oseba = ET.SubElement(ustanovitelji, "Fizicna_oseba")
            ET.SubElement(f_oseba, "Ime").text = oseba_podatki[1].text
            ET.SubElement(f_oseba, "Kapital_dogovorjen").text = oseba_podatki[3].text.replace(",","")
            ET.SubElement(f_oseba, "Kapital_vplacan").text = oseba_podatki[5].text.replace(",","")
            ET.SubElement(f_oseba, "Delnice_stevilo").text = oseba_podatki[7].text.replace(" - ","")


            # for i in range(1,len(oseba_podatki),2):
            #     ustanovitelj.append((oseba_podatki[i].text.replace("\xa0", "")))
            # ustanovitelji.append(ustanovitelj)

        pravne_osebe = soup_5.find_all(text=re.compile("Osnovni podaci"))

        for oseba in pravne_osebe:
            oseba_podatki = oseba.find_parent("table").find_all("td")
            # ustanovitelj = []

            p_oseba = ET.SubElement(ustanovitelji, "Pravna_oseba")
            ET.SubElement(p_oseba, "Naziv").text = oseba_podatki[1].text
            ET.SubElement(p_oseba, "Reg_st_MBS").text = oseba_podatki[3].text
            #
            # for i in range(1,len(oseba_podatki),2):
            #     ustanovitelj.append((oseba_podatki[i].text.replace("\xa0", "")))
            # ustanovitelji.append(ustanovitelj)


        # print(ustanovitelji)


        #UPRAVA
        url_6 = "https://bizreg.pravosudje.ba/pls/apex/f?p=183:22:" + sifra + "::NO::"

        r_6= s.get(url_6, verify=False)
        r_6.encoding = "utf-8"
        soup_6 = BeautifulSoup(r_6.text, "html.parser")

        # zastopniki = []

        uprava = soup_6.find_all(text=re.compile("Položaj"))

        for oseba in uprava:
            oseba_podatki = oseba.find_parent("table").find_all("td")

            zastopnik = ET.SubElement(zastopniki, "Zastopnik")
            ET.SubElement(zastopnik, "Ime").text = oseba_podatki[1].text
            ET.SubElement(zastopnik, "Pooblastila").text = oseba_podatki[3].text
            ET.SubElement(zastopnik, "Polozaj").text = oseba_podatki[5].text
        #
        #     zastopnik = []
        #     for i in range(1,len(oseba_podatki),2):
        #         zastopnik.append((oseba_podatki[i].text.replace("\xa0", "")))
        #     zastopniki.append(zastopnik)
        #
        # print(zastopniki)


        #KAPITAL
        url_7 = "https://bizreg.pravosudje.ba/pls/apex/f?p=183:25:" + sifra + "::NO::"

        r_7= s.get(url_7, verify=False)
        r_7.encoding = "utf-8"
        soup_7 = BeautifulSoup(r_7.text, "html.parser")


        # kapital_skupno = []

        kapital_raw_s = soup_7.find_all(text=re.compile("u stvarima]"))

        for postavka in kapital_raw_s:
            postavka_podatki = postavka.find_parent("table").find_all("td")

            ET.SubElement(kapital_skupno, "Skupno").text = postavka_podatki[1].text.replace(",","")
            ET.SubElement(kapital_skupno, "Denar").text = postavka_podatki[3].text.replace(",","")
            ET.SubElement(kapital_skupno, "Pravice").text = postavka_podatki[5].text.replace(",","")
            ET.SubElement(kapital_skupno, "Stvari").text = postavka_podatki[7].text.replace(",","")
        #
        # for i in range(1,len(kapital_s),2):
        #     kapital_skupno.append((kapital_s[i].text.replace("\xa0", "")))
        #
        # print(kapital_skupno)
        #
        # #
        #
        # vlozki = []

        kapital_raw_p = soup_7.find_all(text=re.compile("u stvarima ]"))

        for oseba in kapital_raw_p:
            oseba_podatki = oseba.find_parent("table").find_all("td")


            druzbenik = ET.SubElement(kapital_podrobno, "Ustanovitelj")
            ET.SubElement(druzbenik, "Ime_Naziv").text = oseba_podatki[1].text
            ET.SubElement(druzbenik, "Skupno").text = oseba_podatki[3].text.replace(",","")
            ET.SubElement(druzbenik, "Denar").text = oseba_podatki[5].text.replace(",","").replace(" - ","")
            ET.SubElement(druzbenik, "Pravice").text = oseba_podatki[7].text.replace(",","").replace(" - ","")
            ET.SubElement(druzbenik, "Stvari").text = oseba_podatki[9].text.replace(",","").replace(" - ","")
        #
        #     vlozek = []
        #     for i in range(1,len(oseba_podatki),2):
        #         vlozek.append((oseba_podatki[i].text.replace("\xa0", "")))
        #     vlozki.append(vlozek)
        #
        # print(vlozki)


        #DEJAVNOST
        url_8 = "https://bizreg.pravosudje.ba/pls/apex/f?p=183:28:" + sifra + "::NO::"

        r_8= s.get(url_8, verify=False)
        r_8.encoding = "utf-8"
        soup_8 = BeautifulSoup(r_8.text, "html.parser")
        #
        # dejavnosti = []

        dejavnosti_raw = soup_8.find_all(text=re.compile("Naziv djelatnosti"))

        for postavka in dejavnosti_raw:
            postavka_podatki = postavka.find_parent("table").find_all("td")

            dejavnost = ET.SubElement(dejavnosti, "Dejavnost")
            ET.SubElement(dejavnost, "Naziv").text = postavka_podatki[1].text
            ET.SubElement(dejavnost, "Sifra").text = postavka_podatki[3].text
        #
        #     dejavnost = []
        #     for i in range(1,len(postavka_podatki),2):
        #         dejavnost.append((postavka_podatki[i].text.replace("\xa0", "")))
        #     dejavnosti.append(dejavnost)
        #
        # print(dejavnosti)


        #PODRUZNICE
        url_9 = "https://bizreg.pravosudje.ba/pls/apex/f?p=183:31:" + sifra + "::NO::"

        r_9= s.get(url_9, verify=False)
        r_9.encoding = "utf-8"
        soup_9 = BeautifulSoup(r_9.text, "html.parser")
        #
        # podruznice = []

        podruznice_raw = soup_9.find_all(text=re.compile("SJEDISTE"))

        for postavka in podruznice_raw:
            postavka_podatki = postavka.find_parent("table").find_all("td")

            podruznica = ET.SubElement(podruznice, "Podruznica")
            ET.SubElement(podruznica, "Naziv").text = postavka_podatki[1].text
            ET.SubElement(podruznica, "Naslov").text = postavka_podatki[3].text
            ET.SubElement(podruznica, "Zastopnik_funkcija").text = postavka_podatki[5].text
            ET.SubElement(podruznica, "Zastopnik_ime").text = postavka_podatki[7].text
            ET.SubElement(podruznica, "Sedez").text = postavka_podatki[9].text
        #
        #     podruznica = []
        #     for i in range(1,len(postavka_podatki),2):
        #         podruznica.append(postavka_podatki[i].text.replace("\xa0", ""))
        #
        #     podruznice.append(podruznica)
        #
        # print(podruznice)


        #ZUNANJA TRGOVINA
        url_10 = "https://bizreg.pravosudje.ba/pls/apex/f?p=183:35:" + sifra + "::NO::"

        r_10= s.get(url_10, verify=False)
        r_10.encoding = "utf-8"
        soup_10 = BeautifulSoup(r_10.text, "html.parser")
        #
        #
        # zunanja_trgovina = []

        trgovina_raw = soup_10.find(text=re.compile("Carinski broj"))

        trgovina_raw = trgovina_raw.find_parent("table").find_all("td")


        ET.SubElement(zunanja_trgovina, "Carinski_broj").text = trgovina_raw[1].text.replace("\xa0", "")
        ET.SubElement(zunanja_trgovina, "Pooblastilo_zunanja_trgovina").text = trgovina_raw[3].text
        #
        # for i in range(1,len(trgovina_raw),2):
        #     zunanja_trgovina.append((trgovina_raw[i].text.replace("\xa0", "")))
        #
        # print(zunanja_trgovina)


        #OPOMBE
        url_11 = "https://bizreg.pravosudje.ba/pls/apex/f?p=183:37:" + sifra + "::NO::"

        r_11= s.get(url_11, verify=False)
        r_11.encoding = "utf-8"
        soup_11 = BeautifulSoup(r_11.text, "html.parser")
        #
        # opombe = []

        opombe_raw = soup_11.find_all(text=re.compile("Sadržaj"))

        for postavka in opombe_raw:
            postavka_podatki = postavka.find_parent("table").find_all("td")

            opomba = ET.SubElement(opombe, "Opomba")
            datum_opombe = dateutil.parser.parse(postavka_podatki[1].text)
            ET.SubElement(opomba, "Datum").text = datum_opombe.strftime("%Y-%m-%d")
            ET.SubElement(opomba, "Vsebina").text = postavka_podatki[3].text
        #
        #
        #     opomba = []
        #     for i in range(1,len(postavka_podatki),2):
        #         opomba.append(postavka_podatki[i].text.replace("\xa0", ""))
        #
        #     opombe.append(opomba)
        #
        # print(opombe)


    except Exception as e:
            print(e)
            a = traceback.format_exc()
            print(a)

            error_csv.write("Generalna napaka na poziciji: " + zap_st + ": " + mat_st + "\n")

            pass



error_csv.close()

tree = ET.ElementTree(root)
tree.write("xml/" + razpon + '.xml', encoding='utf-8', xml_declaration=True)

# USTAVIM ŠTOPARICO
stop = time.time()

razlika = stop - start

print("\n")
print("Potreben cas!")
print(razlika)
