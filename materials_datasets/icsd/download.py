#!/usr/bin/env python3

import json
from pathlib import Path
import requests
import pandas as pd
import urllib.parse
import xml.etree.ElementTree as ET
import datetime

today = datetime.date.today()
YEAR = today.year

HERE = Path(__file__).parent
ICSD_PKL = str(HERE/"icsd_cifs.pkl")
ICSD_CREDENTIALS_JSON = str(HERE/"icsd_credentials.json")


class ICSD_Session():
    def __init__(self, loginid, password):
        self.address = "https://icsd.fiz-karlsruhe.de/ws"
        self.loginid = loginid
        self.password = password
        self.session = requests.Session()
        self.login_token = self.login()  # sets self.login_token
        self.CIF_LIMIT = 1000

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.logout()
        self.session.close()

    def login(self, verbose=True):
        login_response = self.session.post(
            url=self.address+"/auth/login",
            data={
                'loginid': self.loginid,
                'password': self.password,
            },
            headers={
                'accept': 'text/plain',
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        )

        if login_response.text != "Authentication successful":
            raise ConnectionError(login_response.headers)

        self.login_token = login_response.headers['ICSD-Auth-Token']
        if verbose:
            print(f"logged in ICSD  (token={self.login_token})")
        return self.login_token

    def logout(self, verbose=True):
        logout_response = self.session.get(
            url=self.address+"/auth/logout",
            headers={'ICSD-Auth-Token': self.login_token}
        )

        if logout_response.text != "Logout successful":
            raise ConnectionError(logout_response.text)
        if verbose:
            print(f"logged out ICSD (token={self.login_token})")

    def reconnect(self):
        self.logout(verbose=False)
        self.session.close()
        self.session = requests.Session()
        self.login(verbose=False)

    def raw_query(self, query_string, query_headers, **kwargs):
        query_headers['ICSD-Auth-Token'] = self.login_token
        query_response = self.session.get(
            url=self.address+query_string,
            headers=query_headers,
            **kwargs
        )
        return query_response

    def query_ids(self, search_string):
        query_string = "/search/expert?query="
        query_string += urllib.parse.quote(search_string)
        query_headers = {'accept': 'application/xml'}

        query_results = self.raw_query(query_string, query_headers)
        response_xml_tree = ET.fromstring(query_results.text)
        if response_xml_tree[0].text is not None:
            list_of_ids = response_xml_tree[0].text.split()
        else:
            list_of_ids = []
        return list_of_ids

    def query_cifs(self, list_of_ids):
        query_string = "/cif/multiple?"
        for icsd_id in list_of_ids:
            query_string += f"idnum={icsd_id}&"
        # TODO: windowsclient=true
        query_string += "celltype=standardized&windowsclient=false&filetype=cif"
        query_headers = {'accept': 'application/cif'}

        query_results = self.raw_query(query_string, query_headers)
        separator = f"\n#(C) {YEAR} by FIZ Karlsruhe - Leibniz Institute for Information Infrastructure.  All rights reserved.\n"
        list_of_cifs = query_results.text.split(separator)[1:]  # the first entry is blank
        return list_of_cifs

    def safe_query_cifs(self, list_of_ids):
        queue = list_of_ids
        if len(queue) < self.CIF_LIMIT:
            list_of_cifs = self.query_cifs(queue)
        else:
            n_connect = len(queue)//self.CIF_LIMIT+1
            i = 1
            list_of_cifs = []
            while queue:
                to_query = queue[:self.CIF_LIMIT]
                queue = queue[self.CIF_LIMIT:]
                list_of_cifs.extend(self.query_cifs(to_query))
                self.reconnect()
                print(f"  reconnect {i}/{n_connect}  token:{self.login_token}")
                i += 1

        return list_of_cifs


def download_all(loginid, password, saved_file, min_N=1, max_N=22):
    with ICSD_Session(loginid, password) as icsd:
        id_list = []
        cif_list = []
        for N in range(min_N, max_N+1):
            print(f"materials with {N} elements")
            id_list.extend(icsd.query_ids(f"NUMBEROFELEMENTS: {N}"))
            print(f"received {len(id_list)} ids")
            print("querying cifs")
            cif_list.extend(icsd.safe_query_cifs(id_list))
            print(f"received {len(cif_list)}/{len(id_list)} cif strings")

    icsd_dataframe = pd.DataFrame()
    icsd_dataframe['id'] = id_list
    icsd_dataframe['cif'] = cif_list
    icsd_dataframe.to_pickle(saved_file)


if __name__ == "__main__":
    with open(ICSD_CREDENTIALS_JSON, "r") as f:
        credentials = json.load(f)
    usrname = credentials["loginid"]
    passwrd = credentials["password"]
    download_all(usrname, passwrd, ICSD_PKL)

