import unittest
from game_logic import winner, SimpleAI


class TestGameLogic(unittest.TestCase):

    def test_winner_rules(self):
        """Verifica que las reglas de Piedra/Papel/Tijeras sean correctas."""
        self.assertEqual(winner("Piedra", "Tijeras"), "player")
        self.assertEqual(winner("Papel", "Piedra"), "player")
        self.assertEqual(winner("Tijeras", "Papel"), "player")
        self.assertEqual(winner("Piedra", "Papel"), "cpu")
        self.assertEqual(winner("Piedra", "Piedra"), "draw")

    def test_ai_observation(self):
        """Verifica que la IA recuerde los movimientos."""
        ia = SimpleAI(memoria=5)
        ia.observe("Piedra")
        ia.observe("Piedra")
        # La memoria debe contener las jugadas
        self.assertIn("Piedra", ia.hist)
        self.assertEqual(len(ia.hist), 2)

    def test_ai_prediction(self):
        """
        Si el jugador siempre saca Piedra, la IA debería aprender
        y eventualmente sacar Papel (el contra-movimiento).
        """
        ia = SimpleAI(memoria=10)
        # Entrenamos a la IA con un patrón obvio
        for _ in range(10):
            ia.observe("Piedra")

        # La IA debería predecir que sacaremos Piedra, y elegir Papel
        counter_move = ia.choose()
        self.assertEqual(counter_move, "Papel")


if __name__ == '__main__':
    unittest.main()
