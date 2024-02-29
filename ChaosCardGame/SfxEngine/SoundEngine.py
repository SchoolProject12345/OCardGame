## Berda's Sound engine v0.0.75834672548172143785612847781236441237856
from operator import is_
from pygame import mixer
import os
from utility import cwd_path, get_setting, get_settings, static


@static
def sound_handle(track: str = "ClickSound12" , action_type: str = "play", volume: int = 100, channel: int = 5, loop: bool = False, is_muted: bool = False):
    # à terminer
    """Erda's basic pygame sound engine, lets you handle sounds, music, effects etc...
    How work? sound_handle( 
        - what track? only put name not the extension
        - what do you want to do with it? play stop mute/unmute
        - at what volume ? from 0 to 100
        - in what channel? (you cant put 2 things at the same time in the same channel, use it carefully)
        - want it to loop? (true or false)
        - is_muted?... its da variable to get from the settings file, as you will mute either sounds, music or speech. they are all in the settingsfile and can be adjusted.
        to be finished, it works even though its not perfect so dont touch it )
    """

    actions = ["play", "stop", "mute/unmute"]
    if action_type not in actions:
        raise ValueError(f"invalid action {action_type}, check spelling or whatever did you had typen in bruv")
    else:

        sfx_path = os.path.join(cwd_path, "Assets", "Sfx", str(track) + ".wav") # put only filename, not extension in track
        
        sfxchannel = mixer.Channel(channel)
        sound = mixer.Sound(sfx_path)
        sound.set_volume(volume/100)

        match action_type:
            case "play":
                sfxchannel.play(sound, loops= -1 if loop else 0)
            case "stop":
                sfxchannel.stop()
            case "mute/unmute":
                if get_setting("mute", False):
                    get_settings()["volume"] = int(sfxchannel.get_volume()*100)
                    sfxchannel.set_volume(0)
                    print("tried to mute")
                else:
                    sfxchannel.set_volume(get_setting("volume", 100)/100)
                    print("tried to unmute")
                    get_settings()["volume"] = int(sfxchannel.get_volume()*100)

        music_channels = [2]
        sfx_channels = [3,8]
        speech_channels = [7]
        # ajouter par la suite tous les channels avec le so et les vruits, pour regrouper les truks a mute.
        # faut test
        # pour mute unmute, juste mute + channel du track (by default music deverait etre 2)
        # NE PAS UTILSER LA FONC AVEC VOLUME 0 POUR MUTE, UTILISER JUSTE ARGUMENT MUTE ET LE BON CHANNEL.

    # PAS TOUCHER AUX FONCTIONNEMENTS DES CHANNELS POUR LINSTANT CYKA
