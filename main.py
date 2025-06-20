import discord
from discord.ext import commands
from discord.ui import Button, View, Select
import random
import asyncio
import re
import json
import os
import logging
from datetime import datetime
from collections import defaultdict

TOKEN = os.environ.get(
    "DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuração de logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler('bot.log', encoding='utf-8'),
                        logging.StreamHandler()
                    ])

# Variáveis globais
partida_atual = False
jogadores = {}
vivos = set()
votos = {}
escolhas = {}
amaldicoados = {}
deforman_mortes = []
cartomante_usada = False
rodada_atual = 0
personagens_disponiveis = []
idioma_servidores = {}
historico_partidas = defaultdict(list)
rankings = defaultdict(lambda: {"diario": {}, "semanal": {}, "mensal": {}})
moedas = {}

# Arquivos de dados
RANKING_FILE = 'rankings.json'
HISTORICO_FILE = 'historico.json'
MOEDAS_FILE = 'moedas.json'

# Dicionário de idiomas
idiomas = {
    "pt": {
        "bem_vindo":
        "Bem-vindo a *Among Wizards* em Havrenna!",
        "iniciar_msg":
        "Havrenna está inquieta! Use `!entrar` nos próximos 90 segundos. Mínimo 5, máximo 12 jogadores.",
        "ajuda":
        ("Bem-vindo a *Among Wizards* em Havrenna!\n"
         "- Use `!iniciar` para começar uma partida (5-12 jogadores).\n"
         "- Use `!entrar` para se juntar antes do prazo (90 segundos).\n"
         "- Use `!comprar_personagem [nome]` para desbloquear personagens exclusivos.\n"
         "- Durante o dia, vote usando os botões enviados por DM ou com `!votar [nome]`.\n"
         "- À noite, use os botões enviados por DM para escolher suas ações.\n"
         "Digite `!rank` para ver os melhores, `!doar` para apoiar, `!lista_personagens` para ver a lista, `!historico` para ver as últimas partidas, `!como_jogar` para instruções detalhadas ou `!saldo` para ver suas moedas."
         ),
        "ping":
        "Pong! Latência: {latency}ms",
        "doar":
        ("Apoie *Among Wizards* em Havrenna!\n"
         "- **Pix**: Chave Pix: rafaelleggieri@gmail.com\n"
         "Após a doação, envie o comprovante por DM.\n"
         "Código QR para Pix: Disponível em breve. Contate o desenvolvedor para obter."
         ),
        "ja_ativa":
        "Já há uma partida de *Among Wizards* ativa em Havrenna!",
        "menos_jogadores":
        "Menos de 5 corajosos em Havrenna! A névoa se dissipa... Partida cancelada.",
        "identidades_enviadas":
        "{num_jogadores} almas enfrentam a escuridão de Havrenna! Verifique suas DMs para sua identidade secreta!",
        "vulto":
        "Um vulto surge na praça de Havrenna...",
        "morto":
        "Você está morto e não pode agir em Havrenna!",
        "espada_bloqueia":
        "A Espada das Sombras bloqueia suas ações nesta noite!",
        "amaldicoado":
        "Você está bloqueado ou amaldiçoado e não pode agir!",
        "acao_invalida":
        "Ação ou comando inválido para seu personagem!",
        "alvo_invalido":
        "Alvo inválido ou morto!",
        "curar_defesa":
        "Você usou **{acao}** em {alvo}.",
        "ataque_aleatorio":
        "Você lançou um ataque mágico em um alvo aleatório!",
        "invocar":
        "Você invocou os mortos para atacar!",
        "matar_vampiro":
        "Você escolheu drenar {alvo} na escuridão...",
        "cravar_pesas":
        "{alvo} será transformado em vampiro.",
        "salvar":
        "Você escolheu {alvo}.",
        "agua_benta":
        "Você jogou Água Benta em {alvo}.",
        "assassinar":
        "Você marcou {alvo} para a morte.",
        "visao":
        "Você viu a alma de {alvo}. Eles não podem mais te matar.",
        "escolha_sobrevivente":
        "Escolha um jogador para votar ou Cartomante",  # Atualizado para VotoSelect
        "escolha_protecao":
        "Você escolheu proteger-se contra {alvo}.",
        "amaldicoar":
        "Você amaldiçoou {alvo}. Eles morrerão em 2 noites, a menos que você caia.",
        "matar_2":
        "Você lançou uma maldição mortal em alvos aleatórios...",
        "feitico":
        "Você enfeitiçou {alvo} para {acao.lower()} {sub_alvo}.",
        "matar_deforman":
        "Você assassinou {alvo} nas sombras.",
        "espada_ativa":
        "A Espada das Sombras foi ativada! Ninguém fará escolhas por 2 noites, e você pode matar até 2 por noite.",
        "varinha":
        "Você lançou um feitiço de amor em {alvo}.",
        "ceu_azu":
        "Você transformou o céu em azul, confundindo o {alvo} para atacar aleatoriamente!",
        "magia_verdade":
        "Você revelou a identidade de {alvo} para todos!",
        "causador_caos":
        "Você espalhou o caos! Ninguém pode agir essa noite!",
        "senhor_caos":
        "Você inverteu a ação de {alvo}!",
        "chamas_vinganca":
        "Você queimou {alvo} até as cinzas!",
        "exercito_fogo":
        "Seu exército de fogo incinerou {alvo}!",
        "metamorfose":
        "Você assumiu a forma de {alvo}!",
        "prender":
        "Você prendeu {alvo} para interrogatório!",
        "fugir":
        "Você fugiu do ataque de {alvo}!",
        "contra_atacar":
        "Você contra-atacou {alvo} em uma luta épica!",
        "atirar":
        "Você disparou contra {alvo}!",
        "flechada":
        "Você atirou uma flecha em {alvo}!",
        "flecha_escuridao":
        "Você bloqueou {alvo} com uma flecha das sombras!",
        "flecha_mortal":
        "Você matou {alvo} e ele atacou outro aleatoriamente!",
        "hipnotizar":
        "Você hipnotizou {alvo} para matar {sub_alvo} na próxima rodada!",
        "revelacao":
        "Você forçou {alvo} a revelar sua identidade!",
        "puxar_pes":
        "Você puxou os pés de {alvo}, paralisando-o por 2 rodadas!",
        "assumir_controle":
        "Você assumiu as habilidades de {alvo}!",
        "chuva":
        "Você invocou uma chuva intensa, bloqueando {alvo}!",
        "afogar":
        "Você afogou {alvo}!",
        "observar":
        "Você revelou todas as identidades, mas a sua também foi exposta!",
        "arrancar_cabecas":
        "Você arrancou a cabeça de {alvo}!",
        "arranhar":
        "Você arranhou {alvo}, infectando-o!",
        "cartomante_usada":
        "A Cartomante já foi convocada ou a partida não está ativa!",
        "clamar_cartomante":
        "Um jogador clama pela Cartomante em Havrenna...",
        "sem_ranking":
        "Nenhum ranking registrado em Havrenna ainda!",
        "ranking_msg":
        "**Ranking de Havrenna**\nDiário:\n{ranking_diario}\n\nSemanal:\n{ranking_semanal}\n\nMensal:\n{ranking_mensal}\nRecompensas: 100 moedas (semanal), 400 moedas (mensal)",
        "caçador_almas":
        "{nome} foi consumido pelo Caçador de Almas por perturbar Havrenna!",
        "noite_assustadora":
        "A noite {rodada_atual} foi assustadora em Havrenna. Muito sangue e morte. Parece que {assassinos} fizeram suas vítimas...\n{narrativa_mortes}",
        "noite_silenciosa":
        "A noite {rodada_atual} foi silenciosa em Havrenna... Mas a névoa ainda esconde segredos.",
        "badernista_vence":
        "O Badernista ({nome_jogador}) ri ao ser levado à forca! **Badernista vence *Among Wizards*!**",
        "enforcado":
        "{personagem} ({nome_jogador}) foi enforcado na praça de Havrenna...",
        "vitoria_unica":
        "{personagem} ({nome_jogador}) é o último em Havrenna! **Vence *Among Wizards*!**",
        "vitoria_fada":
        "A Fada ({nome_jogador}) distribui abraços e beijos aos caídos de Havrenna, espalhando luz na névoa!",
        "sem_vencedores":
        "Havrenna está vazia... *Among Wizards* termina sem vencedores.",
        "vitoria_vidente":
        "A Vidente ({nome_jogador}) desvendou todos os segredos! **Vidente vence *Among Wizards*!**",
        "vitoria_carcereiro":
        "O Carcereiro ({nome_jogador}) identificou todos os vilões! **Carcereiro vence *Among Wizards*!**",
        "vitoria_criatura":
        "A Criatura ({nome_jogador}) sobreviveu ou lutou até o fim! **Criatura vence *Among Wizards*!**",
        "empate":
        "Havrenna não suporta mais a névoa... *Among Wizards* termina em empate!",
        "bebado_cambaleia":
        "O Bêbado ({nome_jogador}) cambaleia pelas ruas de Havrenna, murmurando sobre a névoa...",
        "setlanguage_success":
        "Idioma alterado para {lang} com sucesso!",
        "setlanguage_invalid":
        "Idioma inválido! Use 'pt' para português ou 'en' para inglês.",
        "personagens_title":
        "**Lista de Personagens de Havrenna**\n",
        "historico_title":
        "**Histórico das Últimas 20 Partidas em {servidor}**\n",
        "sem_historico":
        "Nenhum histórico de partidas registrado neste servidor ainda!",
        "como_jogar_parte1":
        ("**Como Jogar Among Wizards em Havrenna**\n"
         "*Among Wizards* é um jogo de estratégia e mistério onde jogadores assumem papéis secretos em uma vila mágica chamada Havrenna. O objetivo varia conforme seu personagem: eliminar inimigos, sobreviver, ou alcançar condições específicas de vitória.\n\n"
         "**Como Jogar:**\n"
         "1. **Iniciar a Partida**: Use `!iniciar` para começar uma partida. Requer 5 a 12 jogadores, que têm 90 segundos para entrar com `!entrar`.\n"
         "2. **Entrar na Partida**: Use `!entrar` para se juntar. Você receberá um personagem aleatório (padrão ou exclusivo, se desbloqueado) via DM.\n"
         "3. **Comprar Personagens**: Use `!comprar_personagem [nome]` para desbloquear personagens exclusivos (50-500 moedas), que entram no seu pool de personagens aleatórios.\n"
         "4. **Fase do Dia**: Durante o dia (90 segundos), vote em um jogador para a forca ou convoque a Cartomante usando os botões enviados por DM. Alternativamente, use `!votar [nome]` ou `!convocar_cartomante`.\n"
         ),
        "como_jogar_parte2":
        ("5. **Fase da Noite**: À noite (90 segundos), use os botões enviados por DM para selecionar suas ações e alvos.\n"
         "6. **Moedas e Recompensas**:\n"
         "   - **Participar da Partida**: 10 moedas.\n"
         "   - **Vencedor da Partida**: 50 moedas.\n"
         "   - **Ranking Semanal**: 100 moedas para o topo.\n"
         "   - **Ranking Mensal**: 400 moedas para o topo.\n"
         "   Use `!saldo` para verificar suas moedas e personagens desbloqueados.\n"
         "7. **Objetivos**: Cada personagem tem objetivos únicos (ex.: Vidente revela identidades, Badernista vence na forca). Leia sua DM para detalhes.\n"
         "8. **Vitória**: A partida termina quando um jogador atinge sua condição de vitória, ou após 10 rodadas (empate). Apenas um jogador vence!\n\n"
         "**Comandos Disponíveis:**\n"
         "- `!iniciar`: Inicia a partida.\n"
         "- `!entrar`: Entra na partida com um personagem aleatório.\n"
         "- `!comprar_personagem [nome]`: Compra um personagem exclusivo.\n"
         "- `!votar [nome]`: Vota para enforcar alguém (alternativa aos botões).\n"
         "- `!convocar_cartomante`: Convoca a Cartomante (alternativa aos botões).\n"
         "- `!rank`: Mostra os rankings diário, semanal e mensal.\n"
         "- `!historico`: Exibe o histórico das últimas 20 partidas.\n"
         "- `!lista_personagens`: Lista todos os personagens e suas habilidades.\n"
         "- `!como_jogar`: Mostra estas instruções.\n"
         "- `!saldo`: Verifica suas moedas e personagens desbloqueados.\n"
         "- `!doar`: Informações para apoiar o jogo.\n"
         "- `!ping`: Verifica a latência do bot.\n"
         "- `!setlanguage [pt/en]`: Define o idioma do servidor.\n\n"
         "**Dicas**:\n"
         "- Mantenha sua identidade secreta!\n"
         "- Evite linguagem inadequada ou excesso de palavras para não ser penalizado pelo Caçador de Almas.\n"
         "- Use os botões nas DMs para ações rápidas e precisas.\n"
         "Divirta-se na névoa de Havrenna!"),
        "saldo":
        "**Seu Saldo em Havrenna**\nMoedas: {moedas}\nPersonagens Exclusivos Desbloqueados: {personagens}\nUse `!comprar_personagem [nome]` para desbloquear personagens exclusivos e incluí-los no seu pool aleatório.",
        "sem_personagens_exclusivos":
        "Não há personagens exclusivos disponíveis para compra!",
        "personagens_exclusivos_disponiveis":
        "Personagens exclusivos disponíveis:\n{exclusivos}",
        "personagem_nao_exclusivo":
        "Este personagem não é exclusivo!",
        "personagem_ja_comprado":
        "Você já possui este personagem!",
        "moedas_insuficientes":
        "Moedas insuficientes! Você precisa de {custo} moedas.",
        "personagem_comprado":
        "Personagem {personagem} comprado por {custo} moedas!"
    },
    "en": {
        "bem_vindo":
        "Welcome to *Among Wizards* in Havrenna!",
        "iniciar_msg":
        "Havrenna is restless today. It seems the night will bring horrors... Use `!entrar` in the next 90 seconds. Minimum 5, maximum 12 players.",
        "ajuda":
        ("Welcome to *Among Wizards* in Havrenna!\n"
         "- Use `!iniciar` to start a game (5-12 players).\n"
         "- Use `!entrar` to join before the deadline (90 seconds).\n"
         "- Use `!comprar_personagem [name]` to unlock exclusive characters.\n"
         "- During the day, vote using buttons sent via DM or with `!votar [name]`.\n"
         "- At night, use buttons sent via DM to choose your actions.\n"
         "Type `!rank` to see the best players, `!doar` to support, `!lista_personagens` for the character list, `!historico` for recent games, `!como_jogar` for detailed instructions, or `!saldo` to check your coins."
         ),
        "ping":
        "Pong! Latency: {latency}ms",
        "doar":
        ("Support *Among Wizards* in Havrenna!\n"
         "- **Pix**: Pix Key: rafaelleggieri@gmail.com\n"
         "After donating, send proof via DM.\n"
         "QR Code for Pix: Available soon. Contact the developer to obtain."),
        "ja_ativa":
        "A game of *Among Wizards* is already active in Havrenna!",
        "menos_jogadores":
        "Fewer than 5 brave souls in Havrenna! The fog clears... Game canceled.",
        "identidades_enviadas":
        "{num_jogadores} souls face the darkness of Havrenna! Check your DMs for your secret identity!",
        "vulto":
        "A shadowy figure appears in Havrenna's square...",
        "morto":
        "You are dead and cannot act in Havrenna!",
        "espada_bloqueia":
        "The Shadow Sword blocks your actions tonight!",
        "amaldicoado":
        "You are blocked or cursed and cannot act!",
        "acao_invalida":
        "Invalid action or command for your character!",
        "alvo_invalido":
        "Invalid or dead target!",
        "curar_defesa":
        "You used **{acao}** on {alvo}.",
        "ataque_aleatorio":
        "You cast a magical attack on a random target!",
        "invocar":
        "You summoned the dead to attack!",
        "matar_vampiro":
        "You chose to drain {alvo} in the darkness...",
        "cravar_pesas":
        "{alvo} will be turned into a vampire.",
        "salvar":
        "You chose {alvo}.",
        "agua_benta":
        "You threw Holy Water on {alvo}.",
        "assassinar":
        "You marked {alvo} for death.",
        "visao":
        "You saw the soul of {alvo}. They can no longer kill you.",
        "escolha_sobrevivente":
        "Choose a player to vote for or summon the Cartomante",  # Adicionado para VotoSelect
        "escolha_acao":
        "Choose your action and target",  # Já presente
        "escolha_protecao":
        "You chose to protect yourself against {alvo}.",
        "amaldicoar":
        "You cursed {alvo}. They will die in 2 nights unless you fall.",
        "matar_2":
        "You cast a deadly curse on random targets...",
        "feitico":
        "You enchanted {alvo} to {acao.lower()} {sub_alvo}.",
        "matar_deforman":
        "You assassinated {alvo} in the shadows.",
        "espada_ativa":
        "The Shadow Sword was activated! No one can make choices for 2 nights, and you can kill up to 2 per night.",
        "varinha":
        "You cast a love spell on {alvo}.",
        "ceu_azu":
        "You turned the sky blue, confusing {alvo} to attack randomly!",
        "magia_verdade":
        "You revealed {alvo}'s identity to everyone!",
        "causador_caos":
        "You spread chaos! No one can act tonight!",
        "senhor_caos":
        "You reversed {alvo}'s action!",
        "chamas_vinganca":
        "You burned {alvo} to ashes!",
        "exercito_fogo":
        "Your fire army incinerated {alvo}!",
        "metamorfose":
        "You took the form of {alvo}!",
        "prender":
        "You imprisoned {alvo} for interrogation!",
        "fugir":
        "You escaped the attack from {alvo}!",
        "contra_atacar":
        "You counterattacked {alvo} in an epic fight!",
        "atirar":
        "You shot at {alvo}!",
        "flechada":
        "You shot an arrow at {alvo}!",
        "flecha_escuridao":
        "You blocked {alvo} with a shadow arrow!",
        "flecha_mortal":
        "You killed {alvo}, and they attacked another randomly!",
        "hipnotizar":
        "You hypnotized {alvo} to kill {sub_alvo} next round!",
        "revelacao":
        "You forced {alvo} to reveal their identity!",
        "puxar_pes":
        "You pulled {alvo}'s feet, paralyzing them for 2 rounds!",
        "assumir_controle":
        "You took control of {alvo}'s abilities!",
        "chuva":
        "You summoned a heavy rain, blocking {alvo}!",
        "afogar":
        "You drowned {alvo}!",
        "observar":
        "You revealed all identities, but yours was exposed too!",
        "arrancar_cabecas":
        "You tore off {alvo}'s head!",
        "arranhar":
        "You scratched {alvo}, infecting them!",
        "cartomante_usada":
        "The Cartomante has already been summoned or the game is not active!",
        "clamar_cartomante":
        "A player calls to summon the Cartomante in Havrenna...",
        "sem_ranking":
        "No rankings registered in Havrenna yet!",
        "ranking_msg":
        "**Havrenna Rankings**\nDaily:\n{ranking_diario}\n\nWeekly:\n{ranking_semanal}\n\nMonthly:\n{ranking_mensal}\nRewards: 100 coins (weekly), 400 coins (monthly)",
        "caçador_almas":
        "{nome} was consumed by the Soul Hunter for disturbing Havrenna!",
        "noite_assustadora":
        "Night {rodada_atual} was terrifying in Havrenna. Much blood and death. It seems {assassinos} made their victims...\n{narrativa_mortes}",
        "noite_silenciosa":
        "Night {rodada_atual} was silent in Havrenna... But the fog still hides secrets.",
        "badernista_vence":
        "The Troublemaker ({nome_jogador}) laughs as they’re led to the gallows! **Troublemaker wins *Among Wizards*!**",
        "enforcado":
        "{personagem} ({nome_jogador}) was hanged in Havrenna's square...",
        "vitoria_unica":
        "{personagem} ({nome_jogador}) is the last standing in Havrenna! **Wins *Among Wizards*!**",
        "vitoria_fada":
        "The Fairy ({nome_jogador}) spreads hugs and kisses to Havrenna’s fallen, bringing light to the fog!",
        "sem_vencedores":
        "Havrenna is empty... *Among Wizards* ends without a winner.",
        "vitoria_vidente":
        "The Seer ({nome_jogador}) unraveled all secrets! **Seer wins *Among Wizards*!**",
        "vitoria_carcereiro":
        "The Jailor ({nome_jogador}) identified all villains! **Jailor wins *Among Wizards*!**",
        "vitoria_criatura":
        "The Creature ({nome_jogador}) survived or fought to the end! **Creature wins *Among Wizards*!**",
        "empate":
        "Havrenna can no longer bear the fog... *Among Wizards* ends in a tie!",
        "bebado_cambaleia":
        "The Drunk ({nome_jogador}) stumbles through Havrenna’s streets, muttering about the fog...",
        "setlanguage_success":
        "Language changed to {lang} successfully!",
        "setlanguage_invalid":
        "Invalid language! Use 'pt' for Portuguese or 'en' for English.",
        "personagens_title":
        "**List of Havrenna Characters**\n",
        "historico_title":
        "**History of the Last 20 Games in {servidor}**\n",
        "sem_historico":
        "No game history recorded for this server yet!",
        "como_jogar_parte1":
        ("**How to Play Among Wizards in Havrenna**\n"
         "*Among Wizards* is a strategy and mystery game where players take on secret roles in a magical village called Havrenna. The objective varies by character: eliminate enemies, survive, or achieve specific victory conditions.\n\n"
         "**How to Play:**\n"
         "1. **Start a Game**: Use `!iniciar` to begin a game. Requires 5 to 12 players, who have 90 seconds to join with `!entrar`.\n"
         "2. **Join the Game**: Use `!entrar` to join. You’ll receive a random character (standard or exclusive, if unlocked) via DM.\n"
         "3. **Buy Characters**: Use `!comprar_personagem [name]` to unlock exclusive characters (50-500 coins), which are added to your random character pool.\n"
         "4. **Day Phase**: During the day (90 seconds), vote for a player to be hanged or summon the Cartomante using buttons sent via DM. Alternatively, use `!votar [name]` or `!convocar_cartomante`.\n"
         ),
        "como_jogar_parte2":
        ("5. **Night Phase**: At night (90 seconds), use buttons sent via DM to select your actions and targets.\n"
         "6. **Coins and Rewards**:\n"
         "   - **Join a Game**: 10 coins.\n"
         "   - **Win a Game**: 50 coins.\n"
         "   - **Weekly Ranking**: 100 coins for the top.\n"
         "   - **Monthly Ranking**: 400 coins for the top.\n"
         "   Use `!saldo` to check your coins and unlocked characters.\n"
         "7. **Objectives**: Each character has unique goals (e.g., Seer reveals identities, Troublemaker wins by being hanged). Read your DM for details.\n"
         "8. **Victory**: The game ends when a player achieves their victory condition, or after 10 rounds (tie). Only one player wins!\n\n"
         "**Available Commands:**\n"
         "- `!iniciar`: Starts the game.\n"
         "- `!entrar`: Joins the game with a random character.\n"
         "- `!comprar_personagem [name]`: Buys an exclusive character.\n"
         "- `!votar [name]`: Votes to hang someone (alternative to buttons).\n"
         "- `!convocar_cartomante`: Summons the Cartomante (alternative to buttons).\n"
         "- `!rank`: Shows daily, weekly, and monthly rankings.\n"
         "- `!historico`: Displays the history of the last 20 games.\n"
         "- `!lista_personagens`: Lists all characters and their abilities.\n"
         "- `!como_jogar`: Shows these instructions.\n"
         "- `!saldo`: Checks your coins and unlocked characters.\n"
         "- `!doar`: Information to support the game.\n"
         "- `!ping`: Checks the bot’s latency.\n"
         "- `!setlanguage [pt/en]`: Sets the server’s language.\n\n"
         "**Tips**:\n"
         "- Keep your identity secret!\n"
         "- Avoid inappropriate language or excessive chatter to avoid penalties from the Soul Hunter.\n"
         "- Use DM buttons for quick and accurate actions.\n"
         "Enjoy the fog of Havrenna!"),
        "saldo":
        "**Your Balance in Havrenna**\nCoins: {moedas}\nUnlocked Exclusive Characters: {personagens}\nUse `!comprar_personagem [name]` to unlock exclusive characters and add them to your random pool.",
        "sem_personagens_exclusivos":
        "No exclusive characters available for purchase!",
        "personagens_exclusivos_disponiveis":
        "Available exclusive characters:\n{exclusivos}",
        "personagem_nao_exclusivo":
        "This character is not exclusive!",
        "personagem_ja_comprado":
        "You already own this character!",
        "moedas_insuficientes":
        "Insufficient coins! You need {custo} coins.",
        "personagem_comprado":
        "Character {personagem} purchased for {custo} coins!"
    }
}


# Função para detectar idioma
def detectar_idioma(ctx):
    return idioma_servidores.get(ctx.guild.id, "pt")


# Função para salvar dados
def salvar_dados(data, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Erro ao salvar {filename}: {e}")


# Função para carregar dados
def carregar_dados(filename, default):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
    except Exception as e:
        logging.error(f"Erro ao carregar {filename}: {e}")
        return default


# Carregar dados iniciais
rankings = carregar_dados(
    RANKING_FILE,
    defaultdict(lambda: {
        "diario": {},
        "semanal": {},
        "mensal": {}
    }))
historico_partidas = carregar_dados(HISTORICO_FILE, defaultdict(list))
moedas = carregar_dados(MOEDAS_FILE, {})

# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Carregar histórico
historico_partes = carregar_dados(HISTORICO_FILE, defaultdict(list))

# Carregar moedas
moedas = carregar_dados(MOEDAS_FILE, {})


# Função para detectar idioma
def detectar_idioma(ctx):
    if isinstance(ctx, discord.Message):
        ctx = ctx.channel
    if isinstance(ctx, discord.TextChannel):
        if ctx.guild.id in idioma_servidores:
            return idioma_servidores[ctx.guild.id]
        return "pt"
    return "pt"


idioma_servidores = {}  # {guild_id: idioma}

# Estado do jogo
jogadores = {
}  # {id: {personagem, jogador_id, escolhas, aliados, nome_jogador, ...}}
vivos = set()  # IDs dos jogadores vivos
votos = {}  # {id: voto_id}
escolhas = {}  # {id: (acao, escolha)}
cartomante_usada = False
partida_atual = False
personagens_jogaveis = [
    "Mago Branco", "Mago Reverso", "Aldeão", "Bêbado", "Fazendeiro",
    "Badernista", "Vampiro", "Médico", "Padre", "Assassino", "Vidente",
    "Sobrevivente"
]
personagens_exclusivos = {
    "Bruxa": 50,
    "Feiticeira": 50,
    "Deforman": 50,
    "Fada": 50,
    "Lobisomem": 50,
    "Segurança": 50,
    "Mago Vermelho": 50,
    "Mago Azul": 50,
    "Agente do Caos": 50,
    "Garota Infernal": 50,
    "Mutante": 50,
    "Carcereiro": 50,
    "Criatura": 50,
    "Pistoleiro": 50,
    "Arqueira": 50,
    "Arqueiro das Sombras": 50,
    "Hipnotizador": 500,
    "Bicho Papão": 50,
    "Fantasma": 200,
    "Senhor da Chuva": 50,
    "Observador": 30
}
personagens_disponiveis = []
amaldicoados = {}  # {id: rodadas_restantes}
deforman_mortes = {}  # {id: escolha_morte}
rodada_atual = 0
espada_ativa = 0  # Contador para Espada das Sombras
historico_partidas = defaultdict(
    list)  # {guild_id: [(data, vencedor, jogadores_vivos), ...]}
moedas = {}  # {id: {moedas, personagens_desbloqueados}}

# Configuração dos personagens
personagens = {
    "Mago Branco": {
        "habilidades": ["Curar", "Defesa"],
        "tipo": "bom",
        "exclusivo": False,
        "vitoria": "Sobreviver e eliminar todos os personagens malignos.",
        "historia": "Um ancião sábio que protege com magia branca.",
        "forca": "Cura aliados.",
        "fraqueza": "Vulnerável sem aliados."
    },
    "Mago Reverso": {
        "habilidades": ["Atacar", "Invocar"],
        "tipo": "mau",
        "exclusivo": False,
        "vitoria": "Eliminar todos os jogadores bons.",
        "historia": "Um mago que abraçou a escuridão.",
        "forca": "Ataques imprevisíveis.",
        "fraqueza": "Dependência de poderes."
    },
    "Aldeão": {
        "habilidades": [],
        "tipo": "bom",
        "exclusivo": False,
        "vitoria": "Sobreviver até o final.",
        "historia": "Um simples morador de Havrenna.",
        "forca": "Inocência.",
        "fraqueza": "Sem habilidades."
    },
    "Bêbado": {
        "habilidades": [],
        "tipo": "neutro",
        "exclusivo": False,
        "vitoria": "Sobreviver até o final.",
        "historia": "Um bebedor que se arrasta por Havrenna.",
        "forca": "Imprevisibilidade.",
        "fraqueza": "Sem controle."
    },
    "Fazendeiro": {
        "habilidades": ["Salvar"],
        "tipo": "bom",
        "exclusivo": False,
        "vitoria": "Proteger pelo menos 3 jogadores de ataques.",
        "historia": "Um protetor da vila com coração puro.",
        "forca": "Proteção.",
        "fraqueza": "Sem ataque."
    },
    "Badernista": {
        "habilidades": [],
        "tipo": "mau",
        "exclusivo": False,
        "vitoria": "Ser enforcado na praça.",
        "historia": "Um causador de caos que deseja a forca.",
        "forca": "Vence na derrota.",
        "fraqueza": "Sem ações."
    },
    "Vampiro": {
        "habilidades": ["Matar", "Cravar Presas"],
        "tipo": "mau",
        "exclusivo": False,
        "vitoria": "Transformar ou matar 3 jogadores.",
        "historia": "Um predador noturno sedento por sangue.",
        "forca": "Conversão de aliados.",
        "fraqueza": "Vulnerável à Água Benta."
    },
    "Médico": {
        "habilidades": ["Curar"],
        "tipo": "bom",
        "exclusivo": False,
        "vitoria": "Curar pelo menos 3 jogadores de ataques.",
        "historia": "Um curandeiro habilidoso.",
        "forca": "Cura poderosa.",
        "fraqueza": "Sem ataque."
    },
    "Padre": {
        "habilidades": ["Água Benta"],
        "tipo": "bom",
        "exclusivo": False,
        "vitoria": "Eliminar todos os vampiros.",
        "historia": "Um clérigo que purifica a escuridão.",
        "forca": "Anti-vampiros.",
        "fraqueza": "Limitado contra outros."
    },
    "Assassino": {
        "habilidades": ["Assassinar"],
        "tipo": "mau",
        "exclusivo": False,
        "vitoria": "Eliminar 3 jogadores.",
        "historia": "Um matador nas sombras.",
        "forca": "Ataques precisos.",
        "fraqueza": "Sem defesa."
    },
    "Vidente": {
        "habilidades": ["Visão"],
        "tipo": "bom",
        "exclusivo": False,
        "vitoria": "Revelar a identidade de todos os jogadores vivos.",
        "historia": "Um sábio que vê através da névoa.",
        "forca": "Conhecimento.",
        "fraqueza": "Vulnerável após revelar."
    },
    "Sobrevivente": {
        "habilidades": ["Escolha"],
        "tipo": "neutro",
        "exclusivo": False,
        "vitoria": "Ser um dos últimos 3 vivos.",
        "historia": "Um resistente que luta para sobreviver.",
        "forca": "Resiliência.",
        "fraqueza": "Sem ataque direto."
    },
    "Bruxa": {
        "habilidades": ["Amaldiçoar", "Matar 2"],
        "tipo": "mau",
        "exclusivo": True,
        "custo": 50,
        "vitoria": "Matar 3 inimigos com maldições.",
        "historia": "Uma feiticeira que manipula a morte.",
        "forca": "Maldições letais.",
        "fraqueza": "Vulnerável se descoberta."
    },
    "Feiticeira": {
        "habilidades": ["Feitiço"],
        "tipo": "mau",
        "exclusivo": True,
        "custo": 50,
        "vitoria": "Controlar 2 jogadores para matar outros.",
        "historia": "Uma manipuladora de vontades.",
        "forca": "Controle mental.",
        "fraqueza": "Sem ataque direto."
    },
    "Deforman": {
        "habilidades": ["Matar", "Espada das Sombras"],
        "tipo": "mau",
        "exclusivo": True,
        "custo": 50,
        "vitoria": "Matar 4 jogadores com a Espada das Sombras ou ataques.",
        "historia": "Um ser sombrio com uma espada amaldiçoada.",
        "forca": "Bloqueio e ataque.",
        "fraqueza": "Espada limitada."
    },
    "Fada": {
        "habilidades": ["Varinha"],
        "tipo": "bom",
        "exclusivo": True,
        "custo": 50,
        "vitoria": "Sobreviver como o último jogador.",
        "historia": "Uma criatura mágica que espalha amor.",
        "forca": "Voto duplo após 3 rodadas.",
        "fraqueza": "Sem ataque."
    },
    "Lobisomem": {
        "habilidades": ["Arrancar Cabeças", "Arranhar"],
        "tipo": "mau",
        "exclusivo": True,
        "custo": 50,
        "vitoria": "Ter 3 aliados ou matar 3 jogadores.",
        "historia": "Uma fera que uiva na lua cheia.",
        "forca": "Ataques brutais.",
        "fraqueza": "Vulnerável fora da lua."
    },
    "Segurança": {
        "habilidades": ["Proteger"],
        "tipo": "bom",
        "exclusivo": True,
        "custo": 50,
        "vitoria": "Proteger 3 jogadores de ataques.",
        "historia": "Um guardião leal de Havrenna.",
        "forca": "Defesa poderosa.",
        "fraqueza": "Sem ataque."
    },
    "Mago Vermelho": {
        "habilidades": ["Petrificar", "Regeneração"],
        "tipo": "neutro",
        "exclusivo": True,
        "custo": 50,
        "vitoria": "Sobreviver usando Regeneração pelo menos uma vez.",
        "historia": "Um mago que manipula pedra e cura.",
        "forca": "Defesa e bloqueio.",
        "fraqueza": "Regeneração limitada."
    },
    "Mago Azul": {
        "habilidades": ["Céu Azul", "Magia da Verdade"],
        "tipo": "neutro",
        "exclusivo": True,
        "custo": 50,
        "vitoria":
        "Sobreviver até o final e revelar pelo menos uma identidade.",
        "historia": "Um mago que manipula o céu e a verdade.",
        "forca": "Confunde e revela.",
        "fraqueza": "Sem ataque direto."
    },
    "Agente do Caos": {
        "habilidades": ["Causador de Caos", "Senhor do Caos"],
        "tipo": "mau",
        "exclusivo": True,
        "custo": 50,
        "vitoria": "Causar pelo menos 3 mortes via caos ou inversão de ações.",
        "historia": "Um mestre do caos que semeia destruição.",
        "forca": "Manipula ações.",
        "fraqueza": "Requer tempo para carregar."
    },
    "Garota Infernal": {
        "habilidades": ["Chamas da Vingança", "Exército de Fogo"],
        "tipo": "mau",
        "exclusivo": True,
        "custo": 50,
        "vitoria": "Eliminar pelo menos 4 jogadores com fogo.",
        "historia": "Uma mulher que controla chamas vingativas.",
        "forca": "Ataques devastadores.",
        "fraqueza": "Sem defesas."
    },
    "Mutante": {
        "habilidades": ["Metamorfose"],
        "tipo": "neutro",
        "exclusivo": True,
        "custo": 50,
        "vitoria": "Matar pelo menos 2 jogadores via metamorfose.",
        "historia": "Um ser que assume a forma de outros.",
        "forca": "Confunde atacantes.",
        "fraqueza": "Morre em contra-ataques."
    },
    "Carcereiro": {
        "habilidades": ["Prender"],
        "tipo": "bom",
        "exclusivo": True,
        "custo": 50,
        "vitoria": "Identificar e matar todos os jogadores malignos.",
        "historia": "Um guardião que interroga nas sombras.",
        "forca": "Identifica vilões.",
        "fraqueza": "Morre ao matar inocentes."
    },
    "Criatura": {
        "habilidades": ["Fugir", "Contra-atacar"],
        "tipo": "neutro",
        "exclusivo": True,
        "custo": 50,
        "vitoria":
        "Vencer via Contra-atacar em um 1v1 ou sobreviver com 3 fugas.",
        "historia": "Uma besta esquiva que luta até a morte.",
        "forca": "Sobrevivência.",
        "fraqueza": "Vulnerável em grupos."
    },
    "Pistoleiro": {
        "habilidades": ["Atirar"],
        "tipo": "neutro",
        "exclusivo": True,
        "custo": 50,
        "vitoria": "Matar pelo menos 2 jogadores com tiros.",
        "historia": "Um atirador preciso que age à luz do dia.",
        "forca": "Ataques diurnos.",
        "fraqueza": "Tiros limitados."
    },
    "Arqueira": {
        "habilidades": ["Flechada"],
        "tipo": "neutro",
        "exclusivo": True,
        "custo": 50,
        "vitoria": "Matar pelo menos 2 jogadores com flechas.",
        "historia": "Uma arqueira habilidosa com precisão mortal.",
        "forca": "Ataques aleatórios.",
        "fraqueza": "Chance de falha."
    },
    "Arqueiro das Sombras": {
        "habilidades": ["Flecha da Escuridão", "Flecha Mortal"],
        "tipo": "mau",
        "exclusivo": True,
        "custo": 50,
        "vitoria": "Causar 3 mortes via Flecha Mortal ou bloquear 3 ações.",
        "historia": "Um arqueiro que ataca nas sombras.",
        "forca": "Bloqueia e mata.",
        "fraqueza": "Habilidade única limitada."
    },
    "Hipnotizador": {
        "habilidades": ["Hipnotizar", "Revelação"],
        "tipo": "neutro",
        "exclusivo": True,
        "custo": 500,
        "vitoria": "Causar 2 mortes via hipnose ou manipulação.",
        "historia": "Um manipulador que controla mentes.",
        "forca": "Manipulação letal.",
        "fraqueza": "Requer planejamento."
    },
    "Bicho Papão": {
        "habilidades": ["Puxar os Pés"],
        "tipo": "mau",
        "exclusivo": True,
        "custo": 50,
        "vitoria": "Bloquear 4 ações ou matar 2 personagens sem ação.",
        "historia": "Uma entidade que aterroriza na noite.",
        "forca": "Paralisa inimigos.",
        "fraqueza": "Sem ataque direto."
    },
    "Fantasma": {
        "habilidades": ["Assumir Controle"],
        "tipo": "neutro",
        "exclusivo": True,
        "custo": 200,
        "vitoria": "Usar 3 habilidades diferentes para causar 2 mortes.",
        "historia": "Um espírito que imita os vivos.",
        "forca": "Versatilidade.",
        "fraqueza": "Sem identidade própria."
    },
    "Senhor da Chuva": {
        "habilidades": ["Chuva", "Afogar"],
        "tipo": "neutro",
        "exclusivo": True,
        "custo": 50,
        "vitoria":
        "Matar 2 jogadores com Afogar ou bloquear 4 ações com Chuva.",
        "historia": "Um mago que controla as águas.",
        "forca": "Controle climático.",
        "fraqueza": "Ataques limitados."
    },
    "Observador": {
        "habilidades": ["Observar"],
        "tipo": "neutro",
        "exclusivo": True,
        "custo": 30,
        "vitoria": "Sobreviver após revelar todas as identidades.",
        "historia": "Um espião que vê tudo, mas é visto.",
        "forca": "Revelação total.",
        "fraqueza": "Exposição ao usar."
    }
}


# Funções para carregar e salvar dados
def carregar_dados():
    rankings = {}
    historico = {}
    moedas_data = {}
    for file, default in [(RANKING_FILE, {}), (HISTORICO_FILE, {}),
                          (MOEDAS_FILE, {})]:
        try:
            if not os.path.exists(file):
                with open(file, 'w', encoding='utf-8') as f:
                    json.dump(default, f, ensure_ascii=False)
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if file == RANKING_FILE:
                    rankings = data
                elif file == HISTORICO_FILE:
                    historico = data
                elif file == MOEDAS_FILE:
                    moedas_data = data
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logging.error(
                f"Erro ao carregar {file}: {e}. Redefinindo para o padrão.")
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(default, f, ensure_ascii=False)
    return rankings, historico, moedas_data


def salvar_dados(rankings, historico, moedas_data):
    try:
        with open(RANKING_FILE, 'w', encoding='utf-8') as f:
            json.dump(rankings, f, indent=4, ensure_ascii=False)
        with open(HISTORICO_FILE, 'w', encoding='utf-8') as f:
            json.dump(historico, f, indent=4, ensure_ascii=False)
        with open(MOEDAS_FILE, 'w', encoding='utf-8') as f:
            json.dump(moedas_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Erro ao salvar dados: {e}")


rankings, historico_partidas, moedas = carregar_dados()


# Classes para botões interativos
# Classes para botões interativos
class VotoSelect(View):

    def __init__(self, players, idioma_id):
        super().__init__(timeout=90)
        self.players = players
        options = [
            discord.SelectOption(label=jogadores[p]["nome_jogador"],
                                 value=str(p)) for p in players
            if jogadores[p]["vivo"]
        ]
        options.append(
            discord.SelectOption(label="Cartomante", value="Cartomante"))
        select = discord.ui.Select(
            placeholder=idiomas[idioma_id]["escolha_sobrevivente"],
            options=options)
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction, select):
        global votos
        selected = select.values[0]
        if selected == "Cartomante":
            votos[interaction.user.id] = "Cartomante"
            await interaction.response.send_message(
                "Você votou para convocar a Cartomante!", ephemeral=True)
        else:
            votos[interaction.user.id] = int(selected)
            target_name = jogadores[int(selected)]["nome_jogador"]
            await interaction.response.send_message(
                f"Você votou em {target_name} para a forca!", ephemeral=True)
        if rodada_atual >= 3 and jogadores[
                interaction.user.id]["personagem"] == "Fada":
            votos[
                f"{interaction.user.id}_extra"] = selected if selected == "Cartomante" else int(
                    selected)
            await interaction.followup.send(
                "Como Fada, seu voto extra foi registrado!", ephemeral=True)


class AcaoSelecao(View):

    def __init__(self, jogador_id, habilidades, alvos, idioma_id):
        super().__init__(timeout=120)
        self.jogador_id = str(jogador_id)
        options = [
            discord.SelectOption(
                label=f"{hab} ({jogadores[t]['nome_jogador']})",
                value=f"{hab} {t}") for hab in habilidades for t in alvos
            if jogadores[t]["vivo"]
        ]
        if not options:
            options.append(
                discord.SelectOption(label="Nenhuma ação", value="Nenhuma"))
        select = discord.ui.Select(
            placeholder=idiomas[idioma_id]["escolha_acao"], options=options)
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction, select):
        global escolhas
        if select.values[0] == "Nenhuma":
            await interaction.response.send_message(
                "Nenhuma ação selecionada.", ephemeral=True)
            return
        hab, alvo_id = select.values[0].split(" ")
        escolhas[int(self.jogador_id)] = (hab, int(alvo_id))
        alvo_name = jogadores[int(alvo_id)]["nome_jogador"]
        await interaction.response.send_message(
            f"Você escolheu {hab} em {alvo_name}!", ephemeral=True)


# Evento de inicialização
@bot.event
async def on_ready():
    logging.info(
        f'Bot Among Wizards conectado como {bot.user} em {discord.utils.utcnow()}'
    )
    await bot.change_presence(activity=discord.Game(
        name="Among Wizards | !ajuda"))


# Tratamento de erros de comando
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        idioma = detectar_idioma(ctx)
        await ctx.send(idiomas[idioma]["acao_invalida"])
    else:
        logging.error(f"Erro no comando {ctx.command}: {error}")
        raise error


from discord.ext import commands  # Já deve estar no início do arquivo, mas reforçando


# Função salvar_dados (atualizada para salvar todos os dados)
def salvar_dados(rankings, historico_partidas, moedas):
    try:
        with open(RANKING_FILE, 'w', encoding='utf-8') as f:
            json.dump(
                {
                    k: {
                        t: dict(v)
                        for t, v in r.items()
                    }
                    for k, r in rankings.items()
                },
                f,
                ensure_ascii=False,
                indent=2)
        with open(HISTORICO_FILE, 'w', encoding='utf-8') as f:
            json.dump(dict(historico_partidas),
                      f,
                      ensure_ascii=False,
                      indent=2)
        with open(MOEDAS_FILE, 'w', encoding='utf-8') as f:
            json.dump(dict(moedas), f, ensure_ascii=False, indent=2)
        logging.info("Dados salvos com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao salvar dados: {e}")


# Comando para definir idioma
@bot.command()
@commands.guild_only()
async def setlanguage(ctx, lang):
    idioma = detectar_idioma(ctx)
    if lang not in ["pt", "en"]:
        await ctx.send(idiomas[idioma]["setlanguage_invalid"])
        return
    idioma_servidores[str(ctx.guild.id)] = lang  # Convertido para string
    await ctx.send(idiomas[idioma]["setlanguage_success"].format(lang=lang))


# Comando Ajuda
@bot.command()
async def ajuda(ctx):
    idioma = detectar_idioma(ctx)
    await ctx.send(idiomas[idioma]["ajuda"])


# Comando Como Jogar
@bot.command()
async def como_jogar(ctx):
    idioma = detectar_idioma(ctx)
    await ctx.send(idiomas[idioma]["como_jogar_parte1"])
    await ctx.send(idiomas[idioma]["como_jogar_parte2"])


# Comando ping
@bot.command()
async def ping(ctx):
    idioma = detectar_idioma(ctx)
    latency = round(bot.latency * 1000)
    await ctx.send(idiomas[idioma]["ping"].format(latency=latency))


# Comando Saldo
@bot.command()
async def saldo(ctx):
    idioma = detectar_idioma(ctx)
    jogador_id = str(ctx.author.id)
    moedas_jogador = moedas.get(jogador_id, {"moedas": 0, "personagens": []})
    personagens_str = ", ".join(
        moedas_jogador.get("personagens", [])) if moedas_jogador.get(
            "personagens", []) else "Nenhum"
    await ctx.send(idiomas[idioma]["saldo"].format(
        moedas=moedas_jogador.get("moedas", 0), personagens=personagens_str))


# Comando Comprar Personagem
@bot.command()
async def comprar_personagem(ctx, *, personagem=None):
    idioma = detectar_idioma(ctx)
    jogador_id = str(ctx.author.id)
    moedas_jogador = moedas.get(jogador_id, {"moedas": 0, "personagens": []})

    if not personagem:
        exclusivos = "\n".join(
            f"{p}: {custo} moedas"
            for p, custo in personagens_exclusivos.items()
            if p not in moedas_jogador.get("personagens", []))
        if not exclusivos:
            await ctx.send(idiomas[idioma]["sem_personagens_exclusivos"])
            return
        await ctx.send(
            idiomas[idioma]["personagens_exclusivos_disponiveis"].format(
                exclusivos=exclusivos))
        return

    if personagem not in personagens_exclusivos:
        await ctx.send(idiomas[idioma]["personagem_nao_exclusivo"])
        return
    if personagem in moedas_jogador.get("personagens", []):
        await ctx.send(idiomas[idioma]["personagem_ja_comprado"])
        return

    custo = personagens_exclusivos[personagem]
    if moedas_jogador["moedas"] < custo:
        await ctx.send(
            idiomas[idioma]["moedas_insuficientes"].format(custo=custo))
        return

    moedas_jogador["moedas"] -= custo
    moedas_jogador["personagens"].append(personagem)
    moedas[jogador_id] = moedas_jogador
    salvar_dados(rankings, historico_partidas, moedas)  # Salva todos os dados
    await ctx.send(idiomas[idioma]["personagem_comprado"].format(
        personagem=personagem, custo=custo))


# Comando Iniciar
@bot.command()
@commands.guild_only()
async def iniciar(ctx):
    global partida_atual, rodada_atual, cartomante_usada, personagens_disponiveis
    idioma = detectar_idioma(ctx)
    if partida_atual:
        await ctx.send(idiomas[idioma]["ja_ativa"])
        return
    partida_atual = True
    rodada_atual = 0
    cartomante_usada = False
    jogadores.clear()
    vivos.clear()
    votos.clear()
    escolhas.clear()
    amaldicoados.clear()
    deforman_mortes.clear()
    if not personagens:
        await ctx.send(
            "Erro: Nenhum personagem configurado! Contate o administrador.")
        partida_atual = False
        return
    personagens_disponiveis = list(personagens.keys())
    await ctx.send(idiomas[idioma]["iniciar_msg"])

    tempo_decorrido = 0
    while tempo_decorrido < 90:
        if len(jogadores) >= 5:
            break
        await asyncio.sleep(5)
        tempo_decorrido += 5

    if len(jogadores) < 5:
        await ctx.send(idiomas[idioma]["menos_jogadores"])
        partida_atual = False
        personagens_disponiveis = []
        return
    await ctx.send(idiomas[idioma]["identidades_enviadas"].format(
        num_jogadores=len(jogadores)))
    await iniciar_partida(ctx.channel)


# Comando Entrar
@bot.command()
@commands.guild_only()
async def entrar(ctx):
    global partida_atual, personagens_disponiveis
    idioma = detectar_idioma(ctx)
    if not partida_atual:
        await ctx.send("Nenhuma partida ativa! Use `!iniciar`.")
        return
    if len(jogadores) >= 12:
        await ctx.send("Havrenna está lotada! Limite de 12 jogadores atingido."
                       )
        return
    if ctx.author.id in jogadores:
        await ctx.send("Você já está em Havrenna!")
        return

    jogador_id = str(ctx.author.id)
    moedas_jogador = moedas.get(jogador_id, {"moedas": 0, "personagens": []})
    logging.info(
        f"Personagens disponíveis antes de entrar: {personagens_disponiveis}")

    personagens_jogador = [
        p for p in personagens_disponiveis if p not in personagens_exclusivos
        or p in moedas_jogador.get("personagens", [])
    ]
    if not personagens_jogador:
        logging.error(
            f"Sem personagens disponíveis para {ctx.author.name}. Total disponível: {personagens_disponiveis}"
        )
        await ctx.send("Não há mais personagens disponíveis!")
        return
    personagem = random.choice(personagens_jogador)
    personagens_disponiveis.remove(personagem)

    jogadores[ctx.author.id] = {
        "personagem": personagem,
        "vivo": True,
        "nome_jogador": ctx.author.name,
        "escolhas": [],
        "aliados": set(),
        "imunidades": set(),
        "invocar_usado": False,
        "espada_usada": False,
        "protegido": None,
        "bloqueios": {},
        "petrificado": [],
        "regeneracao_usada": False,
        "aliados_lua": [],
        "magia_usada": False,
        "caos_usado": False,
        "carga_caos": 0,
        "exercito_usado": False,
        "fugas": 0,
        "tiros": 3 if personagem == "Pistoleiro" else 0,
        "flecha_mortal_usada": False,
        "viloes_identificados": [],
        "observado": False
    }

    vivos.add(ctx.author.id)
    try:
        await ctx.author.send(
            f"**Among Wizards**: Você é **{personagem}**!\n"
            f"Habilidades: {', '.join(personagens[personagem]['habilidades']) if personagens[personagem]['habilidades'] else 'Nenhuma'}\n"
            f"Objetivo: {personagens[personagem]['vitoria']}\n"
            "Use os botões enviados para votar ou agir. Alternativamente, use:\n"
            "- `/votar @nome` no privado para votar.\n"
            "- `/acao habilidade @nome` no privado para ações noturnas.\n"
            "Mantenha sua identidade secreta!")
        await ctx.send(idiomas[idioma]["vulto"])
        moedas_jogador["moedas"] = moedas_jogador.get("moedas", 0) + 10
        moedas[jogador_id] = moedas_jogador
        salvar_dados(rankings, historico_partidas,
                     moedas)  # Salva todos os dados
    except discord.Forbidden:
        await ctx.send(
            f"{ctx.author.name}, habilite DMs para receber sua identidade!")
        del jogadores[ctx.author.id]
        vivos.remove(ctx.author.id)
        personagens_disponiveis.append(personagem)


# Comando Votar (Canal e DM)
@bot.command()
async def votar(ctx, *, nome_alvo):
    idioma = detectar_idioma(ctx)
    if ctx.author.id not in jogadores or not jogadores[
            ctx.author.id]["vivo"] or not partida_atual:
        await ctx.send(idiomas[idioma]["morto"])
        return
    if nome_alvo.lower() == "cartomante":
        votos[ctx.author.id] = "Cartomante"
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Você votou para convocar a Cartomante!")
        else:
            await ctx.send(idiomas[idioma]["clamar_cartomante"])
        return
    alvo_id = next(
        (id for id, j in jogadores.items()
         if j["nome_jogador"].lower() == nome_alvo.lower() and j["vivo"]),
        None)
    if not alvo_id:
        await ctx.send(idiomas[idioma]["alvo_invalido"])
        return
    votos[ctx.author.id] = alvo_id
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send(f"Você votou em {nome_alvo} para a forca!")
    else:
        await ctx.send(f"Um voto em Havrenna aponta para {nome_alvo}...")
    if rodada_atual >= 3 and jogadores[ctx.author.id]["personagem"] == "Fada":
        votos[f"{ctx.author.id}_extra"] = alvo_id
    if jogadores[ctx.author.id]["personagem"] == "Pistoleiro" and jogadores[
            ctx.author.id]["tiros"] > 0:
        jogadores[ctx.author.id]["tiros"] -= 1
        escolhas[ctx.author.id] = ("Atirar", alvo_id)
        await ctx.send(idiomas[idioma]["atirar"].format(alvo=nome_alvo))


# Comando Ação (DM)
@bot.command()
async def acao(ctx, habilidade, *, nome_alvo):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("Use este comando no privado!")
        return
    idioma = detectar_idioma(ctx)
    if ctx.author.id not in jogadores or not jogadores[
            ctx.author.id]["vivo"] or not partida_atual:
        await ctx.send(idiomas[idioma]["morto"])
        return
    personagem = jogadores[ctx.author.id]["personagem"]
    if habilidade not in personagens[personagem]["habilidades"]:
        await ctx.send(idiomas[idioma]["acao_invalida"])
        return
    alvo_id = next(
        (id for id, j in jogadores.items()
         if j["nome_jogador"].lower() == nome_alvo.lower() and j["vivo"]),
        None)
    if not alvo_id:
        await ctx.send(idiomas[idioma]["alvo_invalido"])
        return
    escolhas[ctx.author.id] = (habilidade, alvo_id)
    await ctx.send(f"Você escolheu {habilidade} em {nome_alvo}!")


# Comando Convocar Cartomante
@bot.command()
async def convocar_cartomante(ctx):
    idioma = detectar_idioma(ctx)
    if cartomante_usada or not partida_atual:
        await ctx.send(idiomas[idioma]["cartomante_usada"])
        return
    votos[ctx.author.id] = "Cartomante"
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("Você votou para convocar a Cartomante!")
    else:
        await ctx.send(idiomas[idioma]["clamar_cartomante"])


# Comando Doar
@bot.command()
async def doar(ctx):
    idioma = detectar_idioma(ctx)
    await ctx.send(idiomas[idioma]["doar"])


# Comando Lista Personagens
@bot.command()
async def lista_personagens(ctx):
    idioma = detectar_idioma(ctx)
    personagens_lista = sorted(personagens.items())
    max_por_embed = 5
    embeds = []
    for i in range(0, len(personagens_lista), max_por_embed):
        embed = discord.Embed(title=idiomas[idioma]["personagens_title"] +
                              f" (Parte {i // max_por_embed + 1})",
                              color=0x00ff00)
        for personagem, dados in personagens_lista[i:i + max_por_embed]:
            value = (
                f"Tipo: {dados['tipo'].capitalize()}\n"
                f"Habilidades: {', '.join(dados['habilidades']) if dados['habilidades'] else 'Nenhuma'}\n"
                f"Objetivo: {dados['vitoria']}\n"
                f"História: {dados['historia']}\n"
                f"Força: {dados['forca']}\n"
                f"Fraqueza: {dados['fraqueza']}")
            if dados.get("exclusivo"):
                value += f"\nCusto: {personagens_exclusivos[personagem]} moedas"
            embed.add_field(name=personagem, value=value, inline=False)
        embeds.append(embed)
    for embed in embeds:
        await ctx.send(embed=embed)


# Comando Histórico
@bot.command()
@commands.guild_only()
async def historico(ctx):
    idioma = detectar_idioma(ctx)
    server_id = str(ctx.guild.id)
    partidas = historico_partidas.get(server_id,
                                      [])[-20:]  # Últimas 20 partidas
    if not partidas:
        await ctx.send(idiomas[idioma]["sem_historico"])
        return
    embed = discord.Embed(title=idiomas[idioma]["historico_title"].format(
        servidor=ctx.guild.name),
                          color=0x00ff00)
    for data, vencedor_id, vivos_ids in partidas[::-1]:
        vencedor_nome = "Ninguém" if not vencedor_id else f"ID {vencedor_id}"  # Evitar usar jogadores
        vivos_nomes = [f"ID {id}"
                       for id in vivos_ids] if vivos_ids else ["Ninguém"]
        embed.add_field(
            name=data,
            value=f"Vencedor: {vencedor_nome}\nVivos: {', '.join(vivos_nomes)}",
            inline=False)
    await ctx.send(embed=embed)


# Comando Rank
@bot.command()
@commands.guild_only()
async def rank(ctx):
    idioma = detectar_idioma(ctx)
    server_id = str(ctx.guild.id)
    rank_data = rankings.get(server_id, {
        "diario": {},
        "semanal": {},
        "mensal": {}
    })

    if not any(rank_data.values()):
        await ctx.send(idiomas[idioma]["sem_ranking"])
        return

    ranking_diario = "\n".join(f"{i}. {nome}: {pontos} pontos"
                               for i, (nome, pontos) in enumerate(
                                   sorted(rank_data["diario"].items(),
                                          key=lambda x: x[1],
                                          reverse=True)[:5], 1)) or "Sem dados"
    ranking_semanal = "\n".join(
        f"{i}. {nome}: {pontos} pontos" for i, (nome, pontos) in enumerate(
            sorted(rank_data["semanal"].items(),
                   key=lambda x: x[1],
                   reverse=True)[:5], 1)) or "Sem dados"
    ranking_mensal = "\n".join(f"{i}. {nome}: {pontos} pontos"
                               for i, (nome, pontos) in enumerate(
                                   sorted(rank_data["mensal"].items(),
                                          key=lambda x: x[1],
                                          reverse=True)[:5], 1)) or "Sem dados"

    msg = idiomas[idioma]["ranking_msg"].format(
        ranking_diario=ranking_diario,
        ranking_semanal=ranking_semanal,
        ranking_mensal=ranking_mensal)
    await ctx.send(msg)


# Processar Cartomante
async def processar_cartomante(canal):
    global cartomante_usada
    idioma = detectar_idioma(canal)
    cartomante_usada = True
    alvos = random.sample(list(vivos), min(3, len(vivos)))
    maus = sum(1 for id in alvos
               if personagens[jogadores[id]["personagem"]]["tipo"] == "mau")
    await canal.send(
        f"A Cartomante observa {', '.join(jogadores[id]['nome_jogador'] for id in alvos)} e revela que {'há' if maus else 'não há'} vilões entre eles!"
    )
    votos.clear()


# Verificar Vitória
async def verificar_vitoria(canal):
    global partida_atual
    idioma = detectar_idioma(canal)
    vivos_ativos = [id for id in vivos if jogadores[id]["vivo"]]
    if not vivos_ativos:
        await canal.send(idiomas[idioma]["sem_vencedores"])
        return True
    if len(vivos_ativos) == 1:
        vencedor_id = vivos_ativos[0]
        personagem = jogadores[vencedor_id]["personagem"]
        nome_jogador = jogadores[vencedor_id]["nome_jogador"]
        await canal.send(idiomas[idioma]["vitoria_unica"].format(
            personagem=personagem, nome_jogador=nome_jogador))
        # Adicionar 50 moedas ao vencedor
        jogador_id = str(vencedor_id)
        moedas_jogador = moedas.get(jogador_id, {
            "moedas": 0,
            "personagens": []
        })
        moedas_jogador["moedas"] += 50
        moedas[jogador_id] = moedas_jogador
        salvar_dados(rankings, historico_partidas, moedas)
        return True
    for id in vivos_ativos:
        personagem = jogadores[id]["personagem"]
        if personagem == "Vidente" and all(
                jogadores[alvo_id]["personagem"] in jogadores[id]["imunidades"]
                for alvo_id in vivos_ativos if alvo_id != id):
            await canal.send(idiomas[idioma]["vitoria_vidente"].format(
                nome_jogador=jogadores[id]["nome_jogador"]))
            return True
        elif personagem == "Carcereiro" and all(
                personagens[jogadores[vilao]["personagem"]]["tipo"] == "mau"
                for vilao in jogadores[id]["viloes_identificados"]):
            await canal.send(idiomas[idioma]["vitoria_carcereiro"].format(
                nome_jogador=jogadores[id]["nome_jogador"]))
            return True
        elif personagem == "Criatura" and (
                jogadores[id]["fugas"] >= 3 or (len(vivos_ativos) == 2 and any(
                    escolhas.get(k, ("", None))[0] == "Contra-atacar"
                    for k in vivos_ativos))):
            await canal.send(idiomas[idioma]["vitoria_criatura"].format(
                nome_jogador=jogadores[id]["nome_jogador"]))
            return True
    if rodada_atual >= 10:
        await canal.send(idiomas[idioma]["empate"])
        return True
    return False


# Processar Noite
async def processar_noite(canal):
    global espada_ativa, rodada_atual
    idioma = detectar_idioma(canal)
    narrativa_mortes = []
    assassinos = []
    mortes = set()
    protecoes = set()
    hipnotizados = {}  # {id: (alvo_id, sub_alvo_id)}
    revelados = {}  # {id: rodada}
    mutações = {}  # {id: alvo_id}

    # Atualizar carga do Agente do Caos
    for id in jogadores:
        if jogadores[id]["personagem"] == "Agente do Caos" and id in vivos:
            jogadores[id]["carga_caos"] += 1

    # Processar bloqueios
    if espada_ativa:
        espada_ativa -= 1
    for id in jogadores:
        for bloqueador_id, rodadas in list(jogadores[id]["bloqueios"].items()):
            if rodadas > 0:
                jogadores[id]["bloqueios"][bloqueador_id] = rodadas - 1
                if rodadas == 0 and jogadores[id]["vivo"] and not personagens[
                        jogadores[id]["personagem"]]["habilidades"]:
                    mortes.add(id)
                    narrativa_mortes.append(
                        f"{jogadores[id]['nome_jogador']} ({jogadores[id]['personagem']}) foi morto por não ter escolha!"
                    )
        for petrificador_id, rodadas in list(
                jogadores[id]["petrificado"].items()):
            if rodadas > 0:
                jogadores[id]["petrificado"][petrificador_id] = rodadas - 1

    # Processar amaldiçoados
    bruxa_viva = any(j["personagem"] == "Bruxa" and j["vivo"]
                     for j in jogadores.values())
    for id in list(amaldicoados):
        if not bruxa_viva:
            continue
        amaldicoados[id] -= 1
        if amaldicoados[id] <= 0 and id in vivos and jogadores[id]["vivo"]:
            mortes.add(id)
            narrativa_mortes.append(
                f"{jogadores[id]['nome_jogador']} sucumbiu à maldição de uma Bruxa!"
            )

    # Processar escolhas
    for id, (acao, alvo) in escolhas.items():
        if not jogadores.get(id, {}).get("vivo", False) or id in jogadores[id][
                "bloqueios"] or id in jogadores[id]["petrificado"]:
            continue
        personagem = jogadores[id]["personagem"]
        if personagem == "Mago Branco":
            protecoes.add(alvo)
            narrativa_mortes.append(idiomas[idioma]["curar_defesa"].format(
                acao=acao, alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Mago Reverso" and acao == "Atacar" and alvo not in protecoes:
            mortes.add(alvo)
            assassinos.append("Mago Reverso")
            narrativa_mortes.append(idiomas[idioma]["ataque_aleatorio"])
        elif personagem == "Mago Reverso" and acao == "Invocar" and not jogadores[
                id].get("invocar_usado", False):
            jogadores[id]["invocar_usado"] = True
            alvos = random.sample(list(vivos), min(2, len(vivos)))
            mortes.update(alvos)
            assassinos.append("Mago Reverso")
            narrativa_mortes.append(idiomas[idioma]["invocar"])
        elif personagem in ["Aldeão", "Bêbado"]:
            continue
        elif personagem == "Fazendeiro" and acao == "Salvar":
            protecoes.add(alvo)
            narrativa_mortes.append(idiomas[idioma]["salvar"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Vampiro" and acao == "Matar" and alvo not in protecoes:
            mortes.add(alvo)
            assassinos.append("Vampiro")
            narrativa_mortes.append(idiomas[idioma]["matar_vampiro"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Vampiro" and acao == "Cravar Presas":
            jogadores[id]["aliados"].add(alvo)
            narrativa_mortes.append(idiomas[idioma]["cravar_pesas"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Médico" and acao == "Curar":
            protecoes.add(alvo)
            narrativa_mortes.append(idiomas[idioma]["curar_defesa"].format(
                acao=acao, alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Padre" and acao == "Água Benta" and jogadores[
                alvo]["personagem"] == "Vampiro":
            mortes.add(alvo)
            assassinos.append("Padre")
            narrativa_mortes.append(idiomas[idioma]["agua_benta"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Assassino" and acao == "Assassinar" and alvo not in protecoes:
            mortes.add(alvo)
            assassinos.append("Assassino")
            narrativa_mortes.append(idiomas[idioma]["assassinar"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Vidente" and acao == "Visão":
            jogadores[id]["imunidades"].add(alvo)
            narrativa_mortes.append(idiomas[idioma]["visao"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Sobrevivente" and acao == "Escolha":
            jogadores[id]["protegido"] = alvo
            narrativa_mortes.append(idiomas[idioma]["escolha_protecao"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Bruxa" and acao == "Amaldiçoar":
            amaldicoados[alvo] = 2
            narrativa_mortes.append(idiomas[idioma]["amaldicoar"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Bruxa" and acao == "Matar 2":
            alvos = random.sample(list(vivos), min(2, len(vivos)))
            mortes.update(alvos)
            assassinos.append("Bruxa")
            narrativa_mortes.append(idiomas[idioma]["matar_2"])
        elif personagem == "Feiticeira" and acao == "Feitiço":
            alvo_id, sub_alvo_id = alvo
            escolhas[alvo_id] = ("Atacar", sub_alvo_id)
            narrativa_mortes.append(idiomas[idioma]["feitico"].format(
                alvo=jogadores[alvo_id]["nome_jogador"],
                acao="Atacar",
                sub_alvo=jogadores[sub_alvo_id]["nome_jogador"]))
        elif personagem == "Deforman" and acao == "Matar" and alvo not in protecoes:
            mortes.add(alvo)
            assassinos.append("Deforman")
            narrativa_mortes.append(idiomas[idioma]["matar_deforman"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Deforman" and acao == "Espada das Sombras" and not jogadores[
                id].get("espada_usada", False):
            jogadores[id]["espada_usada"] = True
            espada_ativa = 2
            alvos = random.sample(list(vivos), min(2, len(vivos)))
            mortes.update(alvos)
            assassinos.append("Deforman")
            narrativa_mortes.append(idiomas[idioma]["espada_ativa"])
        elif personagem == "Fada" and acao == "Varinha":
            narrativa_mortes.append(idiomas[idioma]["varinha"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Segurança" and acao == "Proteger":
            protecoes.add(alvo)
            narrativa_mortes.append(idiomas[idioma]["escolha_protecao"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Mago Vermelho" and acao == "Petrificar":
            jogadores[alvo]["petrificado"][id] = 2
            narrativa_mortes.append(
                f"Mago Vermelho petrificou {jogadores[alvo]['nome_jogador']}!")
        elif personagem == "Mago Vermelho" and acao == "Regeneração" and not jogadores[
                id].get("regeneracao_usada", False):
            jogadores[id]["regeneracao_usada"] = True
            protecoes.add(id)
            narrativa_mortes.append(f"Mago Vermelho usou Regeneração!")
        elif personagem == "Mago Azul" and acao == "Céu Azul":
            alvo_id = random.choice(list(vivos))
            escolhas[alvo_id] = ("Atacar", random.choice(list(vivos)))
            assassinos.append("Mago Azul")
            narrativa_mortes.append(idiomas[idioma]["ceu_azu"].format(
                alvo=jogadores[alvo_id]["nome_jogador"]
                if alvo_id else "ninguém"))
        elif personagem == "Mago Azul" and acao == "Magia da Verdade" and not jogadores[
                id].get("magia_usada", False):
            jogadores[id]["magia_usada"] = True
            await canal.send(idiomas[idioma]["magia_verdade"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Agente do Caos" and acao == "Causador de Caos" and not jogadores[
                id].get("caos_usado", False):
            jogadores[id]["caos_usado"] = True
            for j_id in vivos:
                if j_id != id:
                    jogadores[j_id]["bloqueios"][id] = 1
            assassinos.append("Agente do Caos")
            narrativa_mortes.append(idiomas[idioma]["causador_caos"])
        elif personagem == "Agente do Caos" and acao == "Senhor do Caos" and jogadores[
                id].get("carga_caos", 0) >= 3:
            escolhas[alvo] = ("Atacar", random.choice(list(vivos)))
            jogadores[id]["carga_caos"] = 0
            assassinos.append("Agente do Caos")
            narrativa_mortes.append(idiomas[idioma]["senhor_caos"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Garota Infernal" and acao == "Chamas da Vingança" and alvo not in protecoes:
            mortes.add(alvo)
            assassinos.append("Garota Infernal")
            narrativa_mortes.append(idiomas[idioma]["chamas_vinganca"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Garota Infernal" and acao == "Exército de Fogo" and not jogadores[
                id].get("exercito_usado", False):
            jogadores[id]["exercito_usado"] = True
            mortes.update(alvo)
            assassinos.append("Garota Infernal")
            narrativa_mortes.append(idiomas[idioma]["exercito_fogo"].format(
                alvo=", ".join(jogadores[a]["nome_jogador"] for a in alvo)))
        elif personagem == "Mutante" and acao == "Metamorfose":
            mutações[id] = alvo
            narrativa_mortes.append(idiomas[idioma]["metamorfose"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Carcereiro" and acao == "Prender":
            alvo_id, sub_acao = alvo
            if sub_acao == "prender":
                jogadores[alvo_id]["bloqueios"][id] = 1
                jogadores[id]["viloes_identificados"].append(alvo_id)
                narrativa_mortes.append(idiomas[idioma]["prender"].format(
                    alvo=jogadores[alvo_id]["nome_jogador"]))
            else:
                if personagens[jogadores[alvo_id]
                               ["personagem"]]["tipo"] != "mau":
                    mortes.add(id)
                    narrativa_mortes.append(
                        f"Carcereiro matou um inocente e caiu!")
                else:
                    mortes.add(alvo_id)
                    jogadores[id]["viloes_identificados"].append(alvo_id)
                    assassinos.append("Carcereiro")
                    narrativa_mortes.append(
                        f"Carcereiro matou {jogadores[alvo_id]['nome_jogador']}!"
                    )
        elif personagem == "Criatura" and acao == "Fugir":
            jogadores[id]["fugas"] += 1
            protecoes.add(id)
            narrativa_mortes.append(idiomas[idioma]["fugir"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Criatura" and acao == "Contra-atacar" and alvo not in protecoes:
            mortes.add(alvo)
            assassinos.append("Criatura")
            narrativa_mortes.append(idiomas[idioma]["contra_atacar"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Arqueira" and acao == "Flechada" and random.random(
        ) < 0.7:
            mortes.add(alvo)
            assassinos.append("Arqueira")
            narrativa_mortes.append(idiomas[idioma]["flechada"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Arqueiro das Sombras" and acao == "Flecha da Escuridão":
            jogadores[alvo]["bloqueios"][id] = 1
            narrativa_mortes.append(idiomas[idioma]["flecha_escuridao"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Arqueiro das Sombras" and acao == "Flecha Mortal" and not jogadores[
                id].get("flecha_mortal_usada", False):
            jogadores[id]["flecha_mortal_usada"] = True
            mortes.add(alvo)
            escolhas[alvo] = ("Atacar", random.choice(list(vivos)))
            assassinos.append("Arqueiro das Sombras")
            narrativa_mortes.append(idiomas[idioma]["flecha_mortal"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Hipnotizador" and acao == "Hipnotizar":
            alvo_id, sub_alvo_id = alvo
            hipnotizados[alvo_id] = (alvo_id, sub_alvo_id)
            narrativa_mortes.append(idiomas[idioma]["hipnotizar"].format(
                alvo=jogadores[alvo_id]["nome_jogador"],
                sub_alvo=jogadores[sub_alvo_id]["nome_jogador"]))
        elif personagem == "Hipnotizador" and acao == "Revelação":
            revelados[alvo] = rodada_atual
            await canal.send(idiomas[idioma]["revelacao"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Bicho Papão" and acao == "Puxar os Pés":
            jogadores[alvo]["bloqueios"][id] = 2
            narrativa_mortes.append(idiomas[idioma]["puxar_pes"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Fantasma" and acao == "Assumir Controle":
            jogadores[id]["habilidades"] = personagens[
                jogadores[alvo]["personagem"]]["habilidades"]
            narrativa_mortes.append(idiomas[idioma]["assumir_controle"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Senhor da Chuva" and acao == "Chuva":
            jogadores[alvo]["bloqueios"][id] = 1
            narrativa_mortes.append(idiomas[idioma]["chuva"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Senhor da Chuva" and acao == "Afogar" and alvo not in protecoes:
            mortes.add(alvo)
            assassinos.append("Senhor da Chuva")
            narrativa_mortes.append(idiomas[idioma]["afogar"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Observador" and acao == "Observar":
            jogadores[id]["observado"] = True
            await canal.send(idiomas[idioma]["observar"])
        elif personagem == "Lobisomem" and acao == "Arrancar Cabeças" and alvo not in protecoes:
            mortes.add(alvo)
            assassinos.append("Lobisomem")
            narrativa_mortes.append(idiomas[idioma]["arrancar_cabecas"].format(
                alvo=jogadores[alvo]["nome_jogador"]))
        elif personagem == "Lobisomem" and acao == "Arranhar":
            jogadores[id]["aliados_lua"].append(alvo)
            narrativa_mortes.append(idiomas[idioma]["arranhar"].format(
                alvo=jogadores[alvo]["nome_jogador"]))

    # Processar mortes
    for id in mortes:
        if id in vivos:
            jogadores[id]["vivo"] = False
            vivos.remove(id)
            narrativa_mortes.append(
                f"{jogadores[id]['nome_jogador']} ({jogadores[id]['personagem']}) foi encontrado morto em Havrenna!"
            )

    # Processar hipnotizados (aplicar na próxima rodada)
    for alvo_id, (alvo, sub_alvo) in hipnotizados.items():
        if alvo_id in vivos and sub_alvo in vivos:
            escolhas[alvo_id] = ("Atacar", sub_alvo)

    # Enviar narrativa da noite
    if narrativa_mortes:
        await canal.send(idiomas[idioma]["noite_assustadora"].format(
            rodada_atual=rodada_atual,
            assassinos=", ".join(set(assassinos))
            if assassinos else "forças desconhecidas",
            narrativa_mortes="\n".join(narrativa_mortes)))
    else:
        await canal.send(idiomas[idioma]["noite_silenciosa"].format(
            rodada_atual=rodada_atual))

    escolhas.clear()


# Iniciar Partida
async def iniciar_partida(canal):
    global rodada_atual, cartomante_usada, partida_atual
    idioma = detectar_idioma(canal)

    if not personagens_disponiveis:
        await canal.send("Erro: Nenhum personagem disponível!")
        partida_atual = False
        return

    while partida_atual:
        rodada_atual += 1
        if await verificar_vitoria(canal):
            partida_atual = False
            historico_partidas[str(canal.guild.id)].append(
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 next((id for id in jogadores if jogadores[id]["vivo"]),
                      None), list(vivos)))
            salvar_dados(rankings, historico_partidas, moedas)
            break

        # Fase da Noite
        for id in vivos:
            personagem = jogadores[id]["personagem"]
            habilidades = [
                hab for hab in personagens[personagem]["habilidades"]
                if (hab != "Magia da Verdade"
                    or not jogadores[id].get("magia_usada", False)) and (
                        hab != "Causador de Caos"
                        or not jogadores[id].get("caos_usado", False)) and
                (hab != "Senhor do Caos" or jogadores[id].get("carga_caos", 0)
                 >= 3) and (hab != "Exército de Fogo"
                            or not jogadores[id].get("exercito_usado", False))
                and (hab != "Flecha Mortal"
                     or not jogadores[id].get("flecha_mortal_usada", False))
                and (hab != "Invocar" or not jogadores[id].get(
                    "invocar_usado", False) and rodada_atual >= 3)
            ]
            if not habilidades:
                continue
            alvos = [p for p in vivos if p != id] if habilidades[0] not in [
                "Fugir", "Observar", "Causador de Caos"
            ] else []
            try:
                view = AcaoSelecao(id, habilidades, alvos, idioma)
                await bot.get_user(id).send(
                    f"**{personagem}**: Escolha sua ação para a noite {rodada_atual}.",
                    view=view)
            except discord.Forbidden:
                logging.warning(
                    f"Não foi possível enviar DM para {jogadores[id]['nome_jogador']}."
                )
        await asyncio.sleep(90)
        await processar_noite(canal)

        # Verificar vitória após a noite
        if await verificar_vitoria(canal):
            partida_atual = False
            historico_partidas[str(canal.guild.id)].append(
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 next((id for id in jogadores if jogadores[id]["vivo"]),
                      None), list(vivos)))
            salvar_dados(rankings, historico_partidas, moedas)
            break

        # Fase do Dia
        votos.clear()
        for id in vivos:
            try:
                view = VotoSelect(vivos, idioma)
                await bot.get_user(id).send(
                    f"**Dia {rodada_atual}**: Escolha quem será levado à forca ou convoque a Cartomante.",
                    view=view)
            except discord.Forbidden:
                logging.warning(
                    f"Não foi possível enviar DM para {jogadores[id]['nome_jogador']}."
                )
        await canal.send(
            f"Dia {rodada_atual} em Havrenna! Votem em quem deve ir à forca nos próximos 90 segundos (use os botões nas DMs ou `/votar [nome]`)."
        )
        await asyncio.sleep(90)

        # Contar votos
        contagem_votos = defaultdict(int)
        for voto in votos.values():
            if voto == "Cartomante":
                contagem_votos["Cartomante"] += 1
            else:
                contagem_votos[voto] += 1
        if not contagem_votos:
            await canal.send("Ninguém votou em Havrenna... A névoa continua.")
            continue

        max_votos = max(contagem_votos.values())
        alvos = [k for k, v in contagem_votos.items() if v == max_votos]
        alvo_escolhido = random.choice(alvos) if alvos else None

        if alvo_escolhido == "Cartomante" and not cartomante_usada:
            await processar_cartomante(canal)
        elif alvo_escolhido and alvo_escolhido in vivos:
            personagem = jogadores[alvo_escolhido]["personagem"]
            nome_jogador = jogadores[alvo_escolhido]["nome_jogador"]
            if personagem == "Badernista":
                await canal.send(idiomas[idioma]["badernista_vence"].format(
                    nome_jogador=nome_jogador))
                partida_atual = False
                historico_partidas[str(canal.guild.id)].append(
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                     alvo_escolhido, list(vivos)))
                salvar_dados(rankings, historico_partidas, moedas)
                break
            else:
                jogadores[alvo_escolhido]["vivo"] = False
                vivos.remove(alvo_escolhido)
                await canal.send(idiomas[idioma]["enforcado"].format(
                    personagem=personagem, nome_jogador=nome_jogador))
                if personagem == "Fada":
                    await canal.send(idiomas[idioma]["vitoria_fada"].format(
                        nome_jogador=nome_jogador))
                    partida_atual = False
                    historico_partidas[str(canal.guild.id)].append(
                        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         alvo_escolhido, list(vivos)))
                    salvar_dados(rankings, historico_partidas, moedas)
                    break

        # Processar ações diurnas (ex.: Pistoleiro)
        for id, (acao, alvo) in escolhas.items():
            if acao == "Atirar" and jogadores[id][
                    "personagem"] == "Pistoleiro" and alvo in vivos:
                jogadores[alvo]["vivo"] = False
                vivos.remove(alvo)
                narrativa_mortes.append(idiomas[idioma]["atirar"].format(
                    alvo=jogadores[alvo]["nome_jogador"]))
            elif acao == "Exército de Fogo" and jogadores[id][
                    "personagem"] == "Garota Infernal":
                jogadores[id]["exercito_usado"] = True
                if isinstance(alvo, list):  # Suporte a múltiplos alvos
                    for alvo_id in alvo[:2]:  # Limite de 2 alvos
                        if alvo_id in vivos:
                            jogadores[alvo_id]["vivo"] = False
                            vivos.remove(alvo_id)
                            narrativa_mortes.append(
                                f"{jogadores[alvo_id]['nome_jogador']} foi consumido pelo Exército de Fogo!"
                            )
            elif acao == "Prender" and jogadores[id][
                    "personagem"] == "Carcereiro":
                if isinstance(alvo, tuple):  # (alvo_id, "prender" ou "matar")
                    alvo_id, sub_acao = alvo
                    if sub_acao == "matar" and alvo_id in vivos:
                        jogadores[alvo_id]["vivo"] = False
                        vivos.remove(alvo_id)
                        narrativa_mortes.append(
                            f"{jogadores[alvo_id]['nome_jogador']} foi executado pelo Carcereiro!"
                        )

        # Verificar vitória após o dia
        if await verificar_vitoria(canal):
            partida_atual = False
            historico_partidas[str(canal.guild.id)].append(
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 next((id for id in jogadores if jogadores[id]["vivo"]),
                      None), list(vivos)))
            salvar_dados(rankings, historico_partidas, moedas)
            break

        # Bêbado cambaleia
        bebado_id = next(
            (id for id in vivos if jogadores[id]["personagem"] == "Bêbado"),
            None)
        if bebado_id:
            await canal.send(idiomas[idioma]["bebado_cambaleia"].format(
                nome_jogador=jogadores[bebado_id]["nome_jogador"]))

    # Finalizar partida
    await canal.send("Partida encerrada em Havrenna!")
    partida_atual = False
    personagens_disponiveis = []
    jogadores.clear()
    vivos.clear()
    votos.clear()
    escolhas.clear()
    amaldicoados.clear()
    deforman_mortes.clear()
    cartomante_usada = False
    narrativa_mortes.clear()
    rodada_atual = 0
    salvar_dados(rankings, historico_partidas, moedas)


from flask import Flask
from threading import Thread

app = Flask(__name__)  # Corrigido com dois underscores


@app.route('/')
def main():
    return "Bot is online!"


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    server = Thread(target=run)
    server.start()


keep_alive()
bot.run(TOKEN)
