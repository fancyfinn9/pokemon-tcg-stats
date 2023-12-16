import http.client, json
import leather
import sys
import time
import os, os.path

firsttime = time.time()

def req(method, url, headers={"X-Api-Key": "your-key-here"}):
    fname = url+".cache"
    fname = fname.replace("/", ",").replace("?", ",")
    if os.path.isfile(fname):
        with open(fname, "r", encoding="utf-8") as f:
            res = f.read()
            f.close()
    else:
        conn = http.client.HTTPSConnection("api.pokemontcg.io")
        conn.request(method, url, headers=headers)
        try:
            res = conn.getresponse().read().decode("utf-8", "ignore")
        except Exception as e:
            print(e)
        conn.close()
        with open(fname, "w", encoding="utf-8") as f:
            f.write(res)
            f.close()
    return res

def printclr(text):
    print(text, end="\r")

cards = []
printclr("Fetching card data from \"api.pokemontcg.io\"... ")
request = json.loads(req("GET", "/v2/cards"))
for card in request["data"]:
    cards.append(card)
total = 1
while request["totalCount"] > total*250:
    request = json.loads(req("GET", "/v2/cards?page="+str(total)))
    for card in request["data"]:
        cards.append(card)
    total += 1
    print(str(total*250)+" of "+str(request["totalCount"]))

print("done")

data = {"Base": [], "Neo": [], "E-Card": [], "EX": [],
        "Diamond & Pearl": [], "Platinum": [], "HeartGold & SoulSilver": [],
        "Black & White": [], "XY": [],
        "Sun & Moon": [], "Sword & Shield": [], "Scarlet & Violet": []}

printclr("Parsing data... ")
for card in cards:
    if not card["set"]["series"] in data:
        #data.update({card["set"]["series"]: []})
        #print("Not found: "+card["set"]["series"])
        pass
    else:  
        if card['supertype'] == 'Pokémon':
            try:
                for attack in card["attacks"]:
                    data[card["set"]["series"]].append(int(attack["damage"]))
            except KeyError:
                pass
            except ValueError:
                pass

#print(data)
i = 0
chartdata = []
for series in data:
    #print(data[series])
    for item in data[series]:
        chartdata.append((i, int(item)))
    i+=1

i = 0
avgdata = []
for series in data:
    #print(data[series])
    avgdata.append((i, sum(data[series])/len(data[series])))
    i+=1
print("done")
printclr("Generating chart... ")

chart = leather.Chart('Average damage of Pokemon cards')
chart.add_dots(chartdata, name="Damage")
chart.add_line(avgdata, name="Average damage")
chart.to_svg('damage.svg')

print("done")
finaltime = str(time.time() - firsttime)
print("Script finished in "+finaltime+" secs")
