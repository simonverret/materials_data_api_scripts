#%% MAIN
import time
import json
from pathlib import Path
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd


HERE = Path(__file__).parent
OQMD_PKL = str(HERE / "oqmd.pkl")


class OQMD_multi_session:
    def __init__(self, limit=500, cap=637644, max_connections=8):
        self.address = "http://oqmd.org/optimade/structures?"  # for optimade API
        # self.address = "http://oqmd.org/oqmdapi/entry?"  # for official oqmd API (slower and max 100 items)
        # self.session = requests.Session()  ## turns out that parallel connections require parrallel sessions

        self.limit = limit  # tested above 100 without speed gain
        self.cap = cap
        self.n_urls = cap // limit   # total in OQMD // limit
        if cap%limit != 0:
            self.n_urls += 1
        self.max_connections = max_connections  # tested above 8 without speed gain

    def url_from_dict(self, d):
        ''' produces string "ke1=val1&key2=val2&..." from dict {'key1':"val1",...}'''
        url = self.address
        url += "&".join([f"{key}={d[key]}" for key in d])
        return url

    def get_urls(self, query_dict, n_queries=1):
        chunk_size = int(query_dict['limit'])
        url = self.url_from_dict(query_dict)
        return [url + f"&offset={chunk_size*i}" for i in range(n_queries)]

    def single_query(self, url):
        return requests.get(url, params=None, verify=True)

    def parrallel_queries(self, urls):
        n_workers = min(self.max_connections, len(urls))
        print(f"using {n_workers} workers")
        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            future_to_url = {executor.submit(self.single_query, url): url for url in urls}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    yield future.result()
                except Exception as exc:
                    print(f"{url} generated an exception: {exc}")


    def download_all(self):
        urls=self.get_urls({'natom':"<100",'limit':str(self.limit)}, self.n_urls)

        print(f"downloading {self.cap} materials from OQMD")
        print(f"{len(urls)} queries of {self.limit} entries each:")
        print(f"  {urls[0]}\n  {urls[1]}\n  {urls[2]}\n  ...and so on")
        start = time.time()
        
        response_list = [] 
        for i, response in enumerate(self.parrallel_queries(urls)):
            response_list.extend(json.loads(response.text)['data'])
            print(f"completed request {i+1}/{len(urls)} in {time.time()-start:.2f} s", end="\r")
        print("done.")
        return response_list


def main():
    oqmd = OQMD_multi_session()
    oqdm_list_of_dict = oqmd.download_all()
    oqmd_df = pd.DataFrame(oqdm_list_of_dict)
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
