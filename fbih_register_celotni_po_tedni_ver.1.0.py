import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import traceback
import time
import dateutil.parser
import xml.etree.cElementTree as ET
import datetime
import re

# ŠTOPARICA
start = time.time()


start_date = datetime.date(2007, 1, 1)

today = datetime.date.today()
idx = (today.weekday() + 1)
end_date = today - datetime.timedelta(idx)

delta = datetime.timedelta(days=7)



lista_zadetkov = []

razpon = "od" + str(start_date) + "do" + str(end_date)

# izklopi opozorila glede nevarne povezave
requests.packages.urllib3.disable_warnings()
# odprem sejo requests
s = requests.session()

# pridobim maticne
url = "https://bizreg.pravosudje.ba/pls/apex/f?p=183:3:::NO:RP,3:P3_FIRSTTIME,P3_VISIBLE:TRUE,FALSE"
r = s.get(url, verify=False)
r.encoding = "utf-8"
soup = BeautifulSoup(r.text, "html.parser")
sifra = str(soup.find(id="pInstance")['value'])

url = "https://bizreg.pravosudje.ba/pls/apex/f?p=183:3:" + sifra + "::NO:RP,3:P3_FIRSTTIME,P3_VISIBLE:TRUE,FALSE"
r = s.get(url, verify=False)
r.encoding = "utf-8"
soup = BeautifulSoup(r.text, "html.parser")
sifra = str(soup.find(id="pInstance")['value'])

payload = {'p_request': 'APPLICATION_PROCESS=populateShuttleOps', 'p_instance': sifra, 'p_flow_id': '183',
           'p_flow_step_id': '0', 'x01': '', 'x02': '', 'x03': '-1', 'x04': '-1'}
url_1 = "https://bizreg.pravosudje.ba/pls/apex/wwv_flow.show"
r_1 = s.post(url_1, data=payload, verify=False)
r_1.encoding = "utf-8"
# soup_1 = BeautifulSoup(r_5.text, "html.parser")


while start_date <= end_date:

    last_mon = start_date
    last_sun = start_date + datetime.timedelta(days=6)
    last_mon = last_mon.strftime('%d/%m/%Y')
    last_sun = last_sun.strftime('%d/%m/%Y')
    print(f"{last_mon} - {last_sun}")

    payload = {'p_request': 'APPLICATION_PROCESS=NAPREDNA_PRETRAGA_PARAMS', 'p_instance': sifra, 'p_flow_id': '183', 'p_flow_step_id': '0', 'x01': '', 'x02': '-1', 'x03': '-1', 'x04': '', 'x05': last_mon, 'x06': last_sun, 'x07': '-1', 'x08': '-1', 'x09': ''}
    url_2 = "https://bizreg.pravosudje.ba/pls/apex/wwv_flow.show"
    r_2 = s.post(url_2, data=payload, verify=False)
    r_2.encoding = "utf-8"
    # soup_2 = BeautifulSoup(r_2.text, "html.parser")


    payload = {'p_request': 'APPLICATION_PROCESS=NAPREDNA_PRETRAGA_PARAMS_2', 'p_instance': sifra, 'p_flow_id': '183', 'p_flow_step_id': '0', 'x01': '-1', 'x02': '-1', 'x03': '-1'}
    url_3 = "https://bizreg.pravosudje.ba/pls/apex/wwv_flow.show"
    r_3 = s.post(url_3, data=payload, verify=False)
    r_3.encoding = "utf-8"
    # soup_3 = BeautifulSoup(r_3.text, "html.parser")


    sifra_2 = '183:3:' + sifra + ':FLOW_PPR_OUTPUT_R13525572996245770_pg_R_13525572996245770:NO'
    payload = {'p': sifra_2, 'pg_max_rows': '500', 'pg_min_row': '1', 'pg_rows_fetched': 'undefined'}
    url_4 = "https://bizreg.pravosudje.ba/pls/apex/f"
    r_4 = s.post(url_4, data=payload, verify=False)
    r_4.encoding = "utf-8"
    soup_4 = BeautifulSoup(r_4.text, "html.parser")
    ni_zadetka = soup_4.find(text=re.compile("Nema podataka."))

    regex = re.compile('.*row_mouse_over.*')
    tr_zadetki = soup_4.find_all("tr", {"onmouseover": regex})

    for tr in tr_zadetki:
        lista_pos_zadetek = []
        td_zadetki = tr.find_all("td")
        for td in td_zadetki:
            if td.a:
                text = td.text.strip(' \t\n\r')
                text = text.replace('\n','').replace('\r','')
                lista_pos_zadetek.append(text)
                href = td.a["href"].strip(' \t\n\r')
                href = href.replace('\n','').replace('\r','')
                lista_pos_zadetek.append(href)
                url = td.a["href"]
                fbih_id = re.search("P13_NAZIV:(\d+)%", url)
                if fbih_id:
                    fbih_id =  fbih_id.group(1)
                    fbih_id = fbih_id.strip(' \t\n\r')
                    fbih_id = fbih_id.replace('\n','').replace('\r','')
                lista_pos_zadetek.append(fbih_id)
            else:
                text = td.text.strip(' \t\n\r')
                text = text.replace('\n', '').replace('\r','')
                lista_pos_zadetek.append(text)

        lista_pos_zadetek[6] = datetime.datetime.strptime(lista_pos_zadetek[6], '%Y-%m-%d').date()
        lista_zadetkov.append(lista_pos_zadetek)


    start_date += delta

df = pd.DataFrame.from_records(lista_zadetkov, columns = ['MBS', 'Naziv', 'Link', "FBIH_id", 'Naziv_kratki', 'Naslov', 'Datum'])
df = df[['MBS', 'Naziv', 'Naziv_kratki', 'Naslov', 'Datum', "FBIH_id", 'Link']]

df.to_csv("xml/" + razpon + "_vsa_leta.csv", sep=';', encoding='utf-8')


# USTAVIM ŠTOPARICO
stop = time.time()

razlika = stop - start

print("\n")
print("Potreben cas!")
print(razlika)
