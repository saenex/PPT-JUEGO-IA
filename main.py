import os
import time
import cv2

from hand_utils import HandGestureDetector
from game_logic import SimpleAI, winner, MOVES


# Configuración de captura de video
# Se prioriza CAP_DSHOW en Windows para minimizar el buffer de entrada.
IDX = 0
cap = cv2.VideoCapture(IDX, cv2.CAP_DSHOW)
if not cap.isOpened():
    raise RuntimeError("Error crítico: No se pudo inicializar la cámara.")

cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


# Gestión de Assets y Rutas
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
ASSETS = os.path.join(SCRIPT_DIR, "assets")

FILEMAP = {
    "logo": "Logo.png",
    "1": "1.png",
    "2": "2.png",
    "3": "3.png",
    "Piedra": "Piedra.png",
    "Papel": "Papel.png",
    "Tijeras": "Tijera.png",
}


def _ensure_bgra(img):
    """Normaliza la imagen a 4 canales (BGRA) para composición segura."""
    if img is None:
        return None
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    elif img.shape[2] != 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    return img


def load_image_strict(filename):
    """
    Carga assets en modo estricto.
    Lanza excepción si el archivo no existe o está corrupto.
    """
    path = os.path.join(ASSETS, filename)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Asset no encontrado: {path}")
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise RuntimeError(f"Error de lectura en asset: {path}")
    return _ensure_bgra(img)


def blend_roi(dst, src_bgra, x, y, w_dst, h_dst):
    """
    Superpone una imagen RGBA sobre una región de interés (ROI) en dst.
    Maneja el escalado y la mezcla de canales alfa.
    """
    if src_bgra is None:
        return
    src = cv2.resize(src_bgra, (w_dst, h_dst), cv2.INTER_AREA)
    b, g, r, a = cv2.split(src)
    roi = dst[y:y + h_dst, x:x + w_dst].astype("float32")
    fg = cv2.merge([b, g, r]).astype("float32")

    # Normalización de alfa para mezcla
    alpha = (a.astype("float32") / 255.0)[..., None]
    out = alpha * fg + (1.0 - alpha) * roi
    dst[y:y + h_dst, x:x + w_dst] = out.astype(dst.dtype)


def draw_text(img, text, x, y, scale=1.0, color=(255, 255, 255), thick=2):
    """Renderiza texto en pantalla manteniendo consistencia tipográfica."""
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                scale, color, thick)


# Pre-carga de recursos estáticos
IMG = {}
for key, fname in FILEMAP.items():
    IMG[key] = load_image_strict(fname)


# Inicialización de Lógica y Estado
detector = HandGestureDetector()
ia = SimpleAI(memoria=8)

pts_player = 0
pts_cpu = 0

# Definición de la Máquina de Estados
STATE_IDLE = 0       # Menú principal / Espera
STATE_COUNTDOWN = 1  # Secuencia de juego (3, 2, 1)
STATE_SHOW = 2       # Resolución de la ronda

state = STATE_IDLE
count_started_at = 0.0
COUNT_DUR = 0.9

player_move = None
cpu_move = None
last_valid_gesture = None

# Constantes de UI
COLOR_CPU = (0, 0, 140)
COLOR_PLAYER = (255, 255, 160)
COLOR_TEXT = (255, 255, 255)


# Bucle Principal de Renderizado
try:
    while True:
        # 1. Captura y Preprocesamiento
        ok, frame = cap.read()
        if not ok:
            continue
        frame = cv2.flip(frame, 1)  # Espejo horizontal para UX natural
        h, w = frame.shape[:2]
        mid = w // 2

        # 2. Gestión de Estados Visuales
        if state == STATE_IDLE:
            blend_roi(frame, IMG["logo"], 0, 0, mid, h)

        elif state == STATE_COUNTDOWN:
            # Lógica de temporizador para assets 3-2-1
            elapsed = time.time() - count_started_at
            if elapsed < COUNT_DUR:
                stage = "3"
            elif elapsed < 2 * COUNT_DUR:
                stage = "2"
            else:
                stage = "1"

            num_img = IMG.get(stage)
            if num_img is not None:
                box_w, box_h = 300, 300
                nx = mid - box_w // 2
                ny = h // 2 - box_h // 2
                blend_roi(frame, num_img, nx, ny, box_w, box_h)

            # Transición de estado y cálculo de resultado
            if elapsed >= 3 * COUNT_DUR:
                player_move = (last_valid_gesture
                               if last_valid_gesture in MOVES
                               else "Piedra")

                # Turno de la IA
                cpu_move = ia.choose()
                ia.observe(player_move)

                # Determinación del ganador
                res = winner(player_move, cpu_move)
                if res == "player":
                    pts_player += 1
                elif res == "cpu":
                    pts_cpu += 1

                state = STATE_SHOW

        elif state == STATE_SHOW:
            # Renderizado del movimiento de la CPU (Izquierda)
            if cpu_move in IMG:
                blend_roi(frame, IMG[cpu_move], 0, 0, mid, h)

        # 3. Renderizado del HUD (Puntajes y Etiquetas)
        draw_text(frame, f"CPU: {pts_cpu}", 40, 60, 1.2, COLOR_CPU, 3)
        draw_text(frame, f"Jugador: {pts_player}", mid + 40, 60,
                  1.2, COLOR_PLAYER, 3)

        if state == STATE_SHOW and cpu_move:
            label = f"{cpu_move}"
            tsize, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX,
                                       1.0, 2)
            label_x = max((mid - 20) - tsize[0], 40)
            draw_text(frame, label, label_x, 60, 1.0, COLOR_CPU, 2)

        # 4. Instrucciones Contextuales (Footer)
        if state == STATE_IDLE:
            instr = "Presiona 'S' para iniciar  |  'Q' para salir"
        elif state == STATE_COUNTDOWN:
            instr = "Manten tu gesto al final"
        else:
            instr = "Presiona 'D' para la siguiente ronda  |  'Q' para salir"

        isize, _ = cv2.getTextSize(instr, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        draw_text(frame, instr, (w - isize[0]) // 2, h - 20,
                  1.0, COLOR_TEXT, 2)

        # 5. Pipeline de Visión Computacional
        gesto, meta, frame = detector.detect(frame)
        if gesto in MOVES:
            last_valid_gesture = gesto

        # 6. Salida de Video y Control de Input
        cv2.imshow("Juego SNX", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        if state == STATE_IDLE and key == ord("s"):
            state = STATE_COUNTDOWN
            count_started_at = time.time()
            last_valid_gesture = None
            player_move = None
            cpu_move = None

        if state == STATE_SHOW and key == ord("d"):
            state = STATE_COUNTDOWN
            count_started_at = time.time()
            last_valid_gesture = None
            player_move = None
            cpu_move = None

finally:
    cap.release()
    cv2.destroyAllWindows()
