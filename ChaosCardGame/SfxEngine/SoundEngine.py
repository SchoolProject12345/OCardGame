## Berda's Sound engine v0.0.75834672548172143785612847781236441237857
from operator import is_
from pygame import mixer
import pygame
import os
from utility import cwd_path, get_setting, get_settings, static


@static
def sound_handle(track: str = "ClickSound12" , action_type: str = "play", volume: int = 100, channel: int = 5, loop: bool = False, is_muted: bool = False):
    # à terminer

    sfx_path = os.path.join(cwd_path, "Assets", "Sfx", str(track) + ".wav")
    
    sfxchannel = pygame.mixer.Channel(channel)
    sound = pygame.mixer.Sound(sfx_path)
    sound.set_volume(volume/100)

    if action_type == "play":
        sfxchannel.play(sound, loops=-1 if loop else 0)

    if action_type == "stop":
        sfxchannel.stop()


# faut test
# pour mote unmute, juste mute + channel du track (by default music deverait etre 2)
# NE PAS UTILSER LA FONC AVEC VOLUME 0 POUR MUTE, UTILISER JUSTE ARGUMENT MUTE ET LE BON CHANNEL.

    if action_type == "mute/unmute":

        if get_setting("mute", False):
            get_settings()["volume"] = int(sfxchannel.get_volume()*100)
            sfxchannel.set_volume(0)
            print("tried to mute")
        else:
            sfxchannel.set_volume(get_setting("volume", 100)/100)
            print("tried to unmute")
            get_settings()["volume"] = sfxchannel.get_volume() *  100





