from bleach import clean
from Core.core_main import cleanstr
from Network.server import HandlerHandler as handle
from SfxEngine.SoundEngine import sound_handle

def log_dash_formechange(head, _, forme:str, *args, **kwargs):
    if cleanstr(forme) == "bobthegoldfish":
        sound_handle("spelluse", "play", channel=10)
handle.add_log_player(log_dash_formechange)


# idk how this work or if it does work but its here, plays sound when specific card enters play