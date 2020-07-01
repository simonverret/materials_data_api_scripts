#%% SIMPLEST REQUEST
import time
import json
import requests

query_specs = {
    'element_set': "O",
    'natom': "<100",
    'limit': "10"
}

url_args = [f"{key}={query_specs[key]}" for key in query_specs]
url = "http://oqmd.org/optimade/structures?" + "&".join(url_args)  # for optimade API
# url = "http://oqmd.org/oqmdapi/entry?" + "&".join(url_args)  # for official oqmd API (slower and max 100 items)

time1 = time.time()
session = requests.Session()
response = session.get(url, params=None, verify=True)
session.close()
time2 = time.time()
data = json.loads(response.text)




#%%
print(url)
print(f'received in {time2-time1:.2f} s')
print(f"next page : {data['links']['next']}")
print(f"number of materials: {len(data['data'])}")
# print(data['resource'])  # this one is empty
print(f"number of materials available: {data['meta']['data_available']}")
print(data['meta']['more_data_available'])  # meta data about the request
# print(data['response_message'])  # simply contais 'OK'



#%% PARALLEL REQUESTS
from concurrent.futures import ThreadPoolExecutor, as_completed

out = []
chunk_size = 1000
n_chunk = 637644//chunk_size
CONNECTIONS = 4
TIMEOUT = 100
urls = [url+f"&offset={chunk_size*i}" for i in range(n_chunk)]

session = requests.Session()

def query(url):
    return session.get(url, params=None, verify=True)

response = query(urls[0])

session.close()

#%%



time1 = time.time()
session = requests.Session()
all_data = []

for url in urls[:4]:
    response = query(url)
    data = json.loads(response.text)
    all_data.extend(data['data'])

session.close()
time2 = time.time()
print(f'received in {time2-time1:.2f} s')
print(f"number of materials: {len(all_data)}")


#%%

all_data =
with ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
    query_generator = (executor.submit(query, url) for url in urls[:4])
    for future in as_completed(query_generator):
        try:
            data = future.result()
        except Exception as exc:
            data = str(type(exc))
        finally:
            out.append(data)

            print(str(len(out)),end="\r")


print(f'Took {time2-time1:.2f} s')
print(pd.Series(out).value_counts())



#%%


from urllib import request 
import json

class PPS: 
    def _init_(self, host='https://localhost:1001'): 
        self.host = host 
        self.token = None 
        self.auth_header = None  
    
    def get_token(self, user, passwd): 
        url = f'  {self.host}/oauth2/token' 
        headers = {'Content-Type': 'application/x-www-form-urlencoded'} 
        data = f'grant_type=password&username={user}&password={passwd}' 
        req = request.Request(url, data.encode(), headers) 
        res = request.urlopen(req) 
        self.token = json.loads(res.readlines()[0].decode())['access_token'] 
        self.auth_header = {'Authorization': f'Bearer {self.token}'}
    
    def get_credential(self, id): 
        url = f'{self.host} /api/v4/rest/credential/  {id} /password' 
        headers = {
            **self.auth_header, 
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }
        req = request.Request(url, None, headers)
        res = request.urlopen(req).readlines()[0].decode().strip('"')
        return res





