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

def abrir_linkedin():
    webbrowser.open("https://www.linkedin.com/in/asher-gabriela/")

def abrir_github():
    webbrowser.open("https://github.com/ashcrysis")

def criar_circulo_cor(cor, tamanho=(15, 15)):
    imagem = Image.new("RGBA", tamanho, (255, 255, 255, 0))
    desenho = ImageDraw.Draw(imagem)
    desenho.ellipse([(0, 0), tamanho], fill=cor)
    return ImageTk.PhotoImage(imagem)

def mapear_persona_state(estado_numerico):
    if estado_numerico == 0:
        return "Offline"
    elif estado_numerico == 1:
        return "Online"
    elif estado_numerico == 2:
        return "Busy"
    elif estado_numerico == 3:
        return "Away"
    elif estado_numerico == 4:
        return "Snooze"
    elif estado_numerico == 5:
        return "Looking to Trade"
    elif estado_numerico == 6:
        return "Looking to Play"
    else:
        return "Estado Desconhecido"


def obter_lista_jogos(steam_id, api_key):
    url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steam_id}&format=json'
    
    try:
        resposta = requests.get(url)
        dados = resposta.json()
        
        if 'response' in dados and 'games' in dados['response']:
            jogos = dados['response']['games']
            return jogos
        else:
            print('Erro ao obter lista de jogos.')
            return None
    
    except Exception as e:
        print(f'Erro: {e}')
        return None

@functools.lru_cache(maxsize=None)
def obter_nome_e_imagem_jogo(appid, api_key):
    url_info = f'http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={api_key}&appid={appid}'

    try:
        resposta_info = requests.get(url_info)
        dados_info = resposta_info.json()

        if 'game' in dados_info and 'gameName' in dados_info['game']:
            nome_do_jogo = dados_info['game']['gameName']

            # Construir URL da imagem do jogo
            img_icon_url = f"http://media.steampowered.com/steamcommunity/public/images/apps/{appid}/{appid}.jpg"

            return nome_do_jogo, img_icon_url
        else:
            print('Erro ao obter informações do jogo.')
            return None, None

    except Exception as e:
        print(f'Erro: {e}')
        return None, None

def obter_informacoes_jogador(steam_id, api_key):
    url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}'

    try:
        resposta = requests.get(url)
        dados = resposta.json()

        if 'response' in dados and 'players' in dados['response']:
            jogador = dados['response']['players'][0]
            personaname = jogador.get('personaname', 'Nome não disponível')
            personastate = jogador.get('personastate', 'Estado não disponível')
            avatar_url = jogador.get('avatarfull', None)

            # Adicione informações sobre o jogo atual e o último jogo jogado
            jogo_atual = jogador.get('gameextrainfo', 'Não está jogando no momento')
            ultimo_jogo = jogador.get('last_app', 'Não possui histórico de jogos')

            return personaname, personastate, avatar_url, jogo_atual, ultimo_jogo
        else:
            print('Erro ao obter informações do jogador.')
            return None, None, None, None, None

    except Exception as e:
        print(f'Erro: {e}')
        return None, None, None, None, None


