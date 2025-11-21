from django.shortcuts import render

# Create your views here.
import yt_dlp
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response

SAVE_PATH = "downloads"  # Carpeta para guardar archivos
#FFMPEG_PATH = "ffmpeg"
#COOKIES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
FFMPEG_PATH = r"C:\Users\user\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin"
os.makedirs(SAVE_PATH, exist_ok=True)


def clean_url(url):
    return url.split("&")[0]
INVIDIOUS = "https://inv.nadeko.net"




def descargar_mp3(link):
    ydl_opts_mp3 = {
        'format': 'bestaudio/best',
        #"cookiefile": COOKIES_PATH,
        'outtmpl': f'{SAVE_PATH}/%(title)s.%(ext)s',
        'ffmpeg_location': FFMPEG_PATH,
        'keepvideo': True, 
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],'extractor_args': {
            'youtube': {
                'player_client': ['web_embedded', 'android', 'ios']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10)'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts_mp3) as ydl:
        ydl.download([link])


@api_view(['POST'])
def descargar_video(request):
    try:
        url = request.data.get("url")
        if not url:
            return Response({"error": "Debe enviar la URL"}, status=400)

        link = clean_url(url)

        # Configuración de descarga MP4
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f'{SAVE_PATH}/%(title)s.%(ext)s',
            
            'merge_output_format': 'mp4',

            # *** Aquí está la clave que evita el error ***
            'extractor_args': {
                'youtube': {
                    'player_client': ['web_embedded', 'android', 'ios']
                }
            },

            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10)'
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            title = info.get('title')

            ydl.download([link])

        # Descargar MP3 también
        descargar_mp3(link)

        # Buscar archivo descargado MP4
        files = os.listdir(SAVE_PATH)
        latest_file = max([os.path.join(SAVE_PATH, f) for f in files], key=os.path.getctime)
        file_size = os.path.getsize(latest_file) / (1024 * 1024)

        return Response({
            "titulo": title,
            "archivo": os.path.basename(latest_file),
            "peso_mb": round(file_size, 2),
            "ruta": os.path.abspath(latest_file),
            "mensaje": "Descarga completada"
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)
