import requests
from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

apiKey = "C5E13936C1AA9C869D67FF6B67C54D36"

class Friend(BaseModel):
    name: str
    image: str

class Player(BaseModel):
    personaname: str
    steamid: str
    avatar: str
    profileurl: str

class Game(BaseModel):
    name: str
    img_icon_url: str
    playtime_forever: str

class GameList(BaseModel):
    games: List[Game]

class FriendsListResponse(BaseModel):
    friends: List[Friend]

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("root.html", {"request": request})

@app.get("/friends/{id}")
async def friends(request: Request, id: str):
    friends_id_json = requests.get(f"https://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={apiKey}&steamid={id}&relationship=friend")

    if friends_id_json.status_code == 200:
        friends_list = friends_id_json.json().get("friendslist", {}).get("friends", [])
        friends_ids = ",".join([friend.get("steamid") for friend in friends_list])

        friends_json = requests.get(f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={apiKey}&steamids={friends_ids}")

        if friends_json.status_code == 200:
            friends_data = friends_json.json().get("response", {}).get("players", [])
            friends_names_img = []
            for friend in friends_data:
                friends_names_img.append(Friend(name=friend.get("personaname"), image=friend.get("avatarfull")))
            return templates.TemplateResponse("friendList.html",{"request": request, "friends": friends_names_img})

    return "No se pudo obtener la lista de amigos"

@app.get("/myself/{id}")
async def myself(request: Request, id: str):
    myself_id = requests.get(f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={apiKey}&steamids={id}")
    if myself_id.status_code == 200:
        players = myself_id.json().get("response", {}).get("players", [])
        myselfObj = None
        for player in players:
            myselfObj = Player(personaname= player.get("personaname"), steamid= player.get("steamid"), avatar= player.get("avatarfull"), profileurl= player.get("profileurl"))
        return templates.TemplateResponse("myself.html",{"request": request, "myself": myselfObj})
    return "nosepudo"

@app.get("/games/{id}")
async def games(request: Request, id: str):
    gamesRequest = requests.get(f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={apiKey}&steamid={id}&include_appinfo=true&format=json")
    if gamesRequest.status_code == 200:
        gamesJson = gamesRequest.json().get("response", {}).get("games", [])
        return templates.TemplateResponse("gamesList.html",{"request": request, "games": gamesJson})
    return "Nosepudo"