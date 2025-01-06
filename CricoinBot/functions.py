
from data import *
import pickle
from prettytable import PrettyTable
from settings import *
def dict_to_table(dictionary):
    table = PrettyTable(max_table_width=48)
    table.field_names = dictionary.keys()
    table.add_row(dictionary.values())
    return table
def list_to_table(lst):
    text = ''
    for item in lst:
        text += str(item)+"\n"
    return text
def save():
    global data
    with open("data.bin","wb") as f:
        pickle.dump(data,f)
def add_user(id,ref=None):
    if ref != None and int(ref) > 1243 and int(ref) in users:
        users[id] = {"id":id,"balance":0,"alltime_subs":0,"find_count":0,"referals":[],"alltime_get_subs":0,"ref_father":ref,"level":1,"p1":None}
        save()
        return True
    else:
        users[id] = {"id": id, "balance": 0, "alltime_subs": 0, "find_count": 0, "referals": [], "alltime_get_subs": 0,"ref_father": None, "level": 1,"p1":None}
        save()
        return False

def user_banned(id):
    save()
    if id in black_list:
        return True
    else:
        return False
def user_balance(id):
    return users[id]["balance"]
    save()
def user_level(id):
    save()
    return users[id]["level"]
def alltime_subs(id):
    return users[id]["alltime_subs"]
def alltime_get_subs(id):
    return users[id]["alltime_get_subs"]
def fine_count(id):
    try:
        return users[id]["fine_count"]
    except:
        return 0
def referals(id):
    save()
    return users[id]["referals"]
def channel_for_subscribe(id):
    channels_list = []
    for channel in channels.items():
        channel_id = channel[0]
        channel = channel[1]
        if not id in channel["subscriptions"]:
            channels_list.append(channel_id)
    return channels_list
def posts_for_view(id):
    posts_list = []
    for post in posts.items():
        post_id = post[0]
        post = post[1]
        if not id in post["views"]:
            posts_list.append(post)
    return posts_list
def find_channel(writer):
    find_channel = None
    for channel in channels.items():
        id = channel[0]
        channel = channel[1]
        if channel["writer"] == writer:
            find_channel = channel
            break
    if find_channel != None:
        return find_channel["id"]
    else:
        return 0
def get_writer(id):
    return channels[id]["writer"]
def add_post(id=None,writer=None,count=None):
    if count==None:
        posts[str(id)+'_'+str(writer)] = {"id":id,"views":[],'writer':writer,"count":0}
        save()
        return 1
    else:
        try:
            posts[str(id) + '_' + str(writer)] = {"id": id, "views": [], 'writer': writer, "count": count}
            return posts[str(id) + '_' + str(writer)]
        except:
            pass

def save_channel(id=None,writer=None,username=None,subs_count=None):
    print(str(type(subs_count)))
    if subs_count==None:
        if not id in channels:
            channels[id] = {"id":id,"subscriptions":[],'writer':writer,"subs_count":0,"username":username}
            save()
            return 1
        else:
            save()
            return 0
    else:
        try:
            i = subs_count+1
            find_channel = None
            for channel in channels.items():
                id = channel[0]
                channel = channel[1]
                if channel["writer"] == writer:
                    find_channel = channel
                    break
            if find_channel != None:
                channels[find_channel["id"]] = {"id": find_channel["id"], "subscriptions":find_channel["subscriptions"], 'writer': writer,"username":find_channel["username"], "subs_count": subs_count}
                save()
                return channels[find_channel["id"]]
            else:
                return 0
        except:
            pass