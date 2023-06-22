import concurrent.futures
import re
import random
import socket
import time
import requests
import json
import datetime
import pytz
import os

class Message:
    def __init__(self) -> None:
        self.channel = None
        self.userid = None
        self.name = None
        self.displayname = None
        self.message = None
        self.is_subscriber = None
        self.is_mod = None
        self.is_turbo = None
        self.time = None

def ddn():
    dt_now = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))
    return dt_now.strftime("%Y-%m-%d %H:%M:%S")

def Start(streamer):
    try:
        fakeName = random.randint(1000, 99999)
        _socket = socket.socket()
        _socket.connect(("irc.chat.twitch.tv", 6667))
        _socket.send("CAP REQ :twitch.tv/tags twitch.tv/commands\n".encode("utf-8"))
        _socket.send("PASS SCHMOOPIIE\n".encode("utf-8"))
        _socket.send(f"NICK justinfan{fakeName}\n".encode("utf-8"))
        _socket.send(f"USER justinfan{fakeName} 8 * :justinfan{fakeName}\n".encode("utf-8"))

        while True:
            resp = _socket.recv(2048).decode("utf-8")

            if resp.startswith("PING"):
                print(f"PONG: {streamer}")
                _socket.send("PONG :tmi.twitch.tv\n".encode("utf-8"))
            elif len(resp) > 0:
                if "Your host is tmi.twitch.tv" in resp:
                    _socket.send(f"JOIN #{streamer}\n".encode("utf-8"))
                    print(f"join: {streamer}")
                    continue
                if "emote-only" in resp:
                    pattern = "@badge-info=.*;badges=.*;color=.*;display-name=(.*);emote-only=.*;emotes=.*;first-msg=.*;flags=.*;id=.*;mod=(.*);returning-chatter=.*;room-id=.*;subscriber=(.*);tmi-sent-ts=.*;turbo=(.*);user-id=(.*);user-type=.*:.*\!.*@(.*)\.tmi\.twitch\.tv PRIVMSG #(.*) :(.*)"
                else:
                    pattern = "@badge-info=.*;badges=.*;color=.*;display-name=(.*);emotes=.*;first-msg=.*;flags=.*;id=.*;mod=(.*);returning-chatter=.*;room-id=.*;subscriber=(.*);tmi-sent-ts=.*;turbo=(.*);user-id=(.*);user-type=.*:.*\!.*@(.*)\.tmi\.twitch\.tv PRIVMSG #(.*) :(.*)"
                m = re.match(pattern, resp)
                if m:
                    CommentLogger(
                        channel=        m.group(7).strip(),
                        id=             m.group(5).strip(),
                        display_name=   m.group(1).strip(),
                        name=           m.group(6).strip(),
                        message=        m.group(8).strip(),
                        is_subscriber=  m.group(3).strip(),
                        is_mod=         m.group(2).strip(),
                        is_turbo=       m.group(4).strip(),
                        time=           ddn()
                    )
                    
    except:
        print(f"再接続中: {streamer}")
        time.sleep(10)

        Start(streamer)
    finally:
        _socket.close()

streamers = ["suteio", "norochan728", "maru_takahashi", "euriece"]

if __name__ == "__main__":
    for streamer in streamers:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(streamers))
        executor.submit(Start, streamer)
    
LOGGER_API = os.getenv("loggerUrl")
def CommentLogger(channel, id, display_name, name, message, is_subscriber, is_mod, is_turbo, time):
    data = {
        "stearmer": channel,
        "id": id,
        "name": name,
        "display_name": display_name,
        "message" : message,
        "is_subscriber": bool(int(is_subscriber)),
        "is_mod": bool(int(is_mod)),
        "is_turbo": bool(int(is_turbo)),
        "time": time
    }
    r = requests.post(LOGGER_API, data=json.dumps(data))
    return r.status_code