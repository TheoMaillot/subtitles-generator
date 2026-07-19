import sys
import os

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import customtkinter
import threading
import ctypes
from PIL import Image

from pathlib import Path

from translation import video_translation
from languages import LANGUAGE_CODES

if getattr(sys, 'frozen', False):
    PARENT_FOLDER = Path(sys._MEIPASS)
else:
    PARENT_FOLDER = Path(__file__).parent

'   STYLE   '
BACKGROUND_IMG                      = PARENT_FOLDER / "img/background.png"
ICON_PATH                           = PARENT_FOLDER / "img/logo.ico"
FONT_PATH                           = PARENT_FOLDER / "font/DynaPuff-VariableFont_wdth,wght.ttf"
FONT_NAME                           = "DynaPuff"
CORNER_RADIUS                       = 20
CORNER_RADIUS_2                     = 5
BORDER_WIDTH                        = 3
BORDER_COLOR                        ="#890089"
BACKGROUND_COLOR                    ="#FFACF4"
BAR_COLOR                           ="#B300B0"
# TEXT BUTTON
TEXT_BUTTON_FG_COLOR                ="#FEE5ED"
TEXT_BUTTON_TEXT_COLOR              ="#DB4B93"
TEXT_BUTTON_BORDER_COLOR            ="#C4196F"
TEXT_BUTTON_BORDER_COLOR            ="#D1537B"
# BUTTON
BUTTON_FG_COLOR                     ="#D000D7"
BUTTON_BG_COLOR                     ="#360038"
BUTTON_TEXT_COLOR                   ="#FFCCE5"
# COMBOBOX
COMBOBOX_FG_COLOR                   ="#92FCEE"
COMBOBOX_TEXT_COLOR                 ="#C4196F"
# COMOBOX DROPDOWN
COMOBOX_DROPDOWN_BG                 ="#FD36F0"
COMOBOX_DROPDOWN_FG                 ="#6F0239"
COMOBOX_DROPDOWN_ACTIVEBACKGROUND   ="#E885D6"
COMOBOX_DROPDOWN_ACTIVEFOREGROUND   ="#BF4682"
# PROGRESS BAR
PROGRESS_COLOR                      ="#FF89C4"

def load_font_windows(font_path: Path) -> bool:
    if sys.platform != "win32":
        return False

    FR_PRIVATE = 0x10
    path_str = str(font_path.resolve())

    added = ctypes.windll.gdi32.AddFontResourceExW(
        ctypes.c_wchar_p(path_str), FR_PRIVATE, 0
    )
    return added > 0

