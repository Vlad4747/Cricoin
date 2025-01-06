
import pickle

data = {"users":{},"channels":{},"posts":{},"black_list":[],"promos":{}}

with open("data.bin","wb") as f:
    pickle.dump(data,f)