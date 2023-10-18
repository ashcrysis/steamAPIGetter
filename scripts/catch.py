import requests

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
            return personaname, personastate
        else:
            print('Erro ao obter informações do jogador.')
            return None, None
    
    except Exception as e:
        print(f'Erro: {e}')
        return None, None

def main():
    steam_id = 'USER_STEAM_ID'
    api_key = 'YOUR_API_CODE'

    # Obter informações do jogador
    personaname, personastate = obter_informacoes_jogador(steam_id, api_key)

    lista_jogos = obter_lista_jogos(steam_id, api_key)

    if lista_jogos:
        print('Lista de jogos:')

        # Separar jogos com nome disponível e não disponível
        jogos_com_nome = []
        jogos_sem_nome = []

        for jogo in lista_jogos:
            appid = jogo.get('appid', 'AppID não disponível')
            tempo_jogado_minutos = jogo.get('playtime_forever', 0)

            # Converter minutos para horas
            tempo_jogado_horas = tempo_jogado_minutos / 60

            nome_do_jogo, img_url = obter_nome_e_imagem_jogo(appid, api_key)

            if nome_do_jogo == 'Nome não disponível' or nome_do_jogo == None or nome_do_jogo == "None":
                jogos_sem_nome.append((appid, tempo_jogado_horas))
            else:
                    jogos_com_nome.append((nome_do_jogo, appid, tempo_jogado_horas))

        # Ordenar jogos com nome disponível por horas de jogo em ordem decrescente
        jogos_com_nome = sorted(jogos_com_nome, key=lambda x: x[2], reverse=True)

        print("\n\n\n\n\n")
        print(f'Informações do jogador:')
        print(f'Personal Name: {personaname}')
        personastate = mapear_persona_state(personastate)
        print(f'Persona State: {personastate}\n')

        # Imprimir jogos com nome disponível
        for jogo_com_nome in jogos_com_nome:
            
            print(f"{jogo_com_nome[0]} (AppID: {jogo_com_nome[1]}) - {jogo_com_nome[2]:.2f} horas jogadas")

        # Ordenar jogos sem nome por horas de jogo em ordem decrescente
        jogos_sem_nome = sorted(jogos_sem_nome, key=lambda x: x[1], reverse=True)

        # Imprimir jogos sem nome por último
        for jogo_sem_nome in jogos_sem_nome:
            print(f"Nome não disponível (AppID: {jogo_sem_nome[0]}) - {jogo_sem_nome[1]:.2f} horas jogadas")

if __name__ == "__main__":
    main()