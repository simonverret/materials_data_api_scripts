#%% MAIN
import time
import json
from pathlib import Path
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import asyncio


HERE = Path(__file__).parent
OQMD_PKL = str(HERE / "oqmd.pkl")


class OQMD_multi_session:
    def __init__(self, limit=100, cap=637644, max_connections=8, use_optimade=True):
        if use_optimade:
            self.address = "http://oqmd.org/optimade/structures?"  # for optimade API
        else:
            self.address = "http://oqmd.org/oqmdapi/entry?"  # for official oqmd API (slower, max 100 items, and names are different
            if limit>100:
                limit = 100

        self.limit = limit  # tested above 100 without speed gain
        self.cap = cap
        self.n_urls = cap // limit   # total in OQMD // limit
        if cap%limit != 0:
            self.n_urls += 1
        self.max_connections = max_connections  # tested above 8 without speed gain

    def get_urls(self):
        url = self.address + f"&natom=<100&limit={self.limit}"
        urls = [url + f"&offset={self.limit*i}" for i in range(self.n_urls)]
        print(f"downloading {self.cap} materials from OQMD")
        print(f"{len(urls)} queries of {self.limit} entries each:")
        print(f"  {urls[0]}\n  {urls[1]}\n  {urls[2]}\n  ...and so on")
        return urls


    def single_query(self, url):
        return requests.get(url, params=None, verify=True)

    def parrallel_queries(self, urls):
        n_workers = min(self.max_connections, len(urls))
        print(f"using {n_workers} workers")
        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            future_to_url = {executor.submit(self.single_query, url): url for url in urls}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try: yield future.result()  # response
                except Exception as exc: print(f"{url} caused exception: {exc}")

    def download_all(self):
        urls=self.get_urls()
        start = time.time()

        response_list = [] 
        for i, response in enumerate(self.parrallel_queries(urls)):
            response_list.extend(json.loads(response.text)['data'])
            print(f"completed request {i+1}/{len(urls)} in {time.time()-start:.2f} s", end="\r")
        print("done.")
        
        return response_list

def fetch(session, url):
    with session.get(url, params=None, verify=True, timeout=100) as response:
        if response.status_code != 200:
            print(f"url {url} response: {response.status_code}")
            # raise ConnectionError(f"url {url} response: {response.status_code}")
        fetch.counter += 1
        print(f"completed {fetch.counter} in {time.time()-fetch.start:.2f} s", end="\r")
        return response
fetch.counter = 0
fetch.start = time.time()

async def get_data_asynchronous(urls, max_connections=8):
    with ThreadPoolExecutor(max_workers=max_connections) as executor:
        with requests.Session() as session:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, fetch, *(session, url)) # Allows us to pass in multiple arguments to `fetch`
                for url in urls
            ]

            response_list = [] 
            for response in await asyncio.gather(*tasks):
                response_list.extend(json.loads(response.text)['data'])

            return response_list

def main():
    asynchronous = True
    main_start = time.time()
    oqmd = OQMD_multi_session()
    if asynchronous:
        urls = oqmd.get_urls()
        maxc = oqmd.max_connections
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(get_data_asynchronous(urls, maxc))
        loop.run_until_complete(future)
        oqmd_list_of_dict = future.result()
    else:
        oqmd_list_of_dict = oqmd.download_all()
    main_end = time.time()

    print(f"total time {main_end-main_start}")

    oqmd_df = pd.DataFrame(oqmd_list_of_dict)
    oqmd_df.to_pickle(OQMD_PKL)


if __name__ == "__main__":
    main()


#%%

# json.loads(response.text)['data']

# # query_dict = {
# #     "natom": "<100",
# #     "limit": "500"
# # }

# # with OQMD_multi_session() as oqmd:
# #     responses = oqmd.parallel_queries(query_dict, 16)

# # all_data = []
# # for response in responses:
# #     data = json.loads(response.text)
# #     all_data.extend(data["data"])
# # print(f"number of materials: {len(all_data)}")

# #%%
# # responses[0].__dict__
# list_of_dict = json.loads(responses[0].text)['data']  #list of dict of entries
# dataframe = pd.DataFrame(list_of_dict)
# dataframe['chemical_formula']

# # all_data[0]['chemical_formula']

# #%% WHAT THE DATA CONTAINS
# data = json.loads(responses[0].text)

# print(data["links"])
# print()
# print(data["resource"])
# print()
# print(data["meta"])
# print()
# print(data["response_message"])
# print()
# print(data["data"][0].keys())

# print(f"next page : {data['links']['next']}")
# print(f"number of materials: {len(data['data'])}")
# # print(data['resource'])  # this one is empty
# print(f"number of materials available: {data['meta']['data_available']}")
# print(data["meta"]["more_data_available"])  # meta data about the request
# # print(data['response_message'])  # simply contains 'OK'
