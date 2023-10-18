import requests

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

def obter_nome_jogo(appid, api_key):
    url = f'http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={api_key}&appid={appid}'
    
    try:
        resposta = requests.get(url)
        dados = resposta.json()
        
        if 'game' in dados and 'gameName' in dados['game']:
            return dados['game']['gameName']
        else:
            print('Erro ao obter nome do jogo.')
            return None
    
    except Exception as e:
        print(f'Erro: {e}')
        return None

def main():
    steam_id = 'YOUR_STEAM_ID_CODE'
    api_key = 'YOUR_STEAM_API_CODE'

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

            nome_do_jogo = obter_nome_jogo(appid, api_key) or 'Nome não disponível'

            if nome_do_jogo == 'Nome não disponível':
                jogos_sem_nome.append((appid, tempo_jogado_horas))
            else:
                jogos_com_nome.append((nome_do_jogo, appid, tempo_jogado_horas))

        # Ordenar jogos com nome disponível por horas de jogo em ordem decrescente
        jogos_com_nome = sorted(jogos_com_nome, key=lambda x: x[2], reverse=True)
        jogos_sem_nome = sorted(jogos_sem_nome, key=lambda x: x[1], reverse=True)

        # Imprimir jogos com nome disponível
        for jogo_com_nome in jogos_com_nome:
            print(f"{jogo_com_nome[0]} (AppID: {jogo_com_nome[1]}) - {jogo_com_nome[2]:.2f} horas jogadas")

        # Imprimir jogos com nome não disponível por último
        for jogo_sem_nome in jogos_sem_nome:
            print(f"Nome não disponível (AppID: {jogo_sem_nome[0]}) - {jogo_sem_nome[1]:.2f} horas jogadas")

if __name__ == "__main__":
    main()
