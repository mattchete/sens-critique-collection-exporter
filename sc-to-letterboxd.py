"""
This script will export your SensCritique collection to a CSV file,
then you can import it to Letterboxd in your Letterboxd account: https://letterboxd.com/import/
"""

import csv
import json
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

SENSCRITIQUE_ENDPOINT = "https://apollo.senscritique.com/"
SENSCRITIQUE_AUTHORIZATION_KEY = os.environ.get("SENSCRITIQUE_AUTHORIZATION_KEY")
try:
    with open("sc_post_data.json") as json_file:
        SC_POST_BODY = json.load(json_file)
except Exception as e:
    print("sc_post_data.json not found or invalid", e)
    exit()


def get_sc_collection(offset=0, limit=18):
    try:
        payload = SC_POST_BODY
        payload[0]["variables"]["offset"] = offset
        payload[0]["variables"]["limit"] = limit
        response = requests.post(
            url=SENSCRITIQUE_ENDPOINT,
            headers={
                "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Dnt": "1",
                "Origin": "https://www.senscritique.com",
                "Pragma": "no-cache",
                "Referer": "https://www.senscritique.com/MaTT/collection?page=3",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Authorization": SENSCRITIQUE_AUTHORIZATION_KEY,
                "Content-Type": "application/json",
                "Sec-Ch-Ua": '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"macOS"',
                "Accept-Encoding": "gzip",
            },
            data=json.dumps(payload),
        )
        if response.status_code != 200:
            print(
                "Response HTTP Status Code: {status_code}".format(
                    status_code=response.status_code
                )
            )
            print(
                "Response HTTP Response Body: {content}".format(
                    content=response.content
                )
            )
            exit()

        return response.json()[0]
    except requests.exceptions.RequestException:
        print("HTTP Request failed")
        exit()


def create_lbxd_import(sc_collection):
    lbxd_import = []
    for product in sc_collection:
        lbxd_product = {}
        lbxd_product["Title"] = product["title"]
        lbxd_product["Year"] = (
            product["date_release"].split("-")[0]
            if product["date_release"] is not None
            else ""
        )
        if product["rating"]:
            lbxd_product["Rating10"] = product["rating"]
        if product["date_done"]:
            lbxd_product["WatchedDate"] = product["date_done"]

        lbxd_import.append(lbxd_product)
    return lbxd_import


def write_csv(movies, filename):
    lbxd_import = create_lbxd_import(movies)
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["Title", "Year", "Rating10", "WatchedDate"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for product in lbxd_import:
            writer.writerow(product)
    print("CSV file written", filename)


page = 0
page_total = "?"
offset = 0
limit = 18
sc_seen = []
sc_watchlist = []
while True:
    print(f"Page {page + 1} / {page_total}")
    sc_json = get_sc_collection(offset, limit)
    total = sc_json["data"]["user"]["collection"]["total"]
    products = sc_json["data"]["user"]["collection"]["products"]
    if "products" not in sc_json["data"]["user"]["collection"]:
        print("No products")
        break
    if len(products) == 0:
        print("No more products")
        break
    for product in products:
        try:
            if product["category"] != "Film":
                continue
            movie = {
                "title": product["originalTitle"] or product["title"],
                "date_release": product["dateRelease"],
                "rating": product["currentUserInfos"]["rating"],
                "is_wished": product["currentUserInfos"]["isWished"],
                "date_done": product["currentUserInfos"]["dateDone"].split("T")[0]
                if "dateDone" in product["currentUserInfos"]
                and product["currentUserInfos"]["dateDone"] is not None
                else None,
            }
            if product["currentUserInfos"]["rating"]:
                sc_seen.append(movie)
            else:
                sc_watchlist.append(movie)
        except Exception as e:
            print("error parsing product", product)
            print(e)

    if offset + limit >= total:
        break

    offset += limit
    page += 1
    page_total = round(total / limit)
    time.sleep(1)


write_csv(sc_seen, "sc_to_lbxd_seen.csv")
write_csv(sc_watchlist, "sc_to_lbxd_watchlist.csv")

print("That's all folks!")
