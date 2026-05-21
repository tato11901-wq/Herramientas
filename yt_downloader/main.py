import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import io
from config_manager import load_config, save_config
from downloader import search_youtube, download_media
import webbrowser

# Configuración de apariencia
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("dark-blue")  

# Colores YouTube Dark Mode
BG_COLOR = "#0F0F0F"
FRAME_COLOR = "#181818"
BORDER_COLOR = "#303030"
TEXT_MAIN = "#F1F1F1"
TEXT_SUB = "#AAAAAA"
SEARCH_BG = "#121212"
BTN_SEARCH_BG = "#222222"
BTN_RED = "#FF0000"
BTN_RED_HOVER = "#CC0000"
BTN_SELECT = "#272727"
BTN_SELECT_HOVER = "#3F3F3F"

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Downloader")
        self.geometry("900x750")
        self.minsize(800, 700)
        self.configure(fg_color=BG_COLOR)
        
        # Iniciar maximizado (Windows)
        try:
            self.state('zoomed')
        except:
            pass
        
        # Cargar configuración
        self.config = load_config()
        self.current_download_path = self.config.get("download_path", "")
        self.target_url = ""

        self.build_ui()

    def build_ui(self):
        # Frame principal
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # --- SECCIÓN: BÚSQUEDA / URL ---
        self.search_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.search_frame.pack(fill="x", pady=(10, 20))

        # Contenedor centralizado para la barra de búsqueda tipo YouTube
        self.search_bar_container = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        self.search_bar_container.pack(expand=True)

        self.entry_search = ctk.CTkEntry(self.search_bar_container, width=500, height=45, placeholder_text="Buscar o pegar enlace...", fg_color=SEARCH_BG, text_color=TEXT_MAIN, border_color=BORDER_COLOR, corner_radius=20, font=("Roboto", 15))
        self.entry_search.pack(side="left", padx=(0, 5))
        self.entry_search.bind("<Return>", lambda event: self.start_search())

        self.btn_search = ctk.CTkButton(self.search_bar_container, text="Buscar", width=90, height=45, corner_radius=20, fg_color=BTN_SEARCH_BG, hover_color=BORDER_COLOR, text_color=TEXT_MAIN, font=("Roboto", 14, "bold"), command=self.start_search)
        self.btn_search.pack(side="left")

        # --- SECCIÓN: RESULTADOS DE BÚSQUEDA ---
        # Removido height fijo, fill="both" y expand=True para pantalla completa
        self.results_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color=BG_COLOR, border_color=BORDER_COLOR, border_width=0)
        self.results_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        self.lbl_results_status = ctk.CTkLabel(self.results_frame, text="Busca un video o pega un enlace para comenzar.", text_color=TEXT_SUB, font=("Roboto", 16))
        self.lbl_results_status.pack(pady=40)

        # --- SECCIÓN: OPCIONES Y DESCARGA ---
        self.options_frame = ctk.CTkFrame(self.main_frame, fg_color=FRAME_COLOR, corner_radius=15)
        self.options_frame.pack(fill="x", pady=10, ipadx=10, ipady=10)

        # Fila 1: Opciones de formato
        self.row1_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.row1_frame.pack(fill="x", pady=10, padx=20)

        self.lbl_format = ctk.CTkLabel(self.row1_frame, text="Formato:", text_color=TEXT_MAIN, font=("Roboto", 14, "bold"))
        self.lbl_format.pack(side="left", padx=(0, 10))
        self.combo_format = ctk.CTkComboBox(self.row1_frame, values=["Video MP4", "Audio MP3"], state="readonly", width=140, fg_color=SEARCH_BG, text_color=TEXT_MAIN, border_color=BORDER_COLOR, button_color=BORDER_COLOR, button_hover_color=BTN_SELECT_HOVER)
        self.combo_format.set("Video MP4")
        self.combo_format.pack(side="left", padx=(0, 40))

        self.lbl_quality = ctk.CTkLabel(self.row1_frame, text="Calidad:", text_color=TEXT_MAIN, font=("Roboto", 14, "bold"))
        self.lbl_quality.pack(side="left", padx=(0, 10))
        self.combo_quality = ctk.CTkComboBox(self.row1_frame, values=["Alta", "Media", "Baja"], state="readonly", width=140, fg_color=SEARCH_BG, text_color=TEXT_MAIN, border_color=BORDER_COLOR, button_color=BORDER_COLOR, button_hover_color=BTN_SELECT_HOVER)
        self.combo_quality.set("Alta")
        self.combo_quality.pack(side="left")

        # Fila 2: Ruta
        self.row2_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.row2_frame.pack(fill="x", pady=5, padx=20)

        self.lbl_path_title = ctk.CTkLabel(self.row2_frame, text="Guardar en:", text_color=TEXT_MAIN, font=("Roboto", 14, "bold"))
        self.lbl_path_title.pack(side="left", padx=(0, 10))
        
        self.btn_browse = ctk.CTkButton(self.row2_frame, text="Cambiar", width=90, fg_color=BTN_SELECT, hover_color=BTN_SELECT_HOVER, text_color=TEXT_MAIN, command=self.choose_directory)
        self.btn_browse.pack(side="right", padx=(10, 0))

        self.lbl_path = ctk.CTkLabel(self.row2_frame, text=self.current_download_path, text_color=TEXT_SUB, anchor="w", justify="left", font=("Roboto", 13))
        self.lbl_path.pack(side="left", fill="x", expand=True)

        # --- SECCIÓN: DESCARGA ---
        self.btn_download = ctk.CTkButton(self.main_frame, text="Descargar", height=55, corner_radius=27, font=("Roboto", 18, "bold"), fg_color=BTN_RED, hover_color=BTN_RED_HOVER, text_color="white", command=self.start_download)
        self.btn_download.pack(fill="x", pady=(20, 10))

        # Progreso
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, progress_color=BTN_RED, fg_color=BORDER_COLOR, height=12)
        self.progress_bar.pack(fill="x", pady=(0, 5))
        self.progress_bar.set(0)

        self.lbl_status = ctk.CTkLabel(self.main_frame, text="Listo", text_color=TEXT_SUB, font=("Roboto", 13))
        self.lbl_status.pack()

    def choose_directory(self):
        folder_selected = filedialog.askdirectory(initialdir=self.current_download_path)
        if folder_selected:
            self.current_download_path = folder_selected
            self.lbl_path.configure(text=self.current_download_path)
            self.config["download_path"] = self.current_download_path
            save_config(self.config)

    def clear_results_frame(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def start_search(self):
        query = self.entry_search.get().strip()
        if not query:
            return

        self.target_url = ""
        self.btn_search.configure(state="disabled")
        self.clear_results_frame()
        self.lbl_results_status = ctk.CTkLabel(self.results_frame, text="Buscando...", text_color=TEXT_SUB, font=("Roboto", 16))
        self.lbl_results_status.pack(pady=40)

        search_youtube(query, num_results=5, success_callback=self.on_search_success, error_callback=self.on_search_error)

    def on_search_success(self, results):
        self.after(0, self._render_results, results)

    def _render_results(self, results):
        self.btn_search.configure(state="normal")
        self.clear_results_frame()
        
        if not results:
            self.lbl_results_status = ctk.CTkLabel(self.results_frame, text="No se encontraron resultados.", text_color=BTN_RED)
            self.lbl_results_status.pack(pady=20)
            return

        for i, res in enumerate(results):
            res_frame = ctk.CTkFrame(self.results_frame, fg_color=BG_COLOR, corner_radius=10)
            res_frame.pack(fill="x", pady=5, padx=5)
            
            # Cargar imagen miniatura
            thumb_data = res.get('thumbnail_data')
            if thumb_data:
                try:
                    img = Image.open(io.BytesIO(thumb_data))
                    ctk_img = ctk.CTkImage(light_image=img, size=(120, 68))
                    lbl_img = ctk.CTkLabel(res_frame, image=ctk_img, text="", corner_radius=8)
                    lbl_img.pack(side="left", padx=(5, 10), pady=5)
                except Exception as e:
                    pass

            text_frame = ctk.CTkFrame(res_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True)

            title = res['title']
            if len(title) > 60:
                title = title[:57] + "..."
                
            lbl_title = ctk.CTkLabel(text_frame, text=title, text_color=TEXT_MAIN, font=("Roboto", 14, "bold"), anchor="w", justify="left")
            lbl_title.pack(anchor="w", pady=(5, 0))
            
            lbl_channel = ctk.CTkLabel(text_frame, text=res['uploader'], text_color=TEXT_SUB, font=("Roboto", 12), anchor="w")
            lbl_channel.pack(anchor="w")
            
            buttons_frame = ctk.CTkFrame(res_frame, fg_color="transparent")
            buttons_frame.pack(side="right", padx=10)

            # Botón Ver (Preview web)
            btn_view = ctk.CTkButton(buttons_frame, text="Ver en YouTube", width=100, height=28, corner_radius=14, fg_color=BTN_SELECT, hover_color=BTN_SELECT_HOVER, text_color=TEXT_MAIN,
                                       command=lambda url=res['url']: webbrowser.open(url))
            btn_view.pack(pady=(0, 5))

            # Botón Seleccionar
            btn_select = ctk.CTkButton(buttons_frame, text="Seleccionar", width=100, height=28, corner_radius=14, fg_color=TEXT_MAIN, hover_color="#DDDDDD", text_color=BG_COLOR, font=("Roboto", 12, "bold"),
                                       command=lambda url=res['url']: self.select_video(url))
            btn_select.pack()

    def on_search_error(self, error_msg):
        self.after(0, self._render_error, error_msg)
        
    def _render_error(self, error_msg):
        self.btn_search.configure(state="normal")
        self.clear_results_frame()
        self.lbl_results_status = ctk.CTkLabel(self.results_frame, text=f"Error: {error_msg}", text_color=BTN_RED)
        self.lbl_results_status.pack(pady=20)

    def select_video(self, url):
        self.target_url = url
        self.clear_results_frame()
        self.lbl_results_status = ctk.CTkLabel(self.results_frame, text="Video seleccionado. ¡Listo para descargar!", text_color=TEXT_MAIN, font=("Roboto", 14))
        self.lbl_results_status.pack(pady=40)

    def start_download(self):
        url = self.target_url or self.entry_search.get().strip()
        if not url:
            self.lbl_status.configure(text="Por favor, busca un video o ingresa un enlace.")
            return

        if not self.current_download_path:
            self.lbl_status.configure(text="Por favor, selecciona una ruta de descarga.")
            return

        self.btn_download.configure(state="disabled")
        self.lbl_status.configure(text="Iniciando descarga...", text_color=TEXT_MAIN)
        self.progress_bar.set(0)

        format_type = self.combo_format.get()
        quality = self.combo_quality.get()

        download_media(url, format_type, quality, self.current_download_path, 
                       progress_callback=self.on_progress, 
                       finished_callback=self.on_finished, 
                       error_callback=self.on_download_error)

    def on_progress(self, percentage, speed, eta):
        self.after(0, self._update_progress, percentage, speed, eta)

    def _update_progress(self, percentage, speed, eta):
        self.progress_bar.set(percentage)
        self.lbl_status.configure(text=f"Descargando... {int(percentage*100)}% | Vel: {speed} | Faltan: {eta}")

    def on_finished(self):
        self.after(0, self._download_finished)

    def _download_finished(self):
        self.btn_download.configure(state="normal")
        self.progress_bar.set(1.0)
        self.lbl_status.configure(text="¡Descarga completada con éxito!", text_color="#4CAF50")

    def on_download_error(self, error_msg):
        self.after(0, self._download_error, error_msg)

    def _download_error(self, error_msg):
        self.btn_download.configure(state="normal")
        self.lbl_status.configure(text=f"Error: {error_msg}", text_color=BTN_RED)

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
