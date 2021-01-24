# omegle-api
Well... it is a python api for omegle :)


# Usage
```
from OmegleBot import OmegleBot


class MyBot(OmegleBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_message(self, message: str) -> None:  # Called when a new message arrives
        self.send("Sorry bra, i'm just a bot. Questioning myself you know?? Bye :_(")
        self.disconnect()
    
    def on_typing(self):  # Called when the person is typing
        print("Yo, the dude is typing?!!!")
    
    def on_stranger_disconnected(self):  # Called when the person disconnects
        print("Why am I so LONELY!!!!")


if __name__ == '__main__':
    my_bot = MyBot(common_likes=["potatoes"], requires_common_likes=True, debug=True)
    my_bot.start()

```
Yeah, I have things to do so the README is going to stay like that for some time
Have a great day :)
