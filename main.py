import os
import time
import cv2
import numpy as np

from hand_utils import HandGestureDetector
from game_logic import SimpleAI, winner

# ================= CONFIGURACIÓN "SENIOR" =================
# Configuración de cámara para baja latencia
IDX = 0
cap = cv2.VideoCapture(IDX, cv2.CAP_DSHOW)
if not cap.isOpened():
    # Fallback si CAP_DSHOW falla en algunos sistemas
    cap = cv2.VideoCapture(IDX)
    if not cap.isOpened():
        raise RuntimeError("Error Crítico: Cámara no detectada.")

# Resolución HD estándar
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Rutas dinámicas (funciona en cualquier PC)
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
ASSETS = os.path.join(SCRIPT_DIR, "assets")

# PALETA DE COLORES (Estilo "Cyberpunk Clean")
# Formato BGR (Blue, Green, Red)
C_BG_DARK = (25, 25, 25)       # Gris casi negro (Fondo HUD)
C_ACCENT = (0, 255, 255)       # Cian eléctrico (Resaltados)
C_TEXT_MAIN = (245, 245, 245)  # Blanco humo (Texto general)
C_CPU = (100, 100, 255)        # Rojo neón suave (Enemigo)
C_PLAYER = (255, 200, 100)     # Azul neón suave (Jugador)

FILEMAP = {
    "logo": "Logo.png",
    "1": "1.png", "2": "2.png", "3": "3.png",
    "Piedra": "Piedra.png", "Papel": "Papel.png", "Tijeras": "Tijera.png",
}


# ================= UTILIDADES GRÁFICAS =================
def load_asset(filename):
    """Carga assets asegurando formato BGRA (Transparencia)."""
    path = os.path.join(ASSETS, filename)
    if not os.path.isfile(path):
        # Manejo de error silencioso: crea una imagen negra si falta el asset
        print(f"Warning: Asset {filename} not found.")
        return np.zeros((100, 100, 4), dtype=np.uint8)

    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    # Convertir a BGRA si viene en BGR o Grises
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
    elif img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    return img


def draw_hud(frame, p_score, c_score, state):
    """Dibuja la interfaz de usuario (Barras superior e inferior)."""
    h, w = frame.shape[:2]

    # Crear overlay para transparencias
    overlay = frame.copy()

    # Barra Superior (Scoreboard)
    cv2.rectangle(overlay, (0, 0), (w, 80), C_BG_DARK, -1)

    # Barra Inferior (Status/Instrucciones)
    cv2.rectangle(overlay, (0, h - 60), (w, h), C_BG_DARK, -1)

    # Aplicar transparencia (Alpha blending)
    alpha = 0.85
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Texto de Puntajes
    # Jugador (Izquierda)
    cv2.putText(
        frame,
        f"PLAYER: {p_score}",
        (40, 55),
        cv2.FONT_HERSHEY_DUPLEX,
        1.0,
        C_PLAYER,
        2,
        cv2.LINE_AA
    )

    # CPU (Derecha) - Cálculo de ancho para alinear a la derecha
    txt_cpu = f"CPU: {c_score}"
    tsize = cv2.getTextSize(txt_cpu, cv2.FONT_HERSHEY_DUPLEX, 1.0, 2)[0]
    cv2.putText(
        frame,
        txt_cpu,
        (w - 40 - tsize[0], 55),
        cv2.FONT_HERSHEY_DUPLEX,
        1.0,
        C_CPU,
        2,
        cv2.LINE_AA
    )

    # Separador central visual
    cv2.line(frame, (w // 2, 15), (w // 2, 65), (100, 100, 100), 2)


def blend_centered(bg, fg, y_offset=0, scale=1.0):
    """Superpone una imagen con transparencia en el centro del frame."""
    if fg is None:
        return

    h_bg, w_bg = bg.shape[:2]
    h_fg, w_fg = fg.shape[:2]

    # Escalar si es necesario
    if scale != 1.0:
        w_fg = int(w_fg * scale)
        h_fg = int(h_fg * scale)
        fg = cv2.resize(fg, (w_fg, h_fg), interpolation=cv2.INTER_AREA)

    # Calcular posición centrada
    x = (w_bg - w_fg) // 2
    y = (h_bg - h_fg) // 2 + y_offset

    # Validar límites
    if x < 0 or y < 0 or x + w_fg > w_bg or y + h_fg > h_bg:
        return  # Evita crash si la imagen es más grande que el frame

    # Fusión Alpha (Pixel a pixel)
    alpha_ch = fg[:, :, 3] / 255.0
    for c in range(3):
        bg[y:y + h_fg, x:x + w_fg, c] = (
            alpha_ch * fg[:, :, c] +
            (1.0 - alpha_ch) * bg[y:y + h_fg, x:x + w_fg, c]
        )


# ================= INICIO DEL JUEGO =================
# Carga de recursos
ASSET_STORE = {k: load_asset(v) for k, v in FILEMAP.items()}

# Inicialización de objetos
detector = HandGestureDetector(conf=0.7)
ia = SimpleAI()

# Estado Global
state = "IDLE"      # Estados: IDLE, COUNTDOWN, SHOW_RESULT
timer_start = 0
p_score, c_score = 0, 0
p_move, c_move = None, None
last_detected = None

try:
    while True:
        success, frame = cap.read()
        if not success:
            break

        # Espejo (Flip horizontal) para sensación natural
        frame = cv2.flip(frame, 1)
        H, W = frame.shape[:2]

        # 1. DETECCIÓN (Siempre corre para feedback continuo)
        gesto, _, frame = detector.detect(frame)
        if gesto:
            last_detected = gesto

        # 2. RENDERIZADO BASE (HUD)
        draw_hud(frame, p_score, c_score, state)

        # 3. LÓGICA DE ESTADOS
        if state == "IDLE":
            # Pantalla de espera
            blend_centered(frame, ASSET_STORE["logo"], y_offset=-20, scale=0.8)
            msg = "Presiona [S] para Iniciar  |  [Q] Salir"

            # Texto centrado abajo
            tsize = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.putText(
                frame,
                msg,
                ((W - tsize[0]) // 2, H - 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                C_TEXT_MAIN,
                2,
                cv2.LINE_AA
            )

        elif state == "COUNTDOWN":
            elapsed = time.time() - timer_start

            if elapsed < 1:
                img_num = ASSET_STORE["3"]
            elif elapsed < 2:
                img_num = ASSET_STORE["2"]
            elif elapsed < 3:
                img_num = ASSET_STORE["1"]
            else:
                # FIN DEL CONTEO: Calcular resultado
                # Default si no detecta
                p_move = last_detected if last_detected else "Piedra"
                c_move = ia.choose()
                ia.observe(p_move)  # IA aprende

                # Determinar ganador
                result = winner(p_move, c_move)
                if result == "player":
                    p_score += 1
                elif result == "cpu":
                    c_score += 1

                state = "SHOW_RESULT"
                img_num = None

            # Renderizar número del conteo
            if state == "COUNTDOWN" and img_num is not None:
                blend_centered(frame, img_num, scale=0.8)
                cv2.putText(
                    frame,
                    "¡Prepara tu mano!",
                    ((W // 2) - 130, H - 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    C_ACCENT,
                    2,
                    cv2.LINE_AA
                )

        elif state == "SHOW_RESULT":
            # Mostrar jugada de la CPU (Izquierda o Centro desplazado)
            # Usamos blend manual para posicionar la imagen CPU
            cpu_img = ASSET_STORE.get(c_move)
            if cpu_img is not None:
                # Posicionar a la izquierda del centro
                h_img, w_img = cpu_img.shape[:2]
                target_x = 100
                target_y = (H - h_img) // 2

                # Fusión manual simple
                alpha_s = cpu_img[:, :, 3] / 255.0
                roi = frame[target_y:target_y + h_img, target_x:target_x + w_img]
                for c in range(3):
                    roi[:, :, c] = (
                        alpha_s * cpu_img[:, :, c] +
                        (1.0 - alpha_s) * roi[:, :, c]
                    )

            # Textos de resultado
            cv2.putText(
                frame,
                f"CPU eligio: {c_move}",
                (100, H // 2 + 180),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                C_CPU,
                2,
                cv2.LINE_AA
            )

            msg = "Presiona [D] Siguiente Ronda"
            tsize = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.putText(
                frame,
                msg,
                ((W - tsize[0]) // 2, H - 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                C_TEXT_MAIN,
                2,
                cv2.LINE_AA
            )

        # 4. CONTROL DE INPUTS
        cv2.imshow("Senior Dev Rock-Paper-Scissors", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('s') and state == "IDLE":
            state = "COUNTDOWN"
            timer_start = time.time()
        elif key == ord('d') and state == "SHOW_RESULT":
            state = "COUNTDOWN"
            timer_start = time.time()
            p_move, c_move = None, None

finally:
    cap.release()
    cv2.destroyAllWindows()
