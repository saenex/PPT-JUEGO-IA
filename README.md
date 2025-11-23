# AI Gesture Control: Rock-Paper-Scissors

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-green?style=flat&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand_Tracking-orange?style=flat)
![License](https://img.shields.io/badge/License-MIT-grey?style=flat)

> **[ Read in English ](#english) | [ Leer en Español ](#spanish)**

---

<a name="english"></a>
## 🇺🇸 English Documentation

A real-time computer vision application that implements a gesture recognition system using MediaPipe and OpenCV. The system competes against a probabilistic AI agent that analyzes player patterns using Markov chains.

### Key Features

* **Computer Vision Pipeline**: High-performance hand skeleton extraction and gesture classification operating at 60 FPS using vector geometry.
* **Adaptive Artificial Intelligence**: Implementation of `SimpleAI`, a probabilistic model based on historical frequency analysis (deque/Counter) to predict and counter human inputs.
* **Robust Architecture**: Modular design following SOLID principles, separating business logic (`game_logic.py`) from vision processing (`hand_utils.py`).
* **Production-Grade UI**: Custom HUD rendering with anti-aliasing and strict asset management system.

### Technical Stack

* **Core**: Python 3.10+
* **Vision**: OpenCV (cv2), MediaPipe Hands
* **Math/Logic**: NumPy, Collections (deque)

### Installation and Setup

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/saenex/PPT-JUEGO-IA.git](https://github.com/saenex/PPT-JUEGO-IA.git)
    cd PPT-JUEGO-IA
    ```

2.  **Set up the environment**
    ```bash
    python -m venv .venv
    # Windows
    .\.venv\Scripts\activate
    # Linux/MacOS
    source .venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application**
    ```bash
    python main.py
    ```

### Controls

| Key | Function | Description |
| :--- | :--- | :--- |
| **S** | Start | Initiates the countdown sequence for a new round. |
| **D** | Deal | Proceeds to the next round after result display. |
| **Q** | Quit | Terminates the application safely. |

---

<a name="spanish"></a>
## 🇪🇸 Documentación en Español

Aplicación de visión artificial en tiempo real que implementa un sistema de reconocimiento de gestos utilizando MediaPipe y OpenCV. El sistema compite contra un agente de IA probabilístico que analiza los patrones del jugador utilizando cadenas de Markov.

### Características Principales

* **Pipeline de Visión Artificial**: Extracción de esqueleto de mano de alto rendimiento y clasificación de gestos operando a 60 FPS mediante geometría vectorial.
* **Inteligencia Artificial Adaptativa**: Implementación de `SimpleAI`, un modelo probabilístico basado en análisis de frecuencia histórica (deque/Counter) para predecir y contrarrestar las entradas humanas.
* **Arquitectura Robusta**: Diseño modular siguiendo principios SOLID, separando la lógica de negocio (`game_logic.py`) del procesamiento de visión (`hand_utils.py`).
* **UI de Producción**: Renderizado de HUD personalizado con anti-aliasing y sistema estricto de gestión de assets.

### Stack Técnico

* **Núcleo**: Python 3.10+
* **Visión**: OpenCV (cv2), MediaPipe Hands
* **Matemáticas/Lógica**: NumPy, Collections (deque)

### Instalación y Configuración

1.  **Clonar el repositorio**
    ```bash
    git clone [https://github.com/saenex/PPT-JUEGO-IA.git](https://github.com/saenex/PPT-JUEGO-IA.git)
    cd PPT-JUEGO-IA
    ```

2.  **Configurar el entorno**
    ```bash
    python -m venv .venv
    # Windows
    .\.venv\Scripts\activate
    # Linux/MacOS
    source .venv/bin/activate
    ```

3.  **Instalar dependencias**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación**
    ```bash
    python main.py
    ```

### Controles

| Tecla | Función | Descripción |
| :--- | :--- | :--- |
| **S** | Iniciar | Inicia la secuencia de cuenta regresiva para una nueva ronda. |
| **D** | Siguiente | Procede a la siguiente ronda tras mostrar el resultado. |
| **Q** | Salir | Cierra la aplicación de forma segura. |