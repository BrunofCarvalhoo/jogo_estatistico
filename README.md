# Jogo da Distribuição de Probabilidade - Estilo "The Wall"

Este projeto é um jogo interativo desenvolvido em Python utilizando a biblioteca **Pygame**. Ele combina um quiz de perguntas e respostas com uma simulação estatística estilo "The Wall" (Tabuleiro de Galton), servindo como uma ferramenta educativa para visualização de **Probabilidade** e **Estatística**.

## 📊 Sobre o Projeto

O objetivo do jogo é demonstrar de forma lúdica conceitos estatísticos fundamentais. Ao responder perguntas corretamente, o jogador ganha o direito de jogar bolas no tabuleiro.

O projeto destaca:
-   **Distribuição Normal / Binomial**: A movimentação das bolas pelos pinos tende a formar uma curva de sino (Curva de Gauss).
-   **Comparação em Tempo Real**: O jogo exibe dois gráficos lado a lado:
    -   **Distribuição Empírica (Frequência)**: Onde as bolas realmente caíram durante o jogo.
    -   **Distribuição Teórica**: A probabilidade matemática esperada de onde as bolas deveriam cair.

## 🎮 Funcionalidades

-   **Quiz Interativo**: Perguntas de conhecimentos gerais para ganhar pontos.
-   **Simulação Física**: As bolas caem e colidem com pinos, desviando aleatoriamente para a esquerda ou direita (simulando eventos de Bernoulli sucessivos).
-   **Gráficos Dinâmicos**: Visualização contínua das barras de frequência conforme as bolas acumulam nas caçapas.
-   **Ranking**: Sistema de pontuação local para salvar os melhores jogadores.
-   **Modo de Testes**: Um menu específico para simular o lançamento de várias bolas rapidamente e observar a lei dos grandes números em ação.

## 🚀 Como Rodar o Projeto

Siga os passos abaixo para configurar e executar o jogo em seu computador.

### Pré-requisitos

Você precisa ter o **Python** instalado em sua máquina. Caso não tenha, faça o download [aqui](https://www.python.org/downloads/).

### 1. Clonar ou Baixar o Projeto

Se você tiver o Git instalado:
```bash
git clone <url-do-repositorio>
cd jogo_estatistico
```
Ou simplesmente baixe o código fonte e extraia em uma pasta.

### 2. Instalar Dependências

O projeto utiliza a biblioteca `pygame`. Abra o terminal (Prompt de Comando ou PowerShell) na pasta do projeto e execute:

```bash
pip install pygame
```

### 3. Executar o Jogo

Com as dependências instaladas, execute o arquivo principal:

```bash
python jogo.py
```

## 🕹️ Como Jogar

1.  **Menu Principal**: Escolha "JOGAR" para iniciar o desafio ou "TESTES" para apenas simular.
2.  **Quiz**: Responda a pergunta clicando na alternativa correta.
3.  **The Wall**: Se acertar, escolha a posição de lançamento da bola usando as **SETAS** (Esquerda/Direita) e pressione **ESPAÇO** para soltar.
4.  **Pontuação**: Bolas verdes (acertos) somam pontos, bolas vermelhas (erros) subtraem. Os valores variam dependendo da caçapa onde a bola cai (valores extremos são mais raros e valiosos).

## 🛠️ Tecnologias Utilizadas

-   **Python 3**
-   **Pygame** (Gráficos e lógica de jogo)
-   **JSON** (Persistência de dados do ranking)
