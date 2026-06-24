# Defensor Espacial

Demo de jogo 2D desenvolvido em Python com a biblioteca **Pygame**, para a
disciplina **Linguagem de Programação Aplicada (UNINTER)**.

## Sobre o jogo

Você controla uma nave e precisa defender o espaço dos inimigos que descem pela
tela. O jogo possui menu, comandos exibidos na tela inicial, desafio crescente e
condições de vitória e derrota.

| Requisito do trabalho        | Como foi atendido                                  |
|------------------------------|----------------------------------------------------|
| Jogo 2D (não console)        | Janela gráfica 800x600 com Pygame                  |
| Controle do jogador          | Mover a nave e atirar                              |
| Desafio                      | Inimigos surgem continuamente em posições aleatórias |
| Condição de vitória          | Destruir 20 inimigos                               |
| Condição de derrota          | Perder as 3 vidas                                  |
| Menu com comandos            | Tela inicial lista todos os controles              |

## Comandos

- **Setas** ou **A / D** — Mover a nave
- **Espaço** — Atirar
- **ENTER** — Iniciar / reiniciar
- **M** — Voltar ao menu (telas de fim)
- **ESC** — Sair

## Como rodar (desenvolvimento)

```bash
pip install -r requirements.txt
python main.py
```

## Como gerar o executável (.exe) para Windows

Conforme orientado no material da disciplina, use o **PyInstaller**:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "DefensorEspacial" main.py
```

O executável será criado na pasta `dist/`.

> **Importante (Dica 2 do material):** os assets (imagens, sons) **não** são
> compilados junto com o `.exe`. Caso você adicione assets, copie a pasta
> `assets/` para junto do executável, mantendo a mesma hierarquia de pastas do
> projeto.

Para entrega, gere o **ZIP** contendo o `.exe` + a pasta `assets`.
