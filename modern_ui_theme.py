# modern_ui_theme.py

"""
Nowoczesny design dla aplikacji LSTM
Kolory, style i tematy
"""

class ModernTheme:
    """Kolorystyka i style nowoczesne"""
    
    # Kolory - Motyw jasny
    LIGHT_MODE = {
        "bg_primary": "#FFFFFF",      # Białe tło
        "bg_secondary": "#F8F9FA",    # Szare tło (karty)
        "bg_accent": "#E3F2FD",       # Jasnoniebieskie tło (akcenty)
        "text_primary": "#1A1A1A",    # Ciemny tekst
        "text_secondary": "#666666",  # Szary tekst
        "accent_blue": "#2196F3",     # Niebieski
        "accent_green": "#4CAF50",    # Zielony (sukces)
        "accent_red": "#F44336",      # Czerwony (błędy)
        "accent_orange": "#FF9800",   # Pomarańczowy (warningi)
        "border": "#E0E0E0",          # Granice
        "shadow": "#00000015",        # Cień
    }
    
    # Kolory - Motyw ciemny
    DARK_MODE = {
        "bg_primary": "#1E1E2E",      # Ciemne tło
        "bg_secondary": "#2A2A3E",    # Ciemniejsze tło
        "bg_accent": "#1A3A52",       # Ciemnoniebieskie tło
        "text_primary": "#FFFFFF",    # Biały tekst
        "text_secondary": "#CCCCCC",  # Jasny szary tekst
        "accent_blue": "#42A5F5",     # Jaśniejszy niebieski
        "accent_green": "#66BB6A",    # Jaśniejszy zielony
        "accent_red": "#EF5350",      # Jaśniejszy czerwony
        "accent_orange": "#FFA726",   # Jaśniejszy pomarańczowy
        "border": "#404050",          # Ciemne granice
        "shadow": "#00000030",        # Mocny cień
    }
    
    # Rozmiary i spacing
    SPACING = {
        "xs": 4,      # 4px
        "sm": 8,      # 8px
        "md": 12,     # 12px
        "lg": 16,     # 16px
        "xl": 20,     # 20px
        "xxl": 24,    # 24px
    }
    
    # Czcionki
    FONTS = {
        "title_lg": ("Helvetica", 18, "bold"),
        "title_md": ("Helvetica", 14, "bold"),
        "title_sm": ("Helvetica", 12, "bold"),
        "body_lg": ("Helvetica", 11, "normal"),
        "body_md": ("Helvetica", 10, "normal"),
        "body_sm": ("Helvetica", 9, "normal"),
        "mono": ("Monaco", 10, "normal"),
    }
    
    # Promień zaokrąglenia (emulacja w Tkinter)
    BORDER_RADIUS = {
        "sm": 4,
        "md": 8,
        "lg": 12,
    }


class ModernUIHelper:
    """Pomocnik do tworzenia nowoczesnych elementów UI"""
    
    @staticmethod
    def get_theme(dark_mode=False):
        """Pobierz aktualny motyw"""
        return ModernTheme.DARK_MODE if dark_mode else ModernTheme.LIGHT_MODE
    
    @staticmethod
    def format_log_message(message, level="info"):
        """Format wiadomości logu z emoji"""
        icons = {
            "info": "ℹ️ ",
            "success": "✅ ",
            "warning": "⚠️ ",
            "error": "❌ ",
            "debug": "🔧 ",
            "chart": "📊 ",
            "database": "💾 ",
            "rocket": "🚀 ",
            "target": "🎯 ",
            "book": "📚 ",
        }
        return f"{icons.get(level, '')} {message}"
    
    @staticmethod
    def create_button_text(label, icon=""):
        """Utwórz tekst przycisku z ikoną"""
        if icon:
            return f"{icon}  {label}"
        return label
    
    @staticmethod
    def get_section_title(title):
        """Utwórz tytuł sekcji"""
        return f"━━━━━━━━━━━━━━━━━━━ {title} ━━━━━━━━━━━━━━━━━━━"


class ColorPalette:
    """Paleta kolorów dla różnych stanów"""
    
    @staticmethod
    def get_button_color(button_type="primary", dark_mode=False):
        """Pobierz kolor przycisku wg typu"""
        theme = ModernTheme.DARK_MODE if dark_mode else ModernTheme.LIGHT_MODE
        
        colors = {
            "primary": theme["accent_blue"],
            "success": theme["accent_green"],
            "danger": theme["accent_red"],
            "warning": theme["accent_orange"],
            "secondary": theme["bg_secondary"],
        }
        return colors.get(button_type, theme["accent_blue"])
    
    @staticmethod
    def get_status_color(status, dark_mode=False):
        """Pobierz kolor dla statusu"""
        theme = ModernTheme.DARK_MODE if dark_mode else ModernTheme.LIGHT_MODE
        
        status_colors = {
            "running": theme["accent_blue"],
            "success": theme["accent_green"],
            "error": theme["accent_red"],
            "warning": theme["accent_orange"],
            "idle": theme["text_secondary"],
        }
        return status_colors.get(status, theme["text_secondary"])


class IconSet:
    """Zestaw emoji ikon do użytku w UI"""
    
    # Akcje
    TRAIN = "🧠"
    PREDICT = "🔮"
    ANALYZE = "📊"
    COMPARE = "⚖️"
    VALIDATE = "✔️"
    ALERT = "🔔"
    DOWNLOAD = "⬇️"
    UPLOAD = "⬆️"
    EXPORT = "📤"
    
    # Status
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    LOADING = "⏳"
    
    # Domeny
    STOCK = "📈"
    CHART = "📊"
    DATABASE = "💾"
    CLOCK = "⏰"
    SETTINGS = "⚙️"
    HISTORY = "📜"
    FOLDER = "📁"
    
    # Kontrola
    PLAY = "▶️"
    STOP = "⏹️"
    PAUSE = "⏸️"
    REFRESH = "🔄"
    DELETE = "🗑️"
    EDIT = "✏️"
    
    # Prognoza
    BULLISH = "🚀"
    BEARISH = "📉"
    NEUTRAL = "➡️"
    TREND_UP = "📈"
    TREND_DOWN = "📉"
