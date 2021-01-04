import sys
import spotipy
import spotipy.util as util


class User:
    def __init__(self):
        self.username = None
        self.client = None


def get_auth():
    user = User()
    user.username = input("Please enter your username: ")
    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(user.username, scope)
    if not token:
        sys.exit()
    user.client = spotipy.Spotify(auth=token)
    return user


def choose_playlist(user):
    playlists = user.client.user_playlists(user.username)
    playlist_dict = {}
    i = 1
    for playlist in playlists['items']:
        if playlist['owner']['id'] == user.username:
            print(i, playlist['name'])
            playlist_dict[str(i)] = playlist['id']
            i += 1
    to_fix = -1
    while True:
        to_fix = input("Please enter the number of the playlist to repair: ")
        if to_fix in playlist_dict:
            break
        else:
            print(to_fix, "is not an option")
    return playlist_dict[to_fix]


def find_tracks(playlist):
    track_dict = {}
    track_ids = []
    to_remove = []
    for i, track in enumerate(playlist['items']):
        track_dict[str(i)] = track['track']['id']
    for position, track_id in track_dict.items():
        if track_id in track_ids:
            to_remove.append({"uri": track_id, "positions": [int(position)]})
        else:
            track_ids.append(track_id)
    return to_remove


def main():
    user = get_auth()
    client = user.client
    username = user.username
    retry = 'y'
    while retry.lower() == 'y':
        playlist_id = choose_playlist(user)
        playlist = client.playlist_tracks(playlist_id=playlist_id, fields='items.track.id')

        to_remove = find_tracks(playlist)
        if to_remove:
            print("Duplicate tracks:")
            for track_id in to_remove:
                track = client.track(track_id['uri'])
                print("    ", track['name'])
        else:
            print("No duplicate tracks found.")
            retry = input("Would you like to remove duplicates from another playlist? [y/n]: ")
            continue

        select = input("Would you like to remove these tracks? [y/n]: ")
        if select.lower() == 'y':
            client.trace = False
            results = client.user_playlist_remove_specific_occurrences_of_tracks(username, playlist_id, to_remove)
            print("Duplicate tracks have been removed.")
        else:
            print("Duplicates have not been removed.")
        retry = input("Would you like to remove duplicates from another playlist? [y/n]: ")


if __name__ == '__main__':
    main()