def criar_tela():
    def obter_informacoes():
       
        steam_id = entry_steam_id.get()
        api_key = 'YOUR_API_KEY'

        personaname, personastate, avatar_url, jogo_atual, ultimo_jogo = obter_informacoes_jogador(steam_id, api_key)
        lista_jogos = obter_lista_jogos(steam_id, api_key)
        
        if lista_jogos:
            jogos_com_nome = []
            jogos_sem_nome = []

            for jogo in lista_jogos:
                appid = jogo.get('appid', 'AppID não disponível')
                tempo_jogado_minutos = jogo.get('playtime_forever', 0)
                tempo_jogado_horas = tempo_jogado_minutos / 60

                nome_do_jogo, img_url = obter_nome_e_imagem_jogo(appid, api_key)

                if nome_do_jogo == 'Nome não disponível' or nome_do_jogo is None:
                    jogos_sem_nome.append(('Nome não disponível',appid, tempo_jogado_horas))
                else:
                    jogos_com_nome.append((nome_do_jogo, appid, tempo_jogado_horas))

            jogos_com_nome = sorted(jogos_com_nome, key=lambda x: x[1], reverse=True)

            mostrar_resultados(personaname, personastate, avatar_url, jogos_com_nome,jogo_atual, ultimo_jogo)
           

    def mostrar_resultados(personaname, personastate, avatar_url, jogos_com_nome, jogo_atual, ultimo_jogo):
        resultado_window = tk.Toplevel(root)
        resultado_window.title("Resultados")
        largura_tela = resultado_window.winfo_screenwidth()
        altura_tela = resultado_window.winfo_screenheight()

        # Definir as dimensões da janela principal
        largura_janela = 500  # Ajuste conforme necessário
        altura_janela = 600  # Ajuste conforme necessário

        # Calcular a posição para centralizar a janela
        x_pos = (largura_tela - largura_janela) // 2
        y_pos = (altura_tela - altura_janela) // 2

        # Definir a geometria da janela principal
        resultado_window.geometry(f"{largura_janela}x{altura_janela}+{x_pos}+{y_pos}")
        resultado_window.configure(bg='#262626')  # Cor de fundo escura

        # Centralizar foto
        lbl_avatar = tk.Label(resultado_window)
        lbl_avatar.grid(row=0, column=0, columnspan=3, pady=10, sticky="n")
        carregar_avatar(lbl_avatar, avatar_url)

        lbl_nome = tk.Label(resultado_window, text=f"Personal Name: {personaname}", font=("Arial", 12, "bold"), bg='#262626', fg='white')
        lbl_nome.grid(row=1, column=0, columnspan=3, pady=5)

        personastate_texto = mapear_persona_state(personastate)
        lbl_estado = tk.Label(resultado_window, text=f"Persona State: {personastate_texto}", font=("Arial", 12), bg='#262626', fg='white')
        lbl_estado.grid(row=2, column=1, columnspan=1, pady=5)

        # Criar círculo de estado
        if personastate == 0:
            cor_circulo = "black"
        elif personastate == 1:
            cor_circulo = "green"
        elif personastate == 2:
            cor_circulo = "orange"
        elif personastate == 3:
            cor_circulo = "pink"
        else:
            cor_circulo = "white"

        circulo_estado = criar_circulo_cor(cor_circulo)
        lbl_circulo_estado = tk.Label(resultado_window, image=circulo_estado, bg='#262626')
        lbl_circulo_estado.photo = circulo_estado
        lbl_circulo_estado.grid(row=2, column=2, pady=5, sticky="w")

        lbl_jogo_atual = tk.Label(resultado_window, text=f"Jogo Atual: {jogo_atual}", font=("Arial", 12), bg='#262626', fg='white')
        lbl_jogo_atual.grid(row=3, column=0, columnspan=3, pady=5)

        lbl_ultimo_jogo = tk.Label(resultado_window, text=f"Último Jogo Jogado: {ultimo_jogo}", font=("Arial", 12), bg='#262626', fg='white')
        lbl_ultimo_jogo.grid(row=4, column=0, columnspan=3, pady=5)

        lbl_todos_jogos = tk.Label(resultado_window, text="Todos os Jogos", font=("Arial", 12, "underline"), bg='#262626', fg='white')
        lbl_todos_jogos.grid(row=5, column=0, columnspan=3, pady=5)

        texto_todos_jogos = scrolledtext.ScrolledText(resultado_window, width=60, height=15, bg='#333333', fg='white')
        texto_todos_jogos.grid(row=6, column=0, columnspan=3, pady=5)

        todos_jogos = sorted(jogos_com_nome, key=lambda x: x[2], reverse=True)

        for jogo in todos_jogos:
            if jogo[0] == 'Nome não disponível' or jogo[0] == None or jogo[0] == "None":
                nome_jogo = f"Nome não disponível (AppID: {jogo[1]})"
            else:
                nome_jogo = f"{jogo[0]} (AppID: {jogo[1]})"

            horas_jogadas = jogo[2]
            texto_todos_jogos.insert(tk.END, f"{nome_jogo} - {horas_jogadas:.2f} horas jogadas\n")

        resultado_window.mainloop()



    def carregar_avatar(label, avatar_url):
        response = requests.get(avatar_url)
        img_data = BytesIO(response.content)
        img = Image.open(img_data)
        img = img.resize((100, 100), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.BICUBIC)
        photo = ImageTk.PhotoImage(img)
        label.configure(image=photo)
        label.image = photo


    root = tk.Tk()
    root.title("Steam API Getter")

    # Adicione um banner
    banner_path = "steamAPIGetter/sample/asher-asmp-header.jpg"  # Substitua pelo caminho real do banner
    if os.path.exists(banner_path):
        banner_img = Image.open(banner_path)
        largura_janela = 500  # Ajuste conforme necessário
        altura_janela = 600  # Ajuste conforme necessário
        banner_img = banner_img.resize((largura_janela, 100))

        banner_photo = ImageTk.PhotoImage(banner_img)

        banner_label = tk.Label(root, image=banner_photo, bg='#333333')
        banner_label.photo = banner_photo
        banner_label.pack()

    lbl_instrucao = tk.Label(root, text="Steam ID:", font=("Arial", 12), bg='#333333', fg='white')
    lbl_instrucao.pack(pady=(20, 10))  # Adicionei um espaçamento acima e abaixo
    

    entry_steam_id = tk.Entry(root, width=30, font=("Arial", 12))
    entry_steam_id.pack(pady=10)

    btn_obter_info = tk.Button(root, text="Obter Informações", command=obter_informacoes, bg='#3498db', fg='white', font=("Arial", 12))
    btn_obter_info.pack(pady=10)

    btn_linkedin = tk.Button(root, text="Dev LinkedIn", command=abrir_linkedin, bg='#0077b5', fg='white', font=("Arial", 10, "italic"))
    btn_linkedin.pack(pady=5)

    btn_github = tk.Button(root, text="Dev GitHub", command=abrir_github, bg='#333333', fg='white', font=("Arial", 10, "italic"))
    btn_github.pack(pady=5)
    
    largura_janela = 500  # Ajuste conforme necessário
    altura_janela = 600  # Ajuste conforme necessário
    # Obtém as dimensões da tela
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    lbl_dev = tk.Label(root, text="@ashcrysis:", font=("Arial", 12), bg='#262626', fg='white')
    lbl_dev.pack(pady=(20, 10))  # Adicionei um espaçamento acima e abaixo
    # Calcula a posição para centralizar a janela
    x_pos = (largura_tela - largura_janela) // 2
    y_pos = (altura_tela - altura_janela) // 2

    # Define a geometria da janela principal
    root.geometry(f"{largura_janela}x{altura_janela}+{x_pos}+{y_pos}")

    root.configure(bg='#262626')  # Cor de fundo escura
    root.mainloop()

if __name__ == "__main__":
    criar_tela()