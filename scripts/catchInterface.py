import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import requests
from io import BytesIO
import functools
from PIL import Image, ImageDraw
import webbrowser
from tkinter import ttk
import os

def open_linkedin():
    webbrowser.open("https://www.linkedin.com/in/asher-gabriela/")

def open_github():
    webbrowser.open("https://github.com/ashcrysis")

def create_colored_circle(color, size=(15, 15)):
    image = Image.new("RGBA", size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse([(0, 0), size], fill=color)
    return ImageTk.PhotoImage(image)

def map_persona_state(numeric_state):
    if numeric_state == 0:
        return "Offline"
    elif numeric_state == 1:
        return "Online"
    elif numeric_state == 2:
        return "Busy"
    elif numeric_state == 3:
        return "Away"
    elif numeric_state == 4:
        return "Snooze"
    elif numeric_state == 5:
        return "Looking to Trade"
    elif numeric_state == 6:
        return "Looking to Play"
    else:
        return "Unknown State"

def get_game_list(steam_id, api_key):
    url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steam_id}&format=json'
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if 'response' in data and 'games' in data['response']:
            games = data['response']['games']
            return games
        else:
            print('Error retrieving game list.')
            return None
    
    except Exception as e:
        print(f'Error: {e}')
        return None

@functools.lru_cache(maxsize=None)
def get_game_name_and_image(appid, api_key):
    url_info = f'http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={api_key}&appid={appid}'

    try:
        response_info = requests.get(url_info)
        data_info = response_info.json()

        if 'game' in data_info and 'gameName' in data_info['game']:
            game_name = data_info['game']['gameName']

            # Build the game image URL
            img_icon_url = f"http://media.steampowered.com/steamcommunity/public/images/apps/{appid}/{appid}.jpg"

            return game_name, img_icon_url
        else:
            print('Error retrieving game information.')
            return None, None

    except Exception as e:
        print(f'Error: {e}')
        return None, None

def get_player_info(steam_id, api_key):
    url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}'

    try:
        response = requests.get(url)
        data = response.json()

        if 'response' in data and 'players' in data['response']:
            player = data['response']['players'][0]
            personaname = player.get('personaname', 'Name not available')
            personastate = player.get('personastate', 'State not available')
            avatar_url = player.get('avatarfull', None)

            # Add information about the current game and the last played game
            current_game = player.get('gameextrainfo', 'Not currently playing')
            last_game = player.get('last_app', 'No game history')

            return personaname, personastate, avatar_url, current_game, last_game
        else:
            print('Error retrieving player information.')
            return None, None, None, None, None

    except Exception as e:
        print(f'Error: {e}')
        return None, None, None, None, None

