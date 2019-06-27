from spotdl import handle
from spotdl import const
from spotdl import downloader
import os
import subprocess,sys
#Inline Function
import spotipy
from pprint import pprint
from spotipy.oauth2 import SpotifyClientCredentials
import json
from traceback import print_exc
client_id = "e8a216dfeede4e1082e2f1e0229542ec"
client_secret = "c148928b1daa495eafe4c36891d885be"

def prettify_time(millis):
    millis = int(millis)
    seconds=(millis/1000)%60
    seconds = int(seconds)
    minutes=(millis/(1000*60))%60
    minutes = int(minutes)
    return ("%d minutes %d seconds " % ( minutes, seconds))

def search(query):
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    results = sp.search(q=str(query), limit=5,type='playlist', market='IN')
    return results

def read_playlist(uri):
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    try:
        username = uri.split(':')[0]
        playlist_id = uri.split(':')[-1]

        results = sp.user_playlist(username, playlist_id)
        songs_json=[]
        limited_results=results['tracks']['items'][:25]
        for i in limited_results:
            songs_data={}
            songs_data['song_name']=(i['track']['name'])
            songs_data['album_name']=(i['track']['album']['name'])
            songs_data['duration']=prettify_time(i['track']['duration_ms'])
            songs_data['artist_name']=(i['track']['artists'][0]['name'])
            try:
                songs_data['thumbnail']=(i['track']['album']['images'][0]['url'])
            except IndexError:
                songs_data['thumbnail']='https://tinyimg.io/i/tYtVkja.jpg'
            songs_data['url']=(i['track']['external_urls']['spotify'])
            songs_json.append(songs_data)

        return songs_json

    except Exception as e:
        print(e)
        print_exc()
def spotify_dl(context,update,link):

    user_id=update.message.chat_id,
    status=context.bot.send_message(chat_id=update.message.chat_id,text="Downloading Song!..\nPlease wait..",reply_to_message_id=update.message.message_id)
    try:
        # modify attributes on `const.args` to change any default arguments
        # https://github.com/ritiek/spotify-downloader/blob/67ae7d5c4c9ed289f278a3ad6bfae658b812196f/spotdl/handle.py#L15-L36
        const.args = handle.get_arguments(to_group=False)
        # loglevel can be one of `logging.NOTSET`, `logging.INFO`, `logging.WARNING`, `logging.ERROR`, `logging.DEBUG`
        const.logzero.setup_default_logger(
                                formatter=const._formatter,
                                level=const.logzero.logging.INFO)
        const.args.folder=os.getcwd()
        const.args.trim_silence=True
        #key=link.split('https://open.spotify.com/')[1].split('/')[0]
        #print(link)
        if '/track/' in link:
            print("Track Invoked")
            # raw_song can take Spotify/Youtube URLs or a string
            track = downloader.Downloader(raw_song=link)
            #print(const.args)
            # you probably need one of these variables
            track_title = track.refine_songname(track.content.title)
            track_filename = track_title + const.args.output_ext
            #track_download_path = os.path.join(const.args.folder, track_filename)
            # download, convert and embed metadata
            track.download_single()
            status.edit_text(text='Sending your awesome song!...\n')
            a=context.bot.send_audio(chat_id=update.message.chat_id,audio=open(track_filename,'rb'),caption='Downloaded using @emojifymusicbot', timeout=1000)
            os.remove(track_filename)
        elif '/album/' in link:
            print("Album")
            cmd=['spotdl','--write-to','album.txt','--album',link]
            subprocess.call(cmd)
            with open('album.txt', 'r') as myfile:
                data=myfile.read()
            data=data.split('\n')
            data.pop()
            os.remove('album.txt')
            i=1

            for link in data:
                try:
                    track = downloader.Downloader(raw_song=link)
                    #print(const.args)
                    # you probably need one of these variables
                    track_title = track.refine_songname(track.content.title)
                    track_filename = track_title + const.args.output_ext
                    #track_download_path = os.path.join(const.args.folder, track_filename)
                    # download, convert and embed metadata
                    track.download_single()
                    status.edit_text(text='Sending '+str(i)+'/'+str(len(data))+' songs...\n')
                    a=context.bot.send_audio(chat_id=update.message.chat_id,audio=open(track_filename,'rb'),caption='Downloaded using @emojifymusicbot', timeout=1000)
                    os.remove(track_filename)
                except Exception as e:
                    print(e)
                finally:
                    i=i+1
            status.edit_text(text='Thanks for using @emojifymusicbot\n')

        elif '/playlist/' in link:
            cmd=['spotdl','--write-to','playlist.txt','--playlist',link]
            subprocess.call(cmd)
            with open('playlist.txt', 'r') as myfile:
                data=myfile.read()
            data=data.split('\n')
            data.pop()
            os.remove('playlist.txt')
            i=1

            for link in data:
                try:
                    ack=mongo.send_saved_song(link,user_id)
                    if ack==1:
                        update_db(bot,update,link,'Cached','from_cache')
                        continue
                    track = downloader.Downloader(raw_song=link)
                    #print(const.args)
                    # you probably need one of these variables
                    track_title = track.refine_songname(track.content.title)
                    track_filename = track_title + const.args.output_ext
                    #track_download_path = os.path.join(const.args.folder, track_filename)
                    # download, convert and embed metadata
                    track.download_single()
                    status.edit_text(text='Sending '+str(i)+'/'+str(len(data))+' songs...\n')
                    if '/app/' in track_filename:
                        track_filename=str(track_filename.split('/app/')[-1])
                    a=context.bot.send_audio(chat_id=update.message.chat_id,audio=open(track_filename,'rb'),caption='Downloaded using @emojifymusicbot', timeout=1000)
                    os.remove(track_filename)
                except Exception as e:
                    print(e)
                finally:
                    i=i+1
            status.edit_text(text='Thanks for using @emojifymusicbot\n')
    except Exception as e:
        status.edit_text(text='Error Occured\nPlease try downloading a different song\n')
 
