## Berda's Sound engine v0.0.76
from pygame import mixer
import os
from utility import cwd_path, get_setting


def sound_handle(track:str="ClickSound12" , action_type:str = "play", volume:int=100, channel:int=5, loop:bool=False, is_muted=None):
    # a terminer
    """Erda's basic pygame sound engine, lets you handle sounds, music, effects etc...
    How work? sound_handle( 
        - what track? only put name not the extension
        - what do you want to do with it? play stop mute/unmute
        - at what volume ? from 0 to 100
        - in what channel? (you cant put 2 things at the same time in the same channel, use it carefully)
        - want it to loop? (true or false)
        - is_muted?... this one is tricky, use it only when you mute something( in that case use only sound_handle( mute/unmute, what channel, is_muted= is muted option from settings file))
        )
        to be finished, it works even though its not perfect so dont touch it
    """




    sfx_path = os.path.join(cwd_path, "Assets", "Sfx", str(track) + ".wav")
    
    sfxchannel = mixer.Channel(channel)
    sound = mixer.Sound(sfx_path)
    sound.set_volume(volume/100)

    global previous_volume

    if action_type == "play":
        sfxchannel.play(sound, loops=-1 if loop else 0)

    if action_type == "stop":
        sfxchannel.stop()


    # faut test
    # pour mote unmute, juste mute + channel du track (by default music deverait etre 2)
    # NE PAS UTILSER LA FONC AVEC VOLUME 0 POUR MUTE, UTILISER JUSTE ARGUMENT MUTE ET LE BON CHANNEL.

    if action_type == "mute/unmute":

        if get_setting("mute", False):
            previous_volume = sfxchannel.get_volume()*100
            sfxchannel.set_volume(0)
            print("tried to mute")

        if  not get_setting("mute", False):
            sfxchannel.set_volume(previous_volume/100)
            print("tried to unmute")
            previous_volume = sfxchannel.get_volume() *  100





