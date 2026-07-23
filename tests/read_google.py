from bs4 import BeautifulSoup
import requests


def read_table_from_google_doc(url):
    response = requests.get(url=url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find('table')

def prepare_table_data(table_data):
    data = dict()
    for idx, element in enumerate(table_data):
        if idx == 0:
            continue
        cells = [td.get_text(strip=True) for td in element.find_all("td")]
        data[(cells[0], cells[2])] = cells[1]
    return data

def create_empty_array(table_data):
    max_row = max(int(item[0]) for item in table_data)
    max_col = max(int(item[1]) for item in table_data)
    array = [[' ' for _ in range(max_row+1)] for _ in range(max_col+1)]
    return array

def fill_up_array(table_data, empty_array):
    for k, v in table_data.items():
        empty_array[int(k[1])][int(k[0])] = v


url = "https://docs.google.com/document/d/e/2PACX-1vTMOmshQe8YvaRXi6gEPKKlsC6UpFJSMAk4mQjLm_u1gmHdVVTaeh7nBNFBRlui0sTZ-snGwZM4DBCT/pub"
url2 = "https://docs.google.com/document/d/e/2PACX-1vSZ9d7OCd4QMsjJi2VFQmPYLebG2sGqI879_bSPugwOo_fgRcZLAFyfajPWU91UDiLg-RxRD41lVYRA/pub"
table_data = read_table_from_google_doc(url2)
prepared_data = prepare_table_data(table_data)
empty_array = create_empty_array(prepared_data)

fill_up_array(prepared_data, empty_array)
for row in reversed(empty_array):
    print("".join(row))
