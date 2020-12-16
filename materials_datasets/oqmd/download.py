#!/usr/bin/env python3

import time
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

import requests
import pandas as pd

HERE = Path(__file__).parent
OQMD_PKL = str(HERE / "oqmd.pkl")


class OQMD_multi_session:
    def __init__(
        self,
        use_optimade=True,
        limit_per_page=100,
        stop_at=637644,
        start_at=0,
        max_connections=8,
    ):
        if use_optimade:
            self.address = "http://oqmd.org/optimade/structures?"  # for optimade API
        else:
            self.address = "http://oqmd.org/oqmdapi/entry?"  # for official oqmd API (slower, max 100 items, and column names are different)
            if limit_per_page > 100:
                limit_per_page = 100

        self.limit_per_page = limit_per_page  # tested above 100 without speed gain
        self.stop_at = stop_at
        self.start_at = start_at

        self.n_materials = (stop_at - start_at)
        self.n_urls = self.n_materials // self.limit_per_page  # total in OQMD // limit_per_page
        if  self.n_materials % self.limit_per_page != 0:
            self.n_urls += 1

        self.max_connections = min(max_connections, self.n_urls)  # tested above 8 without speed gain
    
    def get_urls(self):
        url = self.address + f"&natom=<100&limit={self.limit_per_page}"
        urls = [
            url + f"&offset={self.limit_per_page*i + self.start_at}"
            for i in range(self.n_urls)
        ]

        print(f"materials {self.start_at} to {self.stop_at} in {len(urls)} queries")
        print(f"  {urls[0]}\n  {urls[1]}\n  ...and so on")
        return urls

    def single_query(self, url):
        return requests.get(url, params=None, verify=True)

    def parrallel_queries(self, urls):
        print(f"using {self.max_connections} workers")
        with ThreadPoolExecutor(max_workers=self.max_connections) as executor:
            future_to_url = {
                executor.submit(self.single_query, url): url for url in urls
            }
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    yield future.result()  # response
                except Exception as exc:
                    print(f"{url} caused exception: {exc}")

    def download_all(self):
        urls = self.get_urls()
        start = time.time()

        response_list = []
        for i, response in enumerate(self.parrallel_queries(urls)):
            response_list.extend(json.loads(response.text)["data"])
            print(
                f"completed request {i+1}/{len(urls)} in {time.time()-start:.2f} s",
                end="\r",
            )
        print("done.")

        return response_list


def fetch(session, url):
    with session.get(url, params=None, verify=True, timeout=1000) as response:
        if response.status_code != 200:
            # print(f"url {url} response: {response.status_code}")
            raise ConnectionError(f"url {url} response: {response.status_code}")
        fetch.counter += 1
        print(f"completed {fetch.counter} in {time.time()-fetch.start:.2f} s", end="\r")
        return response


fetch.counter = 0
fetch.start = time.time()


async def get_data_asynchronous(urls, max_connections=8):
    print(f"using {max_connections} workers")
    fetch.counter = 0
    with ThreadPoolExecutor(max_workers=max_connections) as executor:
        with requests.Session() as session:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor, fetch, *(session, url)
                )  # Allows us to pass in multiple arguments to `fetch`
                for url in urls
            ]

            response_list = []
            for response in await asyncio.gather(*tasks):
                response_list.extend(json.loads(response.text)["data"])

            return response_list


def main():
    asynchronous = True
    
    start = 0
    stop = 637644
    per_parts = 400  # the 8 queries required by a 800 per_parts often failed
    num_parts = (stop-start)//per_parts
    if per_parts%num_parts != 0:
        num_parts += 1

    if start != 0:
        oqmd_df = pd.read_pickle(OQMD_PKL)
        assert len(oqmd_df) == start
    else:
        oqmd_df = pd.DataFrame()

    for part in range(num_parts):
        print(f"\ndownloading part {part} of {num_parts}")
        
        oqmd = OQMD_multi_session(
            start_at=start+part*per_parts,
            stop_at=start+(part+1)*per_parts
        )
        
        max_retries = 6
        num_retries = 0
        success = False
        while not success:
            try:
                timer_start = time.time()
                if asynchronous:
                    urls = oqmd.get_urls()
                    maxc = oqmd.max_connections
                    loop = asyncio.get_event_loop()
                    future = asyncio.ensure_future(get_data_asynchronous(urls, maxc))
                    loop.run_until_complete(future)
                    list_of_dict = future.result()
                else:
                    list_of_dict = oqmd.download_all()
                
                timer_end = time.time()
                print(f"in {timer_end-timer_start}")
                oqmd_df_tmp = oqmd_df.append(list_of_dict, ignore_index=True)
                success = True
                break
            except Exception as exc:
                num_retries += 1
                if num_retries < max_retries:
                    print(f"\nERROR : RETRY {num_retries} for part {part} of {num_parts}")
                else:
                    raise exc
        
        oqmd_df = oqmd_df_tmp
        oqmd_df.to_pickle(OQMD_PKL)


if __name__ == "__main__":
    main()

