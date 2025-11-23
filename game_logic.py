import random
from collections import Counter, deque

# Movimientos válidos del juego
MOVES = ["Piedra", "Papel", "Tijeras"]


def winner(jugador, cpu):
    """
    Calcula el ganador de una ronda.
    Devuelve: 'player', 'cpu' o 'draw'.
    """
    if jugador == cpu:
        return "draw"
    reglas = {"Piedra": "Tijeras", "Papel": "Piedra", "Tijeras": "Papel"}
    return "player" if reglas[jugador] == cpu else "cpu"


class SimpleAI:
    """
    IA sencilla:
      - Guarda las últimas N jugadas del jugador.
      - Supone que repetirá la más frecuente.
      - Selecciona el contra-movimiento.
    """
    def __init__(self, memoria=8):
        self.hist = deque(maxlen=memoria)

    def observe(self, jugada):
        if jugada in MOVES:
            self.hist.append(jugada)

    def choose(self):
        if not self.hist:
            return random.choice(MOVES)
        freq = Counter(self.hist)
        probable = freq.most_common(1)[0][0]
        contra = {"Piedra": "Papel", "Papel": "Tijeras", "Tijeras": "Piedra"}
        return contra[probable]
