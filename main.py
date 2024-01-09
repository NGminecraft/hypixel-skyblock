import os
import requests
import tkinter
from tkinter import ttk
import threading
import time
# My key: 255b77be-8cd9-404f-904a-f4543f500051


class Main:
    def __init__(self):
        self.root = tkinter.Tk()
        self.frm = ttk.Frame(self.root, padding=10)
        self.frm.grid()
        self.latest_pagect = 1
        self.latest_auctions = None
        self.watched_items_str = tkinter.StringVar()
        self.watched_prices_str = tkinter.StringVar()
        self.watched_total_str = tkinter.StringVar()
        
        self.watched_items_str.set("LOADING")
        self.watched_prices_str.set("LOADING")
        self.watched_total_str.set("LOADING")
        self.startup()
    
    def first_start(self):
        valid_api = False
        for i in range(5):
            test_api = input("Enter your Hypixel API key: ")
            url = f'https://api.hypixel.net/skyblock/profile?key={test_api}&profile=1d4bc4b8ebf349cb94fc6cc2b2b3ee59'
            test_response = requests.get(url=url)
            if test_response.status_code != 200:
                print(f"The provided api key doesn't work, please enter a new one. That was attempt {(i+1)} out of 5.")
            else:
                with open("data.txt", "w") as data:
                    data.write(f"API key: {test_api}")
                self.api_key = test_api
                print("successfully added the api key!")
                print()
                break
            
    def format_items(self, items, several = False):
        if several:
            dict = {}
            for i in items:
                dict[i["name"]]= [i["id"], items.index(i)]
            dict2 = {}
            for key in dict:
                dict2[dict[key][0]] = [key, dict[key][1]]
            return dict, dict2

    def startup(self):
        if os.path.isfile("data.txt"):
            # Fetching API_KEY
            with open("data.txt") as data_file:
                self.info = data_file.readlines()
            self.api_key = self.info[0][9:]
            # Getting, then formatting all the items
            self.watched_items = eval(self.info[1].lstrip("\n"))
            self.item_stats = requests.get("https://api.hypixel.net/v2/resources/skyblock/items").json()["items"]
            self.all_items, self.all_ids = self.format_items(self.item_stats, several=True)
            # Set up ah thread
            ah_thread = threading.Thread(target=self.checkah)
            ah_thread.daemon = True
            ah_thread.start()
            # Set up gui DONE LAST!
            self.setupGUI()
        else:
            self.first_start()
            
    def update_str(self):
        self.watched_items_str.set(self.get_watched_items())
        self.watched_prices_str.set(self.get_watched_prices())
        self.watched_total_str.set(self.get_total_watched())
        
            
    def checkah(self, page=False):
        while True:
            try:
                fullah = []
                print(f"Getting {self.latest_pagect} pages of the Auction House")
                for i in range(self.latest_pagect):
                    result = requests.get(f"https://api.hypixel.net/v2/skyblock/auctions?pages={i+1}").json()
                    fullah.extend(result)
                print(type(fullah))
                print(type(fullah[-1]["auctions"]))
                print(fullah[-1])
                self.latest_auctions = self.format_ah(fullah["auctions"])
                self.latest_pagect = result["totalPages"]
                time.sleep(1)
            except requests.exceptions.ChunkedEncodingError:
                print("Small Connection Error. Skipping")
            
    def format_ah(self, ah_list):
        result_dict = {}
        for i in ah_list:
            if i["item_name"] in result_dict:
                result_dict[i["item_name"]].append(i)
            else:
                result_dict[i["item_name"]] = [i]
        return result_dict


    def get_watched_items(self):
        watched_items = []
        for i in self.watched_items:
            watched_items.append(self.all_ids[i][0])
        return "\n".join(watched_items)
    
    def get_watched_prices(self):
        watched_prices = []
        for i in self.watched_items:
            watched_prices.append(self.get_highest_price_from_id(i))
        return "\n".join(str(v) for v in watched_prices)
            
    def get_highest_price_from_id(self, id):
        try:
            if self.latest_auctions != None:                
                item_info = self.latest_auctions[self.all_ids[id][0]]
                if len(item_info) != 1:
                    highest = 0
                    for j in item_info:
                        if j["highest_bid_amount"] > highest:
                                highest = j["highest_bid_amount"]
                    return highest
                else:
                    return item_info[0]["highest_bid_amount"]
            else:
                return "LOADING"
        except KeyError:
            return "N/A"
    
    def get_total_watched(self):
        result = []
        for i in self.watched_items:
            try:
                if self.latest_auctions != None:
                    ah = self.latest_auctions[self.all_ids[i][0]]
                    lowest = 99999999999999999999999
                    for j in ah:
                        if max(j["highest_bid_amount"], j["starting_bid"]) < lowest:
                            lowest = max(j["highest_bid_amount"], j["starting_bid"])
                    result.append(lowest)
                else:
                    return "LOADING"
            except KeyError:
                result.append("N/A")
        return "\n".join(str(v) for v in result)

    def setupGUI(self):
        ttk.Label(self.frm, text="Hypixel Skyblock", font=("Comic Sans MS", 50), anchor="center").grid(column=0, row=0)
        ttk.Label(self.frm, text=f"Api Key: {self.api_key}", font=("Arial", 10), foreground="gray88", anchor="e").grid(column=1, row=0)
        ttk.Label(self.frm, textvariable=self.watched_items_str, font=("Arial", 25)).grid(column=0, row=1)
        ttk.Label(self.frm, textvariable=self.watched_prices_str, font=("Arial", 25)).grid(column=1, row=1)
        ttk.Label(self.frm, textvariable=self.watched_total_str, font=("Arial", 25)).grid(column=2, row=1)
        running = True
        while running:
            self.update_str()
            self.root.update_idletasks()
            self.root.update()
            time.sleep(0.1)
    

if __name__ == "__main__":
    strt = Main()