import cv2
import mediapipe as mp


class HandGestureDetector:
    """
    Detector de gestos optimizado con estilo visual 'Tech'.
    Cumple estrictamente con PEP8.
    """

    def __init__(self, max_hands=1, conf=0.7, track_conf=0.6):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            model_complexity=0,
            max_num_hands=max_hands,
            min_detection_confidence=conf,
            min_tracking_confidence=track_conf,
        )
        self.drawer = mp.solutions.drawing_utils
        # Configuración de colores visuales (Cian y Magenta)
        self.landmark_spec = self.drawer.DrawingSpec(
            color=(0, 255, 255), thickness=2, circle_radius=2
        )
        self.connection_spec = self.drawer.DrawingSpec(
            color=(255, 0, 255), thickness=2
        )

    def _contar_dedos(self, landmarks, mano):
        """Lógica interna de conteo de dedos."""
        tips = [4, 8, 12, 16, 20]
        pips = [3, 6, 10, 14, 18]
        dedos = []

        # 1. Pulgar (Comparación horizontal)
        x_punta = landmarks[tips[0]][0]
        x_ip = landmarks[pips[0]][0]

        pulgar_levantado = False
        if mano == "Right":
            pulgar_levantado = x_punta > x_ip
        else:
            pulgar_levantado = x_punta < x_ip
        dedos.append(1 if pulgar_levantado else 0)

        # 2. Otros 4 dedos (Comparación vertical)
        for ti, pi in zip(tips[1:], pips[1:]):
            y_punta = landmarks[ti][1]
            y_pip = landmarks[pi][1]
            dedos.append(1 if y_punta < y_pip else 0)

        return sum(dedos), dedos

    def _clasificar(self, total, arr):
        """Clasificador de reglas del juego."""
        if total == 0:
            return "Piedra"
        if total == 5:
            return "Papel"

        # Lógica de tijeras
        is_classic_scissors = (arr == [0, 1, 1, 0, 0])
        is_weird_scissors = (total == 2 and arr[1] and arr[2])

        if is_classic_scissors or is_weird_scissors:
            return "Tijeras"

        return None

    def detect(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        gesto = None
        meta = {"wrist_y": 0, "is_fist": False}

        if results.multi_hand_landmarks and results.multi_handedness:
            mano_lm = results.multi_hand_landmarks[0]
            classification = results.multi_handedness[0].classification[0]
            mano_tipo = classification.label

            # Dibujar esqueleto
            self.drawer.draw_landmarks(
                frame,
                mano_lm,
                self.mp_hands.HAND_CONNECTIONS,
                self.landmark_spec,
                self.connection_spec,
            )

            # Extraer coordenadas
            lm = [(p.x, p.y) for p in mano_lm.landmark]
            meta["wrist_y"] = lm[0][1]

            # Procesar lógica
            total, arr = self._contar_dedos(lm, mano_tipo)
            gesto = self._clasificar(total, arr)
            meta["is_fist"] = (gesto == "Piedra")

            # Renderizado de texto (Feedback visual)
            h, w, _ = frame.shape
            wx, wy = int(lm[0][0] * w), int(lm[0][1] * h)

            if gesto:
                cv2.putText(
                    frame,
                    f"{gesto.upper()}",
                    (wx + 20, wy),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 255),
                    2,
                    cv2.LINE_AA
                )

        return gesto, meta, frame