def set_title_bar_color(window, hex_color):
    try:
        window.update()
        # 1. Retrieve the system identifier (HWND) of your Tkinter window
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        
        # 2. Convert a hex colour (#RRGGBB) to the Windows BGR format (0x00BBGGRR)
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        color_bgr = (b << 16) | (g << 8) | r
        
        # 3. Apply the colour (attribute 35 corresponds to DWMWA_CAPTION_COLOR in Windows 11)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 35, ctypes.byref(ctypes.c_int(color_bgr)), 4
        )
    except Exception as e:
        print(f"It is not possible to change the colour of the title bar: {e}")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Subtitle Generator")
        self.geometry("400x340")
        # logo
        self.iconbitmap(ICON_PATH)
        # bar color
        set_title_bar_color(self, BAR_COLOR)
        # background color
        self.configure(fg_color=BACKGROUND_COLOR)
        # font
        self.main_font = customtkinter.CTkFont(family=FONT_NAME, size=14, weight="bold")
        self.title_font = customtkinter.CTkFont(family=FONT_NAME, size=16, weight="bold")
        # Background
        self.bg_image = customtkinter.CTkImage(
            light_image=Image.open(BACKGROUND_IMG),
            size=(400, 340)
        )
        self.bg_label = customtkinter.CTkLabel(
            self, 
            text="", 
            image=self.bg_image
        )
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()
    

        # path of the selected video file
        self.video_path = None

        # path for the subtiles
        self.sub_path = None

        # Locate button
        self.locate_btn = customtkinter.CTkButton(
            self, text="Locate Video", 
            command=self.locate_video,
            corner_radius=CORNER_RADIUS,
            border_width=BORDER_WIDTH,
            border_color=BORDER_COLOR,
            fg_color=BUTTON_FG_COLOR,
            text_color=BUTTON_TEXT_COLOR,
            font=self.title_font,
            bg_color="#F989AD"
        )
        self.locate_btn.pack(padx=20, pady=(20, 5))
        self.file_label = customtkinter.CTkLabel(
            self, 
            text="No video selected", 
            text_color="red",
            font=self.main_font,
            bg_color="#F989AD"
        )
        self.file_label.pack(padx=20, pady=(0, 15))

        # input language choice
        self.input_lang_label = customtkinter.CTkLabel(
            self, 
            text="Input Language:",
            corner_radius=CORNER_RADIUS_2,
            border_width=BORDER_WIDTH,
            border_color=TEXT_BUTTON_BORDER_COLOR,
            fg_color=TEXT_BUTTON_FG_COLOR,
            text_color=TEXT_BUTTON_TEXT_COLOR,
            font=self.main_font,
            bg_color="#F989AD"
        )
        self.input_lang_label.pack(padx=20, pady=(0, 5))
        self.input_lang_var = customtkinter.StringVar(value="English")
        self.input_lang_dropdown = customtkinter.CTkComboBox(
            self, 
            values=list(LANGUAGE_CODES.keys()), 
            variable=self.input_lang_var,
            corner_radius=CORNER_RADIUS,
            fg_color=COMBOBOX_FG_COLOR,
            text_color=COMBOBOX_TEXT_COLOR,
            font=self.main_font,
            bg_color="#FDBFD8"
        )
        self.input_lang_dropdown.pack(padx=20, pady=(0, 15))
        self.input_lang_dropdown._dropdown_menu.configure(
            bg=COMOBOX_DROPDOWN_BG,
            fg=COMOBOX_DROPDOWN_FG,
            activebackground=COMOBOX_DROPDOWN_ACTIVEBACKGROUND, 
            activeforeground=COMOBOX_DROPDOWN_ACTIVEFOREGROUND,
            font=self.main_font
        )

        # output language choice
        self.output_lang_label = customtkinter.CTkLabel(
            self, 
            text="Output Language",
            corner_radius=CORNER_RADIUS_2,
            border_width=BORDER_WIDTH,
            border_color=TEXT_BUTTON_BORDER_COLOR,
            fg_color=TEXT_BUTTON_FG_COLOR,
            text_color=TEXT_BUTTON_TEXT_COLOR,
            font=self.main_font,
            bg_color="#F989AD"
        )
        self.output_lang_label.pack(padx=20, pady=(0, 5))
        self.output_lang_var = customtkinter.StringVar(value="Chinese")
        self.output_lang_dropdown = customtkinter.CTkComboBox(
            self, 
            values=list(LANGUAGE_CODES.keys()), 
            variable=self.output_lang_var,
            corner_radius=CORNER_RADIUS,
            fg_color=COMBOBOX_FG_COLOR,
            text_color=COMBOBOX_TEXT_COLOR,
            font=self.main_font,
            bg_color="#FED7EA"
        )
        self.output_lang_dropdown.pack(
            padx=20, 
            pady=(0, 15)
        )
        self.output_lang_dropdown._dropdown_menu.configure(
            bg=COMOBOX_DROPDOWN_BG,
            fg=COMOBOX_DROPDOWN_FG,
            activebackground=COMOBOX_DROPDOWN_ACTIVEBACKGROUND, 
            activeforeground=COMOBOX_DROPDOWN_ACTIVEFOREGROUND,
            font=self.main_font
        )

        # generate subtitles button
        self.button = customtkinter.CTkButton(
            self, 
            text="Generate subtitles", 
            command=self.generate_subtitles,
            font=self.title_font,
            corner_radius=CORNER_RADIUS,
            fg_color=BUTTON_FG_COLOR,
            text_color=BUTTON_TEXT_COLOR,
            bg_color="#FFE0F7"
        )
        self.button.pack(padx=20, pady=20)

        # Loading bar
        self.progress = customtkinter.CTkProgressBar(
            self, 
            mode="indeterminate",
            height=16,  
            corner_radius=8,  
            border_width=2,  
            fg_color=PROGRESS_COLOR, 
            border_color=BORDER_COLOR, 
            progress_color=BUTTON_FG_COLOR 
        )

    def locate_video(self):
        from tkinter import filedialog

        # Open file dialog to select a video file
        self.video_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv"), ("All Files", "*.*")]
        )

        # Update the label with the selected file path or a message if no file was selected
        if self.video_path:
            self.file_label.configure(text=self.video_path, text_color="white")
        else:
            self.file_label.configure(text="No video selected", text_color="gray")


    def generate_subtitles(self):
        from tkinter import filedialog
        if not self.video_path:
            self.file_label.configure(text="Please select a video file first.", text_color="red")
            return

        srt_name = os.path.splitext(os.path.basename(self.video_path))[0]
        video_dir = os.path.dirname(self.video_path)

        # Open file dialog to select a video file
        self.sub_path = filedialog.asksaveasfilename(
            title="Enregistrer le fichier de sous-titres",
            initialfile=f"{srt_name}.srt",
            defaultextension=".srt",
            filetypes=[("Fichiers SRT", "*.srt"), ("Tous les fichiers", "*.*")]
        )

        input_lang = self.input_lang_var.get()
        output_lang = self.output_lang_var.get()
        # creation of the subtitles
        self.button.configure(state="disabled", text="Generation in progress...")
        self.progress.pack(padx=20, pady=(0, 10))
        self.progress.start()

        threading.Thread(
            target=self.run_translation_thread, 
            args=(input_lang, output_lang), 
            daemon=True
        ).start()

    # thread for translation
    def run_translation_thread(self, input_lang, output_lang):
        video_translation(
            video_path=self.video_path, 
            subtitles_path=self.sub_path, 
            video_language=input_lang, 
            target_language=output_lang
        )
        # When it’s finished, we safely notify the graphical user interface
        self.after(0, self.on_translation_done)

    # Clears the interface once the job is done
    def on_translation_done(self):
        self.progress.stop()          # Arrête l'animation
        self.progress.pack_forget()   # Cache la barre
        self.button.configure(state="normal", text="generate subtitles") # Réactive le bouton
        self.file_label.configure(text="Subtitles generated successfully!", text_color="#8800FF")

if __name__ == "__main__":
    app = App()
    app.mainloop()