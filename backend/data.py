"""
    author: ffpereira
    date: 2025-09-17
"""

import os
import json

import requests
from dotenv import load_dotenv
from urllib.parse import urlparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.models import Radio, Song, Artist, OtherArtist, Album, Play, NoMcr

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))
ALCHEMICAL_DATABASE_URL = os.environ.get('DATABASE_URL')

engine = create_engine(ALCHEMICAL_DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

todo_directory = 'data/todo'

num_file = 0
total_files = len(os.listdir(todo_directory))
for file in os.listdir(todo_directory):
    num_file += 1
    filedir = os.path.join(todo_directory, file)
    print(f"Found file: {filedir}")

    # parse radio name from file
    radio_name = file.split('_')[0]

    # check if radio exists
    radio = db.query(Radio).filter(Radio.name == radio_name).first()
    if not radio:
    #if radio_name not in ["radio-comercial", "cidade", "m80"]:
        print(f"Radio {radio_name} not found.")
        os.rename(filedir, os.path.join('data/error', file))
        continue

    images_link = None
    if radio.name == 'radio-comercial':
        images_link = 'https://radiocomercial.pt'
    elif radio.name == 'cidade':
        images_link = 'https://cidade.fm'
    else:
        images_link = 'https://m80.pt'

    try:
        with open(filedir, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"File {filedir} is not valid JSON: {e}")
        os.rename(filedir, os.path.join('data/error', file))
        continue

    try:
        songs = data["NOW_PLAYING_LOG"]["NOW_PLAYING_RECORD"]
    except KeyError as e:
        print(f"Missing key in JSON data: {e}")
        os.rename(filedir, os.path.join('data/error', file))
        continue

    num_play = 0
    total_songs = len(songs)
    for song in songs:
        num_play += 1
        total_files_str = f"File ({num_file}/{total_files}) - Play ({num_play}/{total_songs})"
        date = song["DATE"]

        if song["MCR"] is None or song["MCR"]["LEAD_ARTIST"] is None or song["MCR"]["LEAD_ARTIST"].get("NAME") is None or song["MCR"]["ALBUM"] is None:
            no_mcr = NoMcr(
                item_code=song["ZENON"]["ITEM_CODE"],
                radio_id=radio.id,
                timestamp=date,
                song_name=song["ZENON"]["SONG_NAME"],
                artist_name=song["ZENON"]["ARTIST_NAME"]
            )
            db.add(no_mcr)
            print(f"{total_files_str} - No MCR data for song: {song['ZENON']['SONG_NAME']} by {song['ZENON']['ARTIST_NAME']}")
            continue

        song_id = song["MCR"]["SONG_ID"]
        song_lyric = song["MCR"]["SONG_LYRIC"]
        album = song["MCR"]["ALBUM"]
        lead_artist = song["MCR"]["LEAD_ARTIST"]

        existing_artist = db.query(Artist).filter(Artist.id == lead_artist["ID"]).first()
        if not existing_artist:
            # Ask Gemini for artist info
            # time.sleep(6)  # to avoid rate limiting
            # artist_info = ask_gemini(lead_artist["NAME"], song["MCR"]["SONG_NAME"])
            artist_info = {}
            # print(artist_info)
            new_artist = Artist(
                id=lead_artist["ID"],
                name=lead_artist["NAME"],
                description=artist_info.get("description", None),
                nationality=artist_info.get("nationality", None),
                date_of_birth=artist_info.get("date_of_birth", None),
                date_of_death=artist_info.get("date_of_death", None),
                artist_type=artist_info.get("artist_type", None)
            )
            db.add(new_artist)
        else:
            print(f"{total_files_str} - Artist {lead_artist['NAME']} already exists.")

        album_id = album["ID"]
        existing_album = db.query(Album).filter(Album.id == album_id).first()

        album_image_path = os.path.join('api/static/images/albums', f'{album_id}.jpg')
        need_main_image = not os.path.exists(album_image_path)

        if album_id is not None and (not existing_album or need_main_image):
            # Download album image
            if album["IMAGE"] and images_link is not None and need_main_image:
                # print(f"{total_files_str} - Downloading image for album ID {album_id} from {images_link}/upload/album/{album['IMAGE'].split(".jpg")[0]}.300x300.jpg")
                print(f"{total_files_str} - Downloading image for album ID {album_id} from {images_link}/upload/album/{album['IMAGE'].split('.jpg')[0]}.300x300.jpg")
                image_url = f'{images_link}/upload/album/{album["IMAGE"].split(".jpg")[0]}.300x300.jpg'
                # save to api/static/images/albums/{album["ID"]}.jpg
                img_response = requests.get(image_url)
                if img_response.status_code == 200:
                    img_path = os.path.join('api/static/images/albums', f'{album["ID"]}.jpg')
                    # os.makedirs(os.path.dirname(img_path), exist_ok=True)
                    with open(img_path, 'wb') as img_file:
                        img_file.write(img_response.content)

            if not existing_album:
                new_album = Album(
                    id=album["ID"],
                    name=album["NAME"],
                    type=album["TYPE"],
                    artist_id=lead_artist["ID"]
                )
                db.add(new_album)
            else:
                print(f"{total_files_str} - Album {album['NAME']} already exists but images were missing.")

        existing_song = db.query(Song).filter(Song.id == song_id).first()
        has_sample, need_sample_download = False, False

        if not existing_song:
            need_sample_download = bool(song["MCR"]["CLIP_URL"])
        elif existing_song.sample is False and song["MCR"]["CLIP_URL"]:
            need_sample_download = True # Song exists but marked as no sample in DB → redownload

        if need_sample_download:
            # Download song sample
            print(f"{total_files_str} - Downloading sample for song ID {song_id} from {song['MCR']['CLIP_URL']}")
            clip_url = urlparse(song["MCR"]["CLIP_URL"])

            if clip_url.scheme:
                mp4_response = requests.get(song["MCR"]["CLIP_URL"])

                if mp4_response.status_code == 200:
                    mp4_path = os.path.join('api/static/samples', f'{song_id}.mp4')
                    with open(mp4_path, 'wb') as img_file:
                        img_file.write(mp4_response.content)
                    has_sample = True
                else:
                    has_sample = False
                    print(f"{total_files_str} - Failed to download sample for song ID {song_id} from {song['MCR']['CLIP_URL']}")

        if not existing_song:
            new_song = Song(
                id=song_id,
                item_code=song["ZENON"]["ITEM_CODE"],
                name=song["MCR"]["SONG_NAME"],
                lead_artist_id=song["MCR"]["LEAD_ARTIST"]["ID"],
                album_id=album["ID"] if album["ID"] is not None else None,
                sample=has_sample,
            )
            db.add(new_song)
        elif has_sample and not existing_song.sample:
            existing_song.sample = True
            db.add(existing_song)
            print(f"{total_files_str} - Updated sample for song ID {song_id}")

        play = Play(
            radio_id=radio.id,
            song_id=song_id,
            timestamp=date
        )
        db.add(play)

        other_artists = []
        if song["MCR"]["OTHER_ARTISTS"]:
            other_artists = song["MCR"]["OTHER_ARTISTS"]["ARTIST"]
            if isinstance(other_artists, dict):
                other_artists = [other_artists]
            for artist in other_artists:
                existing_artist = db.query(Artist).filter(Artist.id == artist["ID"]).first()
                if not existing_artist:
                    # artist_info = ask_gemini(lead_artist["NAME"], song["MCR"]["SONG_NAME"])
                    artist_info = {}
                    new_artist = Artist(
                        id=artist["ID"],
                        name=artist["NAME"],
                        description=artist_info.get("description", None),
                        nationality=artist_info.get("nationality", None),
                        date_of_birth=artist_info.get("date_of_birth", None),
                        date_of_death=artist_info.get("date_of_death", None),
                        artist_type=artist_info.get("artist_type", None)
                    )
                    db.add(new_artist)
                else:
                    print(f"{total_files_str} - Artist {artist['NAME']} already exists.")

                existing_other_artist_song = db.query(OtherArtist).filter(
                    OtherArtist.song_id == song_id,
                    OtherArtist.artist_id == artist["ID"]
                ).first()
                if not existing_other_artist_song:
                    new_other_artist = OtherArtist(
                        song_id=song_id,
                        artist_id=artist["ID"],
                        name=artist["NAME"]
                    )
                    db.add(new_other_artist)

        song_data = {
            "lyric": song_lyric,
            "album": album,
            "lead_artist": lead_artist,
            "other_artists": other_artists,
            "date": date
        }
        # print(song_data)

    db.commit()

    # move file to done
    os.rename(filedir, os.path.join('data/done', file))
    print(f"Processed file: {filedir}")