def create_main_screen():
    def get_information():
       
        steam_id = entry_steam_id.get()
        api_key = 'YOUR_API_KEY'

        personaname, personastate, avatar_url, current_game, last_game = get_player_info(steam_id, api_key)
        game_list = get_game_list(steam_id, api_key)
        
        if game_list:
            games_with_name = []
            games_without_name = []

            for game in game_list:
                appid = game.get('appid', 'AppID not available')
                playtime_minutes = game.get('playtime_forever', 0)
                playtime_hours = playtime_minutes / 60

                game_name, img_url = get_game_name_and_image(appid, api_key)

                if game_name == 'Name not available' or game_name is None:
                    games_without_name.append(('Name not available', appid, playtime_hours))
                else:
                    games_with_name.append((game_name, appid, playtime_hours))

            games_with_name = sorted(games_with_name, key=lambda x: x[1], reverse=True)

            show_results(personaname, personastate, avatar_url, games_with_name, current_game, last_game)
           
    
    def show_results(personaname, personastate, avatar_url, games_with_name, current_game, last_game):
        result_window = tk.Toplevel(root)
        result_window.title("Results")
        screen_width = result_window.winfo_screenwidth()
        screen_height = result_window.winfo_screenheight()

        # Set the dimensions of the main window
        window_width = 500  # Adjust as needed
        window_height = 600  # Adjust as needed

        # Calculate the position to center the window
        x_pos = (screen_width - window_width) // 2
        y_pos = (screen_height - window_height) // 2

        # Set the geometry of the main window
        result_window.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        result_window.configure(bg='#262626')  # Dark background color
        
        
        
        # Center the photo
        lbl_avatar = tk.Label(result_window)
        lbl_avatar.grid(row=0, column=0, columnspan=3, pady=10, sticky="n")
        load_avatar(lbl_avatar, avatar_url)

        lbl_name = tk.Label(result_window, text=f"Personal Name: {personaname}", font=("Arial", 12, "bold"), bg='#262626', fg='white')
        lbl_name.grid(row=1, column=0, columnspan=3, pady=5)

        personastate_text = map_persona_state(personastate)
        lbl_state = tk.Label(result_window, text=f"Persona State: {personastate_text}", font=("Arial", 12), bg='#262626', fg='white')
        lbl_state.grid(row=2, column=1, columnspan=1, pady=5)

        btn_reload = tk.Button(result_window, text="Reload Info", command=get_information, bg='#262626', fg='white', font=("Arial", 12))
        btn_reload.grid(row=6,column=0, columnspan=3, pady=5)
        # Create state circle
        if personastate == 0:
            circle_color = "black"
        elif personastate == 1:
            circle_color = "green"
        elif personastate == 2:
            circle_color = "orange"
        elif personastate == 3:
            circle_color = "pink"
        else:
            circle_color = "white"

        state_circle = create_colored_circle(circle_color)
        lbl_state_circle = tk.Label(result_window, image=state_circle, bg='#262626')
        lbl_state_circle.photo = state_circle
        lbl_state_circle.grid(row=2, column=2, pady=5, sticky="w")

        lbl_current_game = tk.Label(result_window, text=f"Current Game: {current_game}", font=("Arial", 12), bg='#262626', fg='white')
        lbl_current_game.grid(row=3, column=0, columnspan=3, pady=5)

        lbl_last_game = tk.Label(result_window, text=f"Last Played Game: {last_game}", font=("Arial", 12), bg='#262626', fg='white')
        lbl_last_game.grid(row=4, column=0, columnspan=3, pady=5)

        lbl_all_games = tk.Label(result_window, text="All Games", font=("Arial", 12, "underline"), bg='#262626', fg='white')
        lbl_all_games.grid(row=7, column=0, columnspan=3, pady=5)

        text_all_games = scrolledtext.ScrolledText(result_window, width=60, height=15, bg='#333333', fg='white')
        text_all_games.grid(row=8, column=0, columnspan=3, pady=5)

        all_games = sorted(games_with_name, key=lambda x: x[2], reverse=True)

        for game in all_games:
            if game[0] == 'Name not available' or game[0] == None or game[0] == "None":
                game_name = f"Name not available (AppID: {game[1]})"
            else:
                game_name = f"{game[0]} (AppID: {game[1]})"

            hours_played = game[2]
            text_all_games.insert(tk.END, f"{game_name} - {hours_played:.2f} hours played\n")
        
        result_window.mainloop()

    def load_avatar(label, avatar_url):
        response = requests.get(avatar_url)
        img_data = BytesIO(response.content)
        img = Image.open(img_data)
        img = img.resize((100, 100), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.BICUBIC)
        photo = ImageTk.PhotoImage(img)
        label.configure(image=photo)
        label.image = photo

    root = tk.Tk()
    root.title("Steam API Getter")

    # Add a banner
    banner_path = "steamAPIGetter/sample/asher-asmp-header.jpg"  # Replace with the actual path of the banner
    if os.path.exists(banner_path):
        banner_img = Image.open(banner_path)
        window_width = 500  # Adjust as needed
        window_height = 600  # Adjust as needed
        banner_img = banner_img.resize((window_width, 100))

        banner_photo = ImageTk.PhotoImage(banner_img)

        banner_label = tk.Label(root, image=banner_photo, bg='#333333')
        banner_label.photo = banner_photo
        banner_label.pack()

    lbl_instruction = tk.Label(root, text="Steam ID:", font=("Arial", 12), bg='#333333', fg='white')
    lbl_instruction.pack(pady=(20, 10))  # Added spacing above and below

    entry_steam_id = tk.Entry(root, width=30, font=("Arial", 12))
    entry_steam_id.pack(pady=10)

    btn_get_info = tk.Button(root, text="Get Information", command=get_information, bg='#3498db', fg='white', font=("Arial", 12))
    btn_get_info.pack(pady=10)

    btn_linkedin = tk.Button(root, text="Dev LinkedIn", command=open_linkedin, bg='#0077b5', fg='white', font=("Arial", 10, "italic"))
    btn_linkedin.pack(pady=5)

    btn_github = tk.Button(root, text="Dev GitHub", command=open_github, bg='#333333', fg='white', font=("Arial", 10, "italic"))
    btn_github.pack(pady=5)
    
    window_width = 500  # Adjust as needed
    window_height = 600  # Adjust as needed
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    lbl_dev = tk.Label(root, text="@ashcrysis", font=("Arial", 12), bg='#262626', fg='white')
    lbl_dev.pack(pady=(20, 10))  # Added spacing above and below
    # Calculate the position to center the window
    x_pos = (screen_width - window_width) // 2
    y_pos = (screen_height - window_height) // 2

    # Set the geometry of the main window
    root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

    root.configure(bg='#262626')  # Dark background color
    root.mainloop()

if __name__ == "__main__":
    create_main_screen()
    update_information()
