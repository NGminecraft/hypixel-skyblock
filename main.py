import os
import requests
import tkinter
from tkinter import ttk
import threading
import time
# My key: 255b77be-8cd9-404f-904a-f4543f500051


class Main:
    def __init__(self):
        self.latest_pagect = 1
        self.checkah()
    
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
            
    def checkah(self, page=False):
        fullah = []
        for i in range(self.latest_pagect):
            result = requests.get(f"https://api.hypixel.net/v2/skyblock/auctions?pages={i+1}").json()
            fullah.append(i for i in result)
        print(fullah)
        print(len(fullah))
        self.latest_auctions = self.format_ah(result["auctions"])
        self.latest_pagect = result["totalPages"]
        time.sleep(1)
        
    def format_ah(self, ah_list):
        result_dict = {}
        for i in ah_list:
            print(i["item_name"])
            if i["item_name"] in result_dict:
                result_dict[i["item_name"]].append(i)
            else:
                result_dict[i["item_name"]] = [i]
        return result_dict


    def get_watched_items(self):
        watched_items = []
        for i in self.watched_items:
            watched_items.append(self.all_ids[i][0])
        print(type(watched_items))
        return "\n".join(watched_items)
    
    def get_watched_prices(self):
        watched_prices = []
        for i in self.watched_items:
            watched_prices.append(self.get_highest_price_from_id(i))
        return "\n".join(watched_prices)
            
    def get_highest_price_from_id(self, id):
        try:
            item_info = self.latest_auctions[id]
            if len(item_info) != 1:
                highest = 0
                for j in item_info:
                    if j["highest_bid_amount"] > highest:
                            highest = j["highest_bid_amount"]
                return highest
            else:
                return item_info[0]["highest_bid_amount"]
        except KeyError:
            print(f"Unable to find item: {id} in ah")
            return "N/A"
        

    def setupGUI(self):
        root = tkinter.Tk()
        frm = ttk.Frame(root, padding=10)
        frm.grid()
        ttk.Label(frm, text="Hypixel Skyblock", font=("Comic Sans MS", 50), anchor="center").grid(column=0, row=0)
        ttk.Label(frm, text=f"Api Key: {self.api_key}", font=("Arial", 10), foreground="gray88", anchor="e").grid(column=1, row=0)
        ttk.Label(frm, text=self.get_watched_items(), font=("Arial", 25)).grid(column=0, row=1)
        ttk.Label(frm, text=self.get_watched_prices(), font=("Arial", 25)).grid(column=1, row=1)
        root.mainloop()

    def main(self):
        self.startup()
    

if __name__ == "__main__":
    strt = Main()
    strt.main()