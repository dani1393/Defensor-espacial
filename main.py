import os
import random
import sys

import pygame

LARGURA, ALTURA = 800, 600
FPS = 60

# Cores
PRETO = (10, 12, 24)
BRANCO = (240, 240, 240)
AZUL = (60, 130, 240)
AZUL_CLARO = (120, 190, 255)
AMARELO = (250, 200, 60)
VERMELHO = (230, 70, 70)
VERDE = (90, 210, 120)
CINZA = (150, 150, 170)

PONTUACAO_VITORIA = 20
VIDAS_INICIAIS = 3

ESTADO_MENU = "menu"
ESTADO_JOGANDO = "jogando"
ESTADO_VITORIA = "vitoria"
ESTADO_DERROTA = "derrota"


def _base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = _base_dir()


def caminho_asset(*partes):
    return os.path.join(BASE_DIR, "assets", *partes)


# Entidades
class Jogador:
    def __init__(self):
        self.largura = 50
        self.altura = 40
        self.x = LARGURA // 2 - self.largura // 2
        self.y = ALTURA - self.altura - 20
        self.velocidade = 6

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)

    def mover(self, teclas):
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.x -= self.velocidade
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.x += self.velocidade
        self.x = max(0, min(self.x, LARGURA - self.largura))

    def desenhar(self, tela):
        pontos = [
            (self.x + self.largura // 2, self.y),
            (self.x, self.y + self.altura),
            (self.x + self.largura, self.y + self.altura),
        ]
        pygame.draw.polygon(tela, AZUL_CLARO, pontos)
        pygame.draw.rect(tela, AZUL, (self.x + 10, self.y + self.altura - 10, self.largura - 20, 10))
        pygame.draw.circle(tela, AMARELO, (self.x + self.largura // 2, self.y + 18), 6)


class Tiro:
    def __init__(self, x, y):
        self.largura = 5
        self.altura = 14
        self.x = x - self.largura // 2
        self.y = y
        self.velocidade = 9

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)

    def atualizar(self):
        self.y -= self.velocidade

    def desenhar(self, tela):
        pygame.draw.rect(tela, AMARELO, self.rect)

    def fora_da_tela(self):
        return self.y + self.altura < 0


class Inimigo:
    def __init__(self):
        self.tamanho = random.randint(30, 50)
        self.x = random.randint(0, LARGURA - self.tamanho)
        self.y = -self.tamanho
        self.velocidade = random.uniform(1.5, 3.5)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.tamanho, self.tamanho)

    def atualizar(self):
        self.y += self.velocidade

    def desenhar(self, tela):
        centro = (self.x + self.tamanho // 2, self.y + self.tamanho // 2)
        raio = self.tamanho // 2
        pygame.draw.circle(tela, VERMELHO, centro, raio)
        pygame.draw.circle(tela, (160, 40, 40), centro, raio, 3)
        pygame.draw.circle(tela, (180, 90, 90), (centro[0] - raio // 3, centro[1] - raio // 3), max(2, raio // 5))

    def passou_da_tela(self):
        return self.y > ALTURA


# Jogo principal
class Jogo:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
            self.audio_ok = True
        except pygame.error as erro:
            print(f"Aviso: audio indisponivel ({erro}). O jogo rodara sem som.")
            self.audio_ok = False

        pygame.display.set_caption("Defensor Espacial - UNINTER")
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        self.relogio = pygame.time.Clock()

        self.fonte_titulo = pygame.font.SysFont("arialblack", 56)
        self.fonte_media = pygame.font.SysFont("arial", 30)
        self.fonte_pequena = pygame.font.SysFont("arial", 22)

        self.estrelas = [
            (random.randint(0, LARGURA), random.randint(0, ALTURA), random.randint(1, 3))
            for _ in range(80)
        ]

        self.fundo = self.carregar_fundo()

        self.som_explosao = self.carregar_som("8bit_bomb_explosion.wav")
        self.som_game_over = self.carregar_som("freesound_community-game-over-arcade-6435.mp3")
        self.musica_menu = caminho_asset("soundreality-wrong-place-129242.mp3")

        self.estado_anterior = None
        self.estado = ESTADO_MENU
        self.resetar_partida()

    def carregar_som(self, nome_arquivo):
        if not self.audio_ok:
            return None
        caminho = caminho_asset(nome_arquivo)
        try:
            return pygame.mixer.Sound(caminho)
        except (pygame.error, FileNotFoundError) as erro:
            print(f"Aviso: nao foi possivel carregar o som '{nome_arquivo}' ({erro}).")
            return None

    def tocar(self, som):
        if som is not None:
            som.play()

    def tocar_musica_menu(self):
        if not self.audio_ok:
            return
        try:
            pygame.mixer.music.load(self.musica_menu)
            pygame.mixer.music.play(-1)
        except (pygame.error, FileNotFoundError) as erro:
            print(f"Aviso: nao foi possivel tocar a musica do menu ({erro}).")

    def parar_musica_menu(self):
        if self.audio_ok:
            pygame.mixer.music.stop()

    def carregar_fundo(self):
        caminho = caminho_asset("fundo.png")
        try:
            imagem = pygame.image.load(caminho).convert()
            return pygame.transform.scale(imagem, (LARGURA, ALTURA))
        except (pygame.error, FileNotFoundError) as erro:
            print(f"Aviso: nao foi possivel carregar o cenario de fundo ({erro}).")
            return None

    def resetar_partida(self):
        self.jogador = Jogador()
        self.tiros = []
        self.inimigos = []
        self.pontuacao = 0
        self.vidas = VIDAS_INICIAIS
        self.tempo_spawn = 0
        self.intervalo_spawn = 900

    def desenhar_fundo(self):
        if self.fundo is not None:
            self.tela.blit(self.fundo, (0, 0))
        else:
            self.tela.fill(PRETO)
            for x, y, r in self.estrelas:
                pygame.draw.circle(self.tela, BRANCO, (x, y), r)

    def texto_centralizado(self, texto, fonte, cor, y):
        render = fonte.render(texto, True, cor)
        rect = render.get_rect(center=(LARGURA // 2, y))
        self.tela.blit(render, rect)

    def tela_menu(self):
        self.desenhar_fundo()
        self.texto_centralizado("DEFENSOR ESPACIAL", self.fonte_titulo, AZUL_CLARO, 120)
        self.texto_centralizado("Demo - Linguagem de Programacao Aplicada", self.fonte_pequena, CINZA, 165)

        self.texto_centralizado("COMANDOS", self.fonte_media, AMARELO, 250)
        comandos = [
            "Setas  ou  A / D  -  Mover a nave",
            "Espaco  -  Atirar",
            "ESC  -  Sair do jogo",
        ]
        y = 300
        for c in comandos:
            self.texto_centralizado(c, self.fonte_pequena, BRANCO, y)
            y += 36

        self.texto_centralizado(f"Objetivo: destrua {PONTUACAO_VITORIA} inimigos para vencer!",
                                self.fonte_pequena, VERDE, y + 20)
        self.texto_centralizado(f"Voce tem {VIDAS_INICIAIS} vidas. Nao deixe os inimigos passarem!",
                                self.fonte_pequena, CINZA, y + 52)

        self.texto_centralizado("Pressione ENTER para comecar", self.fonte_media, AMARELO, ALTURA - 70)

    def tela_fim(self, venceu):
        self.desenhar_fundo()
        if venceu:
            self.texto_centralizado("VITORIA!", self.fonte_titulo, VERDE, 200)
            self.texto_centralizado("Voce defendeu o espaco com sucesso!", self.fonte_media, BRANCO, 270)
        else:
            self.texto_centralizado("FIM DE JOGO", self.fonte_titulo, VERMELHO, 200)
            self.texto_centralizado("Os inimigos venceram desta vez...", self.fonte_media, BRANCO, 270)

        self.texto_centralizado(f"Pontuacao: {self.pontuacao}", self.fonte_media, AMARELO, 330)
        self.texto_centralizado("ENTER - Jogar novamente", self.fonte_pequena, BRANCO, 420)
        self.texto_centralizado("M - Voltar ao menu", self.fonte_pequena, BRANCO, 455)
        self.texto_centralizado("ESC - Sair", self.fonte_pequena, CINZA, 490)

    def desenhar_hud(self):
        txt = self.fonte_pequena.render(f"Pontos: {self.pontuacao}/{PONTUACAO_VITORIA}", True, BRANCO)
        self.tela.blit(txt, (15, 12))
        txt_v = self.fonte_pequena.render("Vidas:", True, BRANCO)
        self.tela.blit(txt_v, (LARGURA - 160, 12))
        for i in range(self.vidas):
            cx = LARGURA - 90 + i * 28
            pygame.draw.circle(self.tela, VERMELHO, (cx, 23), 9)

    def atualizar_jogo(self, dt):
        teclas = pygame.key.get_pressed()
        self.jogador.mover(teclas)

        self.tempo_spawn += dt
        if self.tempo_spawn >= self.intervalo_spawn:
            self.tempo_spawn = 0
            self.inimigos.append(Inimigo())

        for tiro in self.tiros[:]:
            tiro.atualizar()
            if tiro.fora_da_tela():
                self.tiros.remove(tiro)

        for inimigo in self.inimigos[:]:
            inimigo.atualizar()

            if inimigo.passou_da_tela():
                self.inimigos.remove(inimigo)
                self.vidas -= 1
                continue

            if inimigo.rect.colliderect(self.jogador.rect):
                self.inimigos.remove(inimigo)
                self.vidas -= 1
                continue

        for tiro in self.tiros[:]:
            for inimigo in self.inimigos[:]:
                if tiro.rect.colliderect(inimigo.rect):
                    if tiro in self.tiros:
                        self.tiros.remove(tiro)
                    self.inimigos.remove(inimigo)
                    self.pontuacao += 1
                    self.tocar(self.som_explosao)
                    break

        if self.pontuacao >= PONTUACAO_VITORIA:
            self.estado = ESTADO_VITORIA
        elif self.vidas <= 0:
            self.vidas = 0
            self.estado = ESTADO_DERROTA

    def desenhar_jogo(self):
        self.desenhar_fundo()
        for tiro in self.tiros:
            tiro.desenhar(self.tela)
        for inimigo in self.inimigos:
            inimigo.desenhar(self.tela)
        self.jogador.desenhar(self.tela)
        self.desenhar_hud()

    def processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.encerrar()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.encerrar()

                if self.estado == ESTADO_MENU:
                    if evento.key == pygame.K_RETURN:
                        self.resetar_partida()
                        self.estado = ESTADO_JOGANDO

                elif self.estado == ESTADO_JOGANDO:
                    if evento.key == pygame.K_SPACE:
                        self.tiros.append(Tiro(self.jogador.x + self.jogador.largura // 2,
                                               self.jogador.y))

                elif self.estado in (ESTADO_VITORIA, ESTADO_DERROTA):
                    if evento.key == pygame.K_RETURN:
                        self.resetar_partida()
                        self.estado = ESTADO_JOGANDO
                    elif evento.key == pygame.K_m:
                        self.estado = ESTADO_MENU

    def encerrar(self):
        pygame.quit()
        sys.exit()

    def ao_entrar_estado(self, estado):
        if estado == ESTADO_MENU:
            self.tocar_musica_menu()
        else:
            self.parar_musica_menu()

        if estado == ESTADO_DERROTA:
            self.tocar(self.som_game_over)

    def executar(self):
        while True:
            dt = self.relogio.tick(FPS)

            if self.estado != self.estado_anterior:
                self.ao_entrar_estado(self.estado)
                self.estado_anterior = self.estado

            self.processar_eventos()

            if self.estado == ESTADO_MENU:
                self.tela_menu()
            elif self.estado == ESTADO_JOGANDO:
                self.atualizar_jogo(dt)
                self.desenhar_jogo()
            elif self.estado == ESTADO_VITORIA:
                self.tela_fim(venceu=True)
            elif self.estado == ESTADO_DERROTA:
                self.tela_fim(venceu=False)

            pygame.display.flip()


if __name__ == "__main__":
    Jogo().executar()
