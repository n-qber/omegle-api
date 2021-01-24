from time import asctime, sleep
from threading import Thread
from typing import List
from random import choice
import requests
import sys


def thread(func):
    def wrapper(*args, **kwargs):
        t = Thread(target=func, args=(*args,), kwargs=kwargs)
        t.start()
        return t

    return wrapper


class OmegleBot:
    def __init__(self, common_likes: List[str] = [],
                 server: str = "",
                 rand_id: str = "",
                 lang: str = "en",
                 requires_common_likes: bool = False,
                 common_likes_timeout: int = 10,
                 debug: bool = False):

        self._BASE_URL = server or OmegleBot._get_a_server()
        self.COMMON_LIKES_TIMEOUT = common_likes_timeout

        self._debug = debug
        self.lang = lang
        self.common_likes = common_likes
        self.requires_common_likes = requires_common_likes

        self.connected = False
        self.client_id = ""
        self.rand_id = rand_id or OmegleBot._generate_rand_id()
        self.event_processing = False
        self.event_specification = {
            'waiting': lambda *args: None,
            'connected': self._connected,
            'disconnected': self._disconnected,
            'strangerDisconnected': self._stranger_disconnected,
            'gotMessage': self._got_message,
            'commonLikes': self._common_likes,
            'serverMessage': lambda *args: None,
            'identDigests': lambda *args: None,
            'typing': self._on_typing
        }
        self.events = []

    def typing(self):
        res = requests.post(self._BASE_URL + 'typing', data={'id': self.client_id})
        if res.text != "win":
            sys.stderr.write(f"[!] Could not be typing :( at: {asctime()}")

    def on_typing(self):
        pass

    def _on_typing(self, *args, **kwargs):
        self.on_typing()

    def send(self, message):
        res = requests.post(self._BASE_URL + 'send', data={'msg': message, 'id': self.client_id})
        if res.text != 'win':
            sys.stderr.write(f'[!] Could not send the message {message} at: {asctime()}')
            return -1

    def on_stranger_disconnected(self):
        pass

    def _stranger_disconnected(self, *args, **kwargs):
        self.on_stranger_disconnected()

    @staticmethod
    def _generate_rand_id():
        chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
        return "".join([choice(chars) for _ in range(8)])

    def _got_message(self, message):
        self.on_message(message[0])

    def _ident_digests(self, *args, **kwargs):
        self.on_connected()

    def disconnect(self):
        if not self.connected:
            print("[!] Not connected to anything, returning...")
            return

        res = requests.post(self._BASE_URL + 'disconnect', data={
                'id': self.client_id
        })
        if res.text == 'win':
            print("[*] Disconnected successfully")
        else:
            print("[!] Oh fuck... you are stuck bro")

    @staticmethod
    def _make_topics(topics):
        if not topics:
            return ""
        mtopics = "["
        for topic in topics:
            topic = topic.replace('"', '\\"')
            mtopics += f'"{topic}",'
        mtopics = mtopics[:-1]
        mtopics += ']'
        return mtopics

    def on_connected(self):
        pass

    def _connected(self, *args, **kwargs):
        self.connected = True
        self.on_connected()
        if self._debug:
            print(f"[*] Yo, you got a friend \"connected\" at: {asctime()}")

    def _common_likes(self, common_likes):
        self.common_likes = common_likes

    def _disconnected(self, *args, **kwargs):
        self.event_processing = False
        self.connected = False

    def start(self):
        if self._debug:
            print(f"[*] Starting at: {asctime()}")
        res = requests.post(self._BASE_URL + "start", params={
            'caps': 'recaptcha2',
            'firstevents': '1',
            'spid': '',
            'randid': self.rand_id,
            'topics': OmegleBot._make_topics(self.common_likes),
            'lang': self.lang
        })
        _json = res.json()
        if self._debug:
            print(f"[*] Topics: {OmegleBot._make_topics(self.common_likes)}")
            print(f"[*] Json at {asctime()}")
            print(_json)
        events, client_id = _json.values()
        if self._debug:
            print(f"[*] Printing events and client_id: at: {asctime()}")
            print("\tevents: ", events)
            print("\tclient_id: ", client_id)
        self.client_id = client_id
        self.events.extend(events)
        if not self.requires_common_likes:
            self._stop_waiting_common_likes()
        self._start_processing_events()

    @thread
    def _stop_waiting_common_likes(self):
        sleep(self.COMMON_LIKES_TIMEOUT)
        if self._debug:
            print(f"[*] Stopped looking for common likes at: {asctime()}")
        requests.post(self._BASE_URL + 'stoplookingforcommonlikes', data={'id': self.client_id})

    @thread
    def _start_fetching_events(self):
        while not self.client_id:
            sleep(.5)

        while self.event_processing:
            sleep(.5)
            res = requests.post(self._BASE_URL + 'events', data={'id': self.client_id})
            info = res.json()
            if not info:
                self.event_processing = False
                self.connected = False
                return
            self.events.extend(info)

    @thread
    def _start_processing_events(self):
        if self.event_processing:
            return
        self.event_processing = True
        self._start_fetching_events()
        while self.event_processing:
            for event in self.events:
                if self._debug:
                    print(f"[*] New event: at: {asctime()}")
                    print("\t", event)
                name_id = event[0]
                self.event_specification.get(name_id, lambda *args: None)(event[1:])
                self.events.pop(0)

    @staticmethod
    def _get_a_server() -> str:
        res = requests.get("https://omegle.com/status")
        servers = res.json()["servers"]
        assert servers, "[!] Omegle is apparently?? Down?????? :((( or we can't access it?"
        return f'https://{servers[0]}.omegle.com/'

    def on_message(self, message: str) -> None:
        if self._debug:
            print(">>", message)


if __name__ == '__main__':
    omegle_bot = OmegleBot(common_likes=["test"], requires_common_likes=True, debug=True, lang="pt")
    omegle_bot.start()
