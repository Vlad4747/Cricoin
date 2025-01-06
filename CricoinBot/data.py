
import pickle

with open("data.bin","rb") as f:
    data = pickle.load(f)
    users = data["users"]
    black_list = data["black_list"]
    channels = data["channels"]
    posts = data["posts"]