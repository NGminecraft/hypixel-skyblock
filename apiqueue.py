"""This class manages the api queue to control request rate"""
import main
import requests

def checkah(self, page=0):
    response = requests.get(f"https://api.hypixel.net/v2/skyblock/auctions?pages={page}")
    print(response.status_code)