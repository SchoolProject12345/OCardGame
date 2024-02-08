## Berda's Sound engine v0.0.75834672548172143785612847781236441237856
from pygame import mixer
import pygame
import os

from sympy import false, true
from utility import cwd_path


def sound_handle(track:str , action_type:str = "play", volume:int=100, channel:int=5, loop:bool=False):
    # a terminer


    sfx_path = os.path.join(cwd_path, "Assets", "Sfx", str(track) + ".wav")
    
    sfxchannel = pygame.mixer.Channel(channel)
    sound = pygame.mixer.Sound(sfx_path)
    sound.set_volume(volume/100)

    previous_volume = volume/100
    mute_status = False

    if action_type == "play":
        sfxchannel.play(sound, loops=-1 if loop else 0)

    if action_type == "stop":
        sfxchannel.stop()


# faut test
# pour mote unmute, juste mute + channel du track (by default music deverait etre 2)
# NE PAS UTILSER LA FONC AVEC VOLUME 0 POUR MUTE, UTILISER JUSTE ARGUMENT MUTE ET LE BON CHANNEL.
        
    if action_type == "mute" and mute_status == False:
        previous_volume = sound.get_volume() *  100
        sound.set_volume(0)
        mute_status = True
    else:
        print("mute action non permitted, check if you didnt already mute somewhere")

    if action_type == "unmute":
        sound.set_volume(previous_volume/100)
        mute_status = False



