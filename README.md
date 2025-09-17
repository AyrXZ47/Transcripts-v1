# Proyecto de Transcripción de Medios

Este proyecto utiliza `faster-whisper` para transcribir archivos de audio o video. Está configurado para ejecutarse de manera eficiente en **CPU**.

Genera dos archivos de salida:
1.  Un archivo de texto plano (`.txt`) con la transcripción completa.
2.  Un archivo de subtítulos (`.srt`) con formato dinámico, ideal para redes sociales, donde cada línea tiene una longitud máxima controlada.

## Requisitos

- **ffmpeg**: Debe estar instalado y accesible en el PATH del sistema. Se usa para la extracción de audio.
- **Python 3.11+**
- Un entorno virtual de Python (recomendado).

## Instalación

1.  **Clona o descarga el proyecto.**

2.  **Crea y activa un entorno virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instala las dependencias de Python:**
    ```bash
    pip install -r requirements.txt
    ```

## Uso

Ejecuta el script `transcribir.sh` pasando la ruta a tu archivo de video o audio como argumento.

**Sintaxis:**
```bash
./transcribir.sh "/ruta/al/archivo.mp4"
```

**Ejemplo:**
```bash
./transcribir.sh "/home/yovick/Videos/mi_video.mkv"
```

El script procesará el archivo y dejará los archivos `.txt` y `.srt` en el mismo directorio que el archivo de entrada.
