import urllib.request
import yt_dlp
import threading
import os
import glob

def _find_ffmpeg():
    """Busca el ejecutable ffmpeg en rutas conocidas de Windows."""
    # 1. Buscar en PATH normal
    import shutil
    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg:
        return os.path.dirname(ffmpeg)

    # 2. Ruta típica de winget
    winget_base = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Packages')
    pattern = os.path.join(winget_base, 'Gyan.FFmpeg*', '**', 'bin', 'ffmpeg.exe')
    matches = glob.glob(pattern, recursive=True)
    if matches:
        return os.path.dirname(matches[0])

    # 3. Ruta típica de choco
    choco_path = r'C:\ProgramData\chocolatey\bin'
    if os.path.exists(os.path.join(choco_path, 'ffmpeg.exe')):
        return choco_path

    return None

FFMPEG_LOCATION = _find_ffmpeg()

def search_youtube(query, num_results=5, success_callback=None, error_callback=None):
    """Realiza una búsqueda en YouTube o extrae información de un enlace y devuelve los resultados."""
    def _search():
        ydl_opts = {
            'extract_flat': 'in_playlist',
            'quiet': True,
            'no_warnings': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                is_url = query.startswith("http://") or query.startswith("https://")
                search_query = query if is_url else f"ytsearch{num_results}:{query}"
                
                result = ydl.extract_info(search_query, download=False)
                
                # Dependiendo de si es URL directa o búsqueda, la estructura cambia
                entries = result.get('entries', [result]) if 'entries' in result else [result]
                
                results = []
                for entry in entries:
                    if not entry: continue

                    # Intentamos obtener la URL de la miniatura desde varias fuentes posibles:
                    # 1. Lista 'thumbnails' (resultados de búsqueda)
                    # 2. Campo 'thumbnail' directo (URLs directas de video)
                    # Preferimos JPEG sobre WebP para mayor compatibilidad con Pillow
                    thumb_url = ''
                    thumbnails_list = entry.get('thumbnails')
                    if thumbnails_list:
                        # Buscar el de mejor calidad que sea JPEG
                        jpg_thumbs = [t for t in thumbnails_list if t.get('url', '').endswith('.jpg') or 'vi/' in t.get('url', '')]
                        if jpg_thumbs:
                            thumb_url = jpg_thumbs[-1].get('url', '')
                        else:
                            thumb_url = thumbnails_list[-1].get('url', '')
                    
                    # Fallback al campo 'thumbnail' plano (habitual en URLs directas)
                    if not thumb_url:
                        thumb_url = entry.get('thumbnail', '')

                    thumb_data = None
                    if thumb_url:
                        try:
                            req = urllib.request.Request(thumb_url, headers={'User-Agent': 'Mozilla/5.0'})
                            thumb_data = urllib.request.urlopen(req, timeout=5).read()
                        except:
                            pass


                    # Para enlaces directos, la url original suele estar en 'webpage_url' o 'original_url'
                    vid_url = entry.get('webpage_url', entry.get('original_url', entry.get('url', query if is_url else '')))
                    
                    results.append({
                        'title': entry.get('title', 'Sin Título'),
                        'uploader': entry.get('uploader', entry.get('channel', 'Desconocido')),
                        'url': vid_url,
                        'duration': entry.get('duration', 0),
                        'thumbnail_data': thumb_data
                    })
                    
                    if is_url: # Si es un solo enlace, solo tomamos el primer resultado
                        break

                if success_callback:
                    success_callback(results)
        except Exception as e:
            if error_callback:
                error_callback(str(e))
                
    # Ejecutamos la búsqueda en un hilo para no bloquear la UI
    threading.Thread(target=_search, daemon=True).start()

def download_media(url, format_type, quality, download_path, progress_callback=None, finished_callback=None, error_callback=None):
    """Descarga el video o audio de la URL proporcionada."""
    def _download():
        try:
            # Configuración base
            ydl_opts = {
                'outtmpl': f'{download_path}/%(title)s.%(ext)s',
                'quiet': True,
                'no_warnings': True,
            }

            # Inyectar ruta de ffmpeg si se encontró
            if FFMPEG_LOCATION:
                ydl_opts['ffmpeg_location'] = FFMPEG_LOCATION

            # Configuración según el formato (Video MP4 o Audio MP3)
            if format_type == "Audio MP3":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192' if quality == 'Alta' else '128',
                }]
            else: # Video MP4
                ydl_opts['merge_output_format'] = 'mp4'

                if quality == "Alta":
                    ydl_opts['format'] = "bestvideo[vcodec~='^avc1'][ext=mp4]+bestaudio[acodec=mp4a][ext=m4a]/bestvideo[vcodec~='^avc'][ext=mp4]+bestaudio[ext=m4a]/best"
                elif quality == "Media":
                    ydl_opts['format'] = "bestvideo[height<=720][vcodec~='^avc1'][ext=mp4]+bestaudio[acodec=mp4a][ext=m4a]/bestvideo[height<=720][vcodec~='^avc'][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]"
                else:
                    ydl_opts['format'] = "bestvideo[height<=480][vcodec~='^avc1'][ext=mp4]+bestaudio[acodec=mp4a][ext=m4a]/bestvideo[height<=480][vcodec~='^avc'][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]"

                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }]

            # Hook de progreso
            def my_hook(d):
                if d['status'] == 'downloading':
                    # Calcular porcentaje de descarga
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                    if total_bytes:
                        downloaded_bytes = d.get('downloaded_bytes', 0)
                        percentage = downloaded_bytes / total_bytes
                        speed = d.get('_speed_str', 'N/A')
                        eta = d.get('_eta_str', 'N/A')
                        
                        if progress_callback:
                            progress_callback(percentage, speed, eta)
                elif d['status'] == 'finished':
                    if progress_callback:
                        progress_callback(1.0, '0 KiB/s', '00:00')

            ydl_opts['progress_hooks'] = [my_hook]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if finished_callback:
                finished_callback()

        except Exception as e:
            if error_callback:
                error_callback(str(e))

    # Ejecutamos la descarga en un hilo para no bloquear la UI
    threading.Thread(target=_download, daemon=True).start()
