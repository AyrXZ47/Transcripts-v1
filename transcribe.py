import os
import argparse
import subprocess
from faster_whisper import WhisperModel
import torch
from tqdm import tqdm

def format_srt_timestamp(seconds):
    """Converts seconds to SRT timestamp format (HH:MM:SS,ms)."""
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)
    hours = int(milliseconds / 3_600_000)
    milliseconds %= 3_600_000
    minutes = int(milliseconds / 60_000)
    milliseconds %= 60_000
    seconds = int(milliseconds / 1000)
    milliseconds %= 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def transcribe_media(media_path, model_size="medium", max_line_length=22):
    """
    Transcribes a media file using faster-whisper, generating a .txt file and a
    dynamic .srt file ideal for social media.
    """
    print(f"🚀 Iniciando transcripción para: {media_path}")
    print(f"🤖 Modelo: {model_size}, Longitud máx. SRT: {max_line_length}")

    if not os.path.exists(media_path):
        print(f"❌ Error: Archivo no encontrado en {media_path}")
        return

    temp_audio_path = "temp_audio.wav"

    try:
        print("🔊 Extrayendo audio con ffmpeg...")
        subprocess.run(
            ['ffmpeg', '-i', media_path, '-y', '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', temp_audio_path],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print("✅ Audio extraído.")

        device = "cpu"
        compute_type = "int8"
        
        print(f"🧠 Cargando modelo '{model_size}' en dispositivo 'CPU' con tipo de cómputo 'int8'...")

        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print("✅ Modelo cargado.")

        print("🎤 Transcribiendo... (esto puede tardar)")
        segments, info = model.transcribe(temp_audio_path, beam_size=5, word_timestamps=True)
        print(f"✅ Transcripción completa. Idioma detectado: {info.language} (Probabilidad: {info.language_probability:.2f})")

        base_name = os.path.splitext(media_path)[0]
        txt_path = base_name + ".txt"
        srt_path = base_name + ".srt"
        
        srt_content = []
        srt_counter = 1
        full_text = ""

        # Usamos tqdm para una barra de progreso
        print("✍️ Procesando segmentos y generando archivos...")
        segment_list = list(segments)
        for segment in tqdm(segment_list, unit="segment"):
            full_text += segment.text.strip() + " "
            
            # --- Lógica para SRT dinámico usando word_timestamps ---
            if not segment.words:
                continue

            current_line = ""
            line_start_time = segment.words[0].start
            
            for i, word in enumerate(segment.words):
                # Limpia la palabra antes de añadirla
                word_text = word.word.strip()
                if not word_text:
                    continue

                if len(current_line + " " + word_text) > max_line_length:
                    srt_content.append(str(srt_counter))
                    srt_content.append(f"{format_srt_timestamp(line_start_time)} --> {format_srt_timestamp(word.start)}")
                    srt_content.append(current_line.strip())
                    srt_content.append("")
                    srt_counter += 1
                    current_line = word_text
                    line_start_time = word.start
                else:
                    if current_line:
                       current_line += " " + word_text
                    else:
                       current_line = word_text

            if current_line.strip():
                srt_content.append(str(srt_counter))
                srt_content.append(f"{format_srt_timestamp(line_start_time)} --> {format_srt_timestamp(segment.end)}")
                srt_content.append(current_line.strip())
                srt_content.append("")
                srt_counter += 1
        
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(full_text.strip())
        print(f"📄 Archivo de texto guardado en: {txt_path}")

        with open(srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_content))
        print(f"🎬 Archivo SRT guardado en: {srt_path}")

    except Exception as e:
        print(f"🚨 Ocurrió un error: {e}")
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            print("🧹 Archivo de audio temporal eliminado.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe media files using faster-whisper.")
    parser.add_argument("media_path", type=str, help="Ruta al archivo de audio/video.")
    parser.add_argument("--model_size", type=str, default="medium", help="Modelo a usar (e.g., tiny, base, small, medium, large-v3).")
    parser.add_argument("--max_line_length", type=int, default=22, help="Máximo de caracteres por línea en SRT.")
    args = parser.parse_args()
    transcribe_media(args.media_path, args.model_size, args.max_line_length)