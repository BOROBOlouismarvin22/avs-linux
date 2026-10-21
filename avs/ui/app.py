# -*- coding: utf-8 -*-

"""
AVS COMPUTER ASSISTANT
======================

CONSOLE PROFESSIONNELLE AVS
Interface graphique desktop V3

Cette interface utilise directement le rapport produit par :

    avs.orchestrator.system_orchestrator

Architecture :

    PROBES
       ↓
    DIAGNOSTICS
       ↓
    CAUSES
       ↓
    ACTIONS
       ↓
    DASHBOARD AVS
"""

import platform
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from avs.orchestrator.system_orchestrator import run_system_diagnostic
from avs.system.hardware_info_probe import (
    get_processor_info,
    get_graphics_info,
    get_machine_info,
)


# =========================================================
# CONFIGURATION
# =========================================================

APP_NAME = "AVS Computer Assistant"
APP_VERSION = "3.0"

COLOR_NAVY = "#0A1628"
COLOR_NAVY_LIGHT = "#14263D"
COLOR_BACKGROUND = "#F4F7FA"
COLOR_WHITE = "#FFFFFF"
COLOR_TEXT = "#0A1628"
COLOR_MUTED = "#64748B"
COLOR_BORDER = "#D9E0E7"

COLOR_GREEN = "#16A34A"
COLOR_ORANGE = "#EA580C"
COLOR_RED = "#DC2626"
COLOR_BLUE = "#2563EB"
COLOR_GRAY = "#64748B"

FONT_MAIN = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_TITLE = ("Segoe UI", 24, "bold")
FONT_SECTION = ("Segoe UI", 17, "bold")
FONT_CARD_TITLE = ("Segoe UI", 10, "bold")
FONT_CARD_VALUE = ("Segoe UI", 23, "bold")
FONT_BIG_STATUS = ("Segoe UI", 25, "bold")
FONT_MONO = ("Consolas", 10)


# =========================================================
# APPLICATION
# =========================================================

class AVSApplication(tk.Tk):
    """Console graphique principale d'AVS Computer Assistant."""

    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} — Console AVS")
        self.geometry("1250x780")
        self.minsize(1050, 680)

        self.configure(bg=COLOR_BACKGROUND)

        self.report = None
        self.is_running = False

        self._create_styles()
        self._create_interface()

        # Lance automatiquement une première analyse.
        self.after(400, self.run_diagnostic)

    # =====================================================
    # STYLES
    # =====================================================

    def _create_styles(self):
        """Configure les styles ttk."""

        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Main.TFrame",
            background=COLOR_BACKGROUND,
        )

        style.configure(
            "Sidebar.TFrame",
            background=COLOR_NAVY,
        )

        style.configure(
            "Card.TFrame",
            background=COLOR_WHITE,
            relief="flat",
        )

        style.configure(
            "Title.TLabel",
            background=COLOR_BACKGROUND,
            foreground=COLOR_TEXT,
            font=FONT_TITLE,
        )

        style.configure(
            "Subtitle.TLabel",
            background=COLOR_BACKGROUND,
            foreground=COLOR_MUTED,
            font=FONT_MAIN,
        )

        style.configure(
            "Section.TLabel",
            background=COLOR_BACKGROUND,
            foreground=COLOR_TEXT,
            font=FONT_SECTION,
        )

        style.configure(
            "CardTitle.TLabel",
            background=COLOR_WHITE,
            foreground=COLOR_MUTED,
            font=FONT_CARD_TITLE,
        )

        style.configure(
            "CardValue.TLabel",
            background=COLOR_WHITE,
            foreground=COLOR_TEXT,
            font=FONT_CARD_VALUE,
        )

        style.configure(
            "CardStatus.TLabel",
            background=COLOR_WHITE,
            foreground=COLOR_MUTED,
            font=FONT_SMALL,
        )

        style.configure(
            "Action.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(18, 10),
        )

        style.configure(
            "Small.TButton",
            font=("Segoe UI", 9, "bold"),
            padding=(10, 7),
        )

        style.configure(
            "Horizontal.TProgressbar",
            thickness=7,
        )

    # =====================================================
    # INTERFACE
    # =====================================================

    def _create_interface(self):
        """Construit la console AVS."""

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.rowconfigure(0, weight=1)

        self._create_sidebar()
        self._create_main_area()

    # =====================================================
    # SIDEBAR
    # =====================================================

    def _create_sidebar(self):
        """Construit le menu latéral AVS."""

        self.sidebar = tk.Frame(
            self,
            bg=COLOR_NAVY,
            width=235,
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="ns",
        )

        self.sidebar.grid_propagate(False)

        # -------------------------------------------------
        # LOGO
        # -------------------------------------------------

        logo = tk.Label(
            self.sidebar,
            text="AVS",
            bg=COLOR_NAVY,
            fg=COLOR_WHITE,
            font=("Segoe UI", 30, "bold"),
        )

        logo.pack(
            pady=(30, 0),
        )

        subtitle = tk.Label(
            self.sidebar,
            text="COMPUTER ASSISTANT",
            bg=COLOR_NAVY,
            fg="#AAB7C4",
            font=("Segoe UI", 9),
        )

        subtitle.pack(
            pady=(0, 25),
        )

        separator = tk.Frame(
            self.sidebar,
            bg="#26384C",
            height=1,
        )

        separator.pack(
            fill="x",
            padx=20,
            pady=(0, 18),
        )

        # -------------------------------------------------
        # NAVIGATION
        # -------------------------------------------------

        navigation = [
            ("⌂", "Tableau de bord", self.show_dashboard),
            ("◉", "Diagnostic complet", self.run_diagnostic),
            ("◈", "Mémoire RAM", self.show_ram),
            ("⚙", "Processeur", self.show_cpu),
            ("▣", "Stockage", self.show_disk),
            ("≡", "Processus", self.show_processes),
            ("◎", "Réseau", self.show_network),
            ("▶", "Démarrage", self.show_startup),
            ("△", "Causes probables", self.show_causes),
            ("✓", "Actions", self.show_actions),
            ("▤", "Rapport", self.show_report),
            ("▢", "Informations système", self.show_hardware_info),
        ]

        for icon, text, command in navigation:

            button = tk.Button(
                self.sidebar,
                text=f"  {icon}   {text}",
                command=command,
                bg=COLOR_NAVY,
                fg=COLOR_WHITE,
                activebackground=COLOR_NAVY_LIGHT,
                activeforeground=COLOR_WHITE,
                relief="flat",
                borderwidth=0,
                anchor="w",
                padx=18,
                pady=10,
                font=FONT_MAIN,
                cursor="hand2",
            )

            button.pack(
                fill="x",
                padx=8,
                pady=1,
            )

        # -------------------------------------------------
        # BAS SIDEBAR
        # -------------------------------------------------

        bottom_frame = tk.Frame(
            self.sidebar,
            bg=COLOR_NAVY,
        )

        bottom_frame.pack(
            side="bottom",
            fill="x",
            padx=20,
            pady=20,
        )

        tk.Frame(
            bottom_frame,
            bg="#26384C",
            height=1,
        ).pack(
            fill="x",
            pady=(0, 15),
        )

        tk.Label(
            bottom_frame,
            text=f"AVS Computer Assistant\nVersion {APP_VERSION}",
            bg=COLOR_NAVY,
            fg="#8EA2B8",
            font=("Segoe UI", 8),
            justify="left",
        ).pack(
            anchor="w",
            pady=(0, 12),
        )

        quit_button = tk.Button(
            bottom_frame,
            text="■   Quitter",
            command=self.destroy,
            bg=COLOR_NAVY,
            fg="#AAB7C4",
            activebackground=COLOR_NAVY_LIGHT,
            activeforeground=COLOR_WHITE,
            relief="flat",
            borderwidth=0,
            anchor="w",
            padx=5,
            pady=7,
            font=FONT_SMALL,
            cursor="hand2",
        )

        quit_button.pack(
            fill="x",
        )

    # =====================================================
    # ZONE PRINCIPALE
    # =====================================================

    def _create_main_area(self):
        """Construit la zone principale, avec défilement vertical."""

        self.main = ttk.Frame(
            self,
            style="Main.TFrame",
            padding=30,
        )

        self.main.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        self.main.columnconfigure(0, weight=1)
        self.main.rowconfigure(1, weight=1)

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        header = ttk.Frame(
            self.main,
            style="Main.TFrame",
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 20),
        )

        header.columnconfigure(0, weight=1)

        self.page_title = ttk.Label(
            header,
            text="Tableau de bord",
            style="Title.TLabel",
        )

        self.page_title.grid(
            row=0,
            column=0,
            sticky="w",
        )

        self.status_label = ttk.Label(
            header,
            text="Initialisation de la console AVS...",
            style="Subtitle.TLabel",
        )

        self.status_label.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(4, 0),
        )

        # -------------------------------------------------
        # BOUTON ACTUALISER
        # -------------------------------------------------

        self.refresh_button = ttk.Button(
            header,
            text="↻  Actualiser",
            command=self.run_diagnostic,
            style="Small.TButton",
        )

        self.refresh_button.grid(
            row=0,
            column=1,
            rowspan=2,
            padx=(20, 0),
        )

        # -------------------------------------------------
        # CONTENU (avec défilement vertical)
        # -------------------------------------------------
        #
        # self.content n'est plus directement gridé dans self.main :
        # il vit maintenant à l'intérieur d'un Canvas scrollable,
        # avec une barre de défilement. Ça permet à n'importe quelle
        # page (ex: la liste des programmes au démarrage) de dépasser
        # la hauteur visible de la fenêtre sans que son contenu
        # devienne inaccessible.

        content_container = ttk.Frame(
            self.main,
            style="Main.TFrame",
        )

        content_container.grid(
            row=1,
            column=0,
            sticky="nsew",
        )

        content_container.columnconfigure(0, weight=1)
        content_container.rowconfigure(0, weight=1)

        self._content_canvas = tk.Canvas(
            content_container,
            bg=COLOR_BACKGROUND,
            highlightthickness=0,
        )

        self._content_canvas.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        content_scrollbar = ttk.Scrollbar(
            content_container,
            orient="vertical",
            command=self._content_canvas.yview,
        )

        content_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        self._content_canvas.configure(
            yscrollcommand=content_scrollbar.set,
        )

        self.content = ttk.Frame(
            self._content_canvas,
            style="Main.TFrame",
        )

        self._content_window = self._content_canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw",
        )

        self.content.columnconfigure(
            0,
            weight=1,
        )

        self.content.columnconfigure(
            1,
            weight=1,
        )

        def _on_content_resize(event):
            # Met à jour la zone défilable pour couvrir tout le contenu.
            self._content_canvas.configure(
                scrollregion=self._content_canvas.bbox("all")
            )

        self.content.bind(
            "<Configure>",
            _on_content_resize,
        )

        def _on_canvas_resize(event):
            # Force le contenu à occuper toute la largeur du canvas,
            # pour que les cartes et tableaux s'étirent correctement.
            self._content_canvas.itemconfig(
                self._content_window,
                width=event.width,
            )

        self._content_canvas.bind(
            "<Configure>",
            _on_canvas_resize,
        )

        def _on_mousewheel(event):
            self._content_canvas.yview_scroll(
                int(-1 * (event.delta / 120)),
                "units",
            )

        self._content_canvas.bind_all(
            "<MouseWheel>",
            _on_mousewheel,
        )

        self.show_dashboard()

    # =====================================================
    # OUTILS
    # =====================================================

    def _clear_content(self):
        """Nettoie la zone principale."""

        for widget in self.content.winfo_children():
            widget.destroy()

        for index in range(8):
            self.content.rowconfigure(
                index,
                weight=0,
            )

        # Remonte en haut de la page à chaque changement de contenu.
        self._content_canvas.yview_moveto(0)

    def _normalize(self, value):
        """Retourne un statut propre."""

        return str(value).upper().strip()

    def _status_color(self, status):
        """Détermine la couleur correspondant au statut."""

        status = self._normalize(status)

        if status in {
            "OK",
            "BONNE",
            "NORMAL",
            "FAIBLE",
            "CORRECT",
            "CORRECTE",
        }:
            return COLOR_GREEN

        if status in {
            "ATTENTION",
            "MOYENNE",
            "ÉLEVÉ",
            "ÉLEVÉE",
            "ELEVE",
            "ELEVEE",
            "LIMITÉE",
            "LIMITEE",
            "PACKET_LOSS",
            "HIGH_LATENCY",
            "UNSTABLE",
            "INCOMPLETE_DATA",
        }:
            return COLOR_ORANGE

        if status in {
            "CRITIQUE",
            "TRÈS LIMITÉE",
            "TRES LIMITEE",
            "HAUTE",
            "CRITICAL",
            "DNS_ERROR",
        }:
            return COLOR_RED

        return COLOR_GRAY

    def _create_card(
        self,
        row,
        column,
        title,
        value,
        status,
        description="",
    ):
        """Crée une carte professionnelle."""

        card = tk.Frame(
            self.content,
            bg=COLOR_WHITE,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
        )

        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=6,
            pady=6,
        )

        inner = tk.Frame(
            card,
            bg=COLOR_WHITE,
        )

        inner.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=15,
        )

        # Titre

        tk.Label(
            inner,
            text=title,
            bg=COLOR_WHITE,
            fg=COLOR_MUTED,
            font=FONT_CARD_TITLE,
            anchor="w",
        ).pack(
            fill="x",
        )

        # Valeur

        tk.Label(
            inner,
            text=value,
            bg=COLOR_WHITE,
            fg=COLOR_TEXT,
            font=FONT_CARD_VALUE,
            anchor="w",
        ).pack(
            fill="x",
            pady=(10, 2),
        )

        # Statut

        status_frame = tk.Frame(
            inner,
            bg=COLOR_WHITE,
        )

        status_frame.pack(
            fill="x",
        )

        color = self._status_color(status)

        tk.Label(
            status_frame,
            text="●",
            bg=COLOR_WHITE,
            fg=color,
            font=("Segoe UI", 8),
        ).pack(
            side="left",
        )

        tk.Label(
            status_frame,
            text=f"  {status}",
            bg=COLOR_WHITE,
            fg=color,
            font=("Segoe UI", 9, "bold"),
        ).pack(
            side="left",
        )

        if description:

            tk.Label(
                inner,
                text=description,
                bg=COLOR_WHITE,
                fg=COLOR_MUTED,
                font=("Segoe UI", 8),
                anchor="w",
                justify="left",
            ).pack(
                fill="x",
                pady=(7, 0),
            )

        # Barre visuelle

        bar_background = tk.Frame(
            inner,
            bg="#E5EAF0",
            height=5,
        )

        bar_background.pack(
            fill="x",
            pady=(10, 0),
        )

        bar_background.pack_propagate(False)

        bar = tk.Frame(
            bar_background,
            bg=color,
            height=5,
        )

        bar.pack(
            side="left",
            fill="y",
            expand=False,
        )

        # Longueur approximative selon statut

        normalized = self._normalize(status)

        if normalized in {"OK", "BONNE", "NORMAL", "CORRECT"}:
            width = 0.55
        elif normalized in {
            "ATTENTION",
            "MOYENNE",
            "LIMITÉE",
            "LIMITEE",
        }:
            width = 0.75
        else:
            width = 0.95

        self.after(
            10,
            lambda: bar.config(
                width=max(
                    20,
                    int(bar_background.winfo_width() * width),
                )
            ),
        )

    # =====================================================
    # CARTE INFORMATION (valeurs textuelles longues)
    # =====================================================

    def _create_info_card(
        self,
        row,
        column,
        title,
        value,
        status,
        description="",
    ):
        """
        Crée une carte adaptée aux valeurs textuelles longues
        (nom de processeur, modèle de machine, etc.), avec une
        police plus petite et un retour à la ligne automatique.

        Contrairement à _create_card, pas de barre de progression
        (une barre n'a pas de sens pour du texte descriptif).
        """

        card = tk.Frame(
            self.content,
            bg=COLOR_WHITE,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
        )

        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=6,
            pady=6,
        )

        inner = tk.Frame(
            card,
            bg=COLOR_WHITE,
        )

        inner.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=15,
        )

        tk.Label(
            inner,
            text=title,
            bg=COLOR_WHITE,
            fg=COLOR_MUTED,
            font=FONT_CARD_TITLE,
            anchor="w",
        ).pack(
            fill="x",
        )

        tk.Label(
            inner,
            text=value,
            bg=COLOR_WHITE,
            fg=COLOR_TEXT,
            font=("Segoe UI", 13, "bold"),
            anchor="w",
            justify="left",
            wraplength=420,
        ).pack(
            fill="x",
            pady=(10, 2),
        )

        status_frame = tk.Frame(
            inner,
            bg=COLOR_WHITE,
        )

        status_frame.pack(
            fill="x",
        )

        color = self._status_color(status)

        tk.Label(
            status_frame,
            text="●",
            bg=COLOR_WHITE,
            fg=color,
            font=("Segoe UI", 8),
        ).pack(
            side="left",
        )

        tk.Label(
            status_frame,
            text=f"  {status}",
            bg=COLOR_WHITE,
            fg=color,
            font=("Segoe UI", 9, "bold"),
        ).pack(
            side="left",
        )

        if description:

            tk.Label(
                inner,
                text=description,
                bg=COLOR_WHITE,
                fg=COLOR_MUTED,
                font=("Segoe UI", 8),
                anchor="w",
                justify="left",
            ).pack(
                fill="x",
                pady=(7, 0),
            )

    # =====================================================
    # PAGE SANS DIAGNOSTIC
    # =====================================================

    def _show_no_diagnostic(self):
        """Affiche un écran lorsque le rapport est absent."""

        self._clear_content()

        frame = tk.Frame(
            self.content,
            bg=COLOR_WHITE,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
        )

        frame.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=6,
            pady=6,
        )

        tk.Label(
            frame,
            text="◇",
            bg=COLOR_WHITE,
            fg=COLOR_BLUE,
            font=("Segoe UI", 40),
        ).pack(
            pady=(50, 10),
        )

        tk.Label(
            frame,
            text="Aucun diagnostic disponible",
            bg=COLOR_WHITE,
            fg=COLOR_TEXT,
            font=("Segoe UI", 18, "bold"),
        ).pack()

        tk.Label(
            frame,
            text=(
                "Lancez une analyse complète afin qu'AVS puisse "
                "examiner l'état réel de votre machine."
            ),
            bg=COLOR_WHITE,
            fg=COLOR_MUTED,
            font=FONT_MAIN,
            wraplength=600,
            justify="center",
        ).pack(
            pady=10,
        )

        ttk.Button(
            frame,
            text="▶  LANCER LE DIAGNOSTIC",
            command=self.run_diagnostic,
            style="Action.TButton",
        ).pack(
            pady=(15, 50),
        )

    # =====================================================
    # DASHBOARD
    # =====================================================

    def show_dashboard(self):
        """Affiche le dashboard principal."""

        self.page_title.config(
            text="Tableau de bord"
        )

        self._clear_content()

        self.content.rowconfigure(
            0,
            weight=1,
        )

        self.content.rowconfigure(
            1,
            weight=1,
        )

        self.content.rowconfigure(
            2,
            weight=0,
        )

        if self.report is None:

            self.status_label.config(
                text="Prêt pour le diagnostic."
            )

            self._create_card(
                0,
                0,
                "◈  MÉMOIRE RAM",
                "--",
                "En attente",
                "Analyse de la mémoire système",
            )

            self._create_card(
                0,
                1,
                "⚙  PROCESSEUR",
                "--",
                "En attente",
                "Analyse de la charge CPU",
            )

            self._create_card(
                1,
                0,
                "▣  STOCKAGE",
                "--",
                "En attente",
                "Analyse du disque système",
            )

            self._create_card(
                1,
                1,
                "▤  PROCESSUS",
                "--",
                "En attente",
                "Processus principaux surveillés",
            )

            return

        # -------------------------------------------------
        # DONNEES
        # -------------------------------------------------

        ram = self.report.get("ram", {})
        cpu = self.report.get("cpu", {})
        disk = self.report.get("disk", {})
        processes = self.report.get("processes", {})
        causes = self.report.get("causes", {})

        ram_status = ram.get(
            "diagnostic",
            {},
        ).get(
            "usage_status",
            "N/A",
        )

        cpu_status = cpu.get(
            "diagnostic",
            {},
        ).get(
            "usage_status",
            "N/A",
        )

        disk_status = disk.get(
            "diagnostic",
            {},
        ).get(
            "usage_status",
            "N/A",
        )

        global_status = causes.get(
            "priority",
            "NORMALE",
        )

        # -------------------------------------------------
        # HEADER STATUS
        # -------------------------------------------------

        self.status_label.config(
            text=(
                "Dernière analyse terminée  —  "
                f"État global : {global_status}"
            )
        )

        # -------------------------------------------------
        # CARTES
        # -------------------------------------------------

        self._create_card(
            0,
            0,
            "◈  MÉMOIRE RAM",
            f"{ram.get('measurement', {}).get('usage_percent', 0)} %",
            ram_status,
            (
                f"{ram.get('measurement', {}).get('used_gb', 0)} Go "
                f"utilisés sur "
                f"{ram.get('measurement', {}).get('total_gb', 0)} Go"
            ),
        )

        self._create_card(
            0,
            1,
            "⚙  PROCESSEUR",
            f"{cpu.get('measurement', {}).get('usage_percent', 0)} %",
            cpu_status,
            (
                f"{cpu.get('measurement', {}).get('logical_processors', 0)} "
                "processeurs logiques"
            ),
        )

        self._create_card(
            1,
            0,
            "▣  STOCKAGE",
            f"{disk.get('measurement', {}).get('usage_percent', 0)} %",
            disk_status,
            (
                f"{disk.get('measurement', {}).get('free_gb', 0)} Go "
                "libres"
            ),
        )

        self._create_card(
            1,
            1,
            "▤  PROCESSUS",
            str(processes.get("count", 0)),
            "Analysés",
            "Top des processus surveillés par AVS",
        )

        # -------------------------------------------------
        # ETAT GLOBAL
        # -------------------------------------------------

        global_frame = tk.Frame(
            self.content,
            bg=COLOR_WHITE,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
        )

        global_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=6,
            pady=(12, 6),
        )

        tk.Label(
            global_frame,
            text="ÉTAT DU SYSTÈME",
            bg=COLOR_WHITE,
            fg=COLOR_MUTED,
            font=("Segoe UI", 9, "bold"),
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 3),
        )

        status_text = causes.get(
            "status",
            "NON DISPONIBLE",
        )

        if global_status in {"HAUTE", "CRITIQUE"}:
            display_status = "ATTENTION"
        elif status_text == "NORMAL":
            display_status = "NORMAL"
        else:
            display_status = "ATTENTION"

        tk.Label(
            global_frame,
            text=display_status,
            bg=COLOR_WHITE,
            fg=self._status_color(global_status),
            font=FONT_BIG_STATUS,
        ).pack(
            anchor="w",
            padx=20,
        )

        tk.Label(
            global_frame,
            text=causes.get(
                "summary",
                "Analyse disponible.",
            ),
            bg=COLOR_WHITE,
            fg=COLOR_MUTED,
            font=FONT_SMALL,
            wraplength=850,
            justify="left",
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 15),
        )

        # -------------------------------------------------
        # BOUTON
        # -------------------------------------------------

        button_frame = tk.Frame(
            self.content,
            bg=COLOR_BACKGROUND,
        )

        button_frame.grid(
            row=3,
            column=0,
            columnspan=2,
            pady=15,
        )

        ttk.Button(
            button_frame,
            text="▶  LANCER UN NOUVEAU DIAGNOSTIC",
            command=self.run_diagnostic,
            style="Action.TButton",
        ).pack()

    # =====================================================
    # DIAGNOSTIC
    # =====================================================

    def run_diagnostic(self):
        """Lance un diagnostic sans bloquer l'interface."""

        if self.is_running:
            return

        self.is_running = True

        self.page_title.config(
            text="Diagnostic système"
        )

        self.status_label.config(
            text="AVS analyse actuellement votre machine..."
        )

        self._clear_content()

        container = tk.Frame(
            self.content,
            bg=COLOR_WHITE,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
        )

        container.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=6,
            pady=6,
        )

        tk.Label(
            container,
            text="◇",
            bg=COLOR_WHITE,
            fg=COLOR_BLUE,
            font=("Segoe UI", 42),
        ).pack(
            pady=(80, 10),
        )

        tk.Label(
            container,
            text="Diagnostic AVS en cours...",
            bg=COLOR_WHITE,
            fg=COLOR_TEXT,
            font=("Segoe UI", 18, "bold"),
        ).pack()

        tk.Label(
            container,
            text=(
                "Analyse de la RAM, du processeur, du stockage "
                "et des processus."
            ),
            bg=COLOR_WHITE,
            fg=COLOR_MUTED,
            font=FONT_MAIN,
        ).pack(
            pady=8,
        )

        progress = ttk.Progressbar(
            container,
            mode="indeterminate",
            style="Horizontal.TProgressbar",
            length=450,
        )

        progress.pack(
            pady=20,
        )

        progress.start(10)

        self.refresh_button.config(
            state="disabled",
        )

        thread = threading.Thread(
            target=self._diagnostic_worker,
            daemon=True,
        )

        thread.start()

    def _diagnostic_worker(self):
        """Exécute le diagnostic dans un thread."""

        try:

            report = run_system_diagnostic()

            self.after(
                0,
                lambda: self._diagnostic_success(report),
            )

        except Exception as error:

            self.after(
                0,
                lambda: self._diagnostic_error(error),
            )

    def _diagnostic_success(self, report):
        """Traite la réussite du diagnostic."""

        self.report = report
        self.is_running = False

        self.refresh_button.config(
            state="normal",
        )

        self.status_label.config(
            text="Diagnostic terminé avec succès."
        )

        self.show_dashboard()

    def _diagnostic_error(self, error):
        """Traite une erreur du diagnostic."""

        self.is_running = False

        self.refresh_button.config(
            state="normal",
        )

        self.status_label.config(
            text="Erreur pendant le diagnostic."
        )

        messagebox.showerror(
            "Erreur AVS",
            (
                "Le diagnostic n'a pas pu être terminé.\n\n"
                f"Détail : {error}"
            ),
        )

        self.show_dashboard()

    # =====================================================
    # RAM
    # =====================================================

    def show_ram(self):
        """Affiche le diagnostic détaillé RAM."""

        self.page_title.config(
            text="◈ Analyse de la mémoire RAM"
        )

        if self.report is None:
            self._show_no_diagnostic()
            return

        self._clear_content()

        ram = self.report["ram"]

        measurement = ram.get(
            "measurement",
            {},
        )

        diagnostic = ram.get(
            "diagnostic",
            {},
        )

        self._create_card(
            0,
            0,
            "RAM TOTALE",
            f"{measurement.get('total_gb', 0)} Go",
            diagnostic.get(
                "capacity_status",
                "N/A",
            ),
            diagnostic.get(
                "capacity_message",
                "",
            ),
        )

        self._create_card(
            0,
            1,
            "RAM UTILISÉE",
            f"{measurement.get('used_gb', 0)} Go",
            diagnostic.get(
                "usage_status",
                "N/A",
            ),
            diagnostic.get(
                "usage_message",
                "",
            ),
        )

        self._create_card(
            1,
            0,
            "RAM DISPONIBLE",
            f"{measurement.get('available_gb', 0)} Go",
            "DISPONIBLE",
            "Mémoire actuellement disponible.",
        )

        self._create_card(
            1,
            1,
            "UTILISATION",
            f"{measurement.get('usage_percent', 0)} %",
            diagnostic.get(
                "usage_status",
                "N/A",
            ),
            "Pourcentage de mémoire actuellement utilisé.",
        )

        self._create_information_box(
            2,
            "◆ RECOMMANDATION AVS",
            diagnostic.get(
                "recommendation",
                "Aucune recommandation disponible.",
            ),
        )

    # =====================================================
    # CPU
    # =====================================================

    def show_cpu(self):
        """Affiche le diagnostic CPU."""

        self.page_title.config(
            text="⚙  Analyse du processeur"
        )

        if self.report is None:
            self._show_no_diagnostic()
            return

        self._clear_content()

        cpu = self.report["cpu"]

        measurement = cpu.get(
            "measurement",
            {},
        )

        diagnostic = cpu.get(
            "diagnostic",
            {},
        )

        self._create_card(
            0,
            0,
            "UTILISATION CPU",
            f"{measurement.get('usage_percent', 0)} %",
            diagnostic.get(
                "usage_status",
                "N/A",
            ),
            "Charge actuelle du processeur.",
        )

        self._create_card(
            0,
            1,
            "PROCESSEURS LOGIQUES",
            str(
                measurement.get(
                    "logical_processors",
                    0,
                )
            ),
            diagnostic.get(
                "processor_status",
                "N/A",
            ),
            "Nombre de processeurs logiques détectés.",
        )

        self._create_information_box(
            1,
            "◆ RECOMMANDATION CPU",
            diagnostic.get(
                "recommendation",
                "Consulter le diagnostic CPU.",
            ),
        )

    # =====================================================
    # DISQUE
    # =====================================================

    def show_disk(self):
        """Affiche le diagnostic du stockage."""

        self.page_title.config(
            text="▣ Analyse du stockage"
        )

        if self.report is None:
            self._show_no_diagnostic()
            return

        self._clear_content()

        disk = self.report["disk"]

        measurement = disk.get(
            "measurement",
            {},
        )

        diagnostic = disk.get(
            "diagnostic",
            {},
        )

        self._create_card(
            0,
            0,
            "CAPACITÉ TOTALE",
            f"{measurement.get('total_gb', 0)} Go",
            "STOCKAGE",
            "Capacité totale du disque.",
        )

        self._create_card(
            0,
            1,
            "ESPACE UTILISÉ",
            f"{measurement.get('used_gb', 0)} Go",
            diagnostic.get(
                "usage_status",
                "N/A",
            ),
            "Espace actuellement utilisé.",
        )

        self._create_card(
            1,
            0,
            "ESPACE LIBRE",
            f"{measurement.get('free_gb', 0)} Go",
            diagnostic.get(
                "free_space_status",
                diagnostic.get(
                    "free_status",
                    "N/A",
                ),
            ),
            "Espace disponible sur le disque.",
        )

        self._create_card(
            1,
            1,
            "UTILISATION",
            f"{measurement.get('usage_percent', 0)} %",
            diagnostic.get(
                "usage_status",
                "N/A",
            ),
            "Pourcentage du stockage utilisé.",
        )

        self._create_information_box(
            2,
            "◆ RECOMMANDATION STOCKAGE",
            diagnostic.get(
                "recommendation",
                "Consulter le diagnostic du stockage.",
            ),
        )

    # =====================================================
    # PROCESSUS
    # =====================================================

    def show_processes(self):
        """Affiche les processus principaux."""

        self.page_title.config(
            text="▤ Processus principaux"
        )

        if self.report is None:
            self._show_no_diagnostic()
            return

        self._clear_content()

        processes = self.report.get(
            "processes",
            {},
        ).get(
            "diagnostics",
            [],
        )

        if not processes:

            self._show_message(
                "Aucun processus disponible."
            )

            return

        # -------------------------------------------------
        # EN-TETE
        # -------------------------------------------------

        header = tk.Frame(
            self.content,
            bg=COLOR_WHITE,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
        )

        header.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=6,
            pady=6,
        )

        tk.Label(
            header,
            text=(
                f"▤  {len(processes)} processus principaux "
                "analysés par AVS"
            ),
            bg=COLOR_WHITE,
            fg=COLOR_TEXT,
            font=("Segoe UI", 11, "bold"),
        ).pack(
            anchor="w",
            padx=15,
            pady=12,
        )

        # -------------------------------------------------
        # TABLEAU
        # -------------------------------------------------

        table = tk.Frame(
            self.content,
            bg=COLOR_WHITE,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
        )

        table.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=6,
            pady=6,
        )

        columns = [
            ("#", 5),
            ("Processus", 28),
            ("RAM", 15),
            ("CPU", 15),
            ("Statut", 18),
        ]

        for column, (title, width) in enumerate(columns):

            tk.Label(
                table,
                text=title,
                bg=COLOR_NAVY,
                fg=COLOR_WHITE,
                font=("Segoe UI", 9, "bold"),
                width=width,
                anchor="w",
                padx=8,
                pady=8,
            ).grid(
                row=0,
                column=column,
                sticky="ew",
            )

        for index, process in enumerate(
            processes,
            start=1,
        ):

            status = process.get(
                "status",
                "NORMAL",
            )

            color = self._status_color(status)

            values = [
                str(index),
                process.get("name", "Inconnu"),
                f"{process.get('memory_mb', 0):.2f} MB",
                f"{process.get('cpu_percent', 0):.2f} %",
                status,
            ]

            for column, value in enumerate(values):

                fg = color if column == 4 else COLOR_TEXT

                tk.Label(
                    table,
                    text=value,
                    bg=COLOR_WHITE,
                    fg=fg,
                    font=(
                        "Segoe UI",
                        9,
                        "bold" if column == 4 else "normal",
                    ),
                    anchor="w",
                    padx=8,
                    pady=7,
                ).grid(
                    row=index,
                    column=column,
                    sticky="ew",
                )

    # =====================================================
    # RÉSEAU
    # =====================================================

    def show_network(self):
        """Affiche le diagnostic réseau."""

        self.page_title.config(
            text="◎ Diagnostic réseau"
        )

        if self.report is None:
            self._show_no_diagnostic()
            return

        self._clear_content()

        network = self.report.get(
            "network",
            {},
        )

        ping_data = network.get("ping", {})
        dns_data = network.get("dns", {})
        diagnostic = network.get("diagnostic", {})

        self._create_card(
            0,
            0,
            "CONNEXION",
            "OK" if ping_data.get("success") else "ÉCHEC",
            diagnostic.get("status", "N/A"),
            f"Hôte testé : {ping_data.get('host', 'N/A')}",
        )

        self._create_card(
            0,
            1,
            "RÉSOLUTION DNS",
            "OK" if dns_data.get("success") else "ÉCHEC",
            diagnostic.get("status", "N/A"),
            f"Domaine testé : {dns_data.get('hostname', 'N/A')}",
        )

        avg_latency = ping_data.get("avg_latency_ms")

        self._create_card(
            1,
            0,
            "LATENCE MOYENNE",
            f"{avg_latency} ms" if avg_latency is not None else "N/A",
            diagnostic.get("status", "N/A"),
            "Temps de réponse moyen mesuré.",
        )

        packet_loss = ping_data.get("packet_loss_percent")

        self._create_card(
            1,
            1,
            "PERTE DE PAQUETS",
            f"{packet_loss} %" if packet_loss is not None else "N/A",
            diagnostic.get("status", "N/A"),
            "Pourcentage de paquets sans réponse.",
        )

        self._create_information_box(
            2,
            f"◆ {diagnostic.get('title', 'DIAGNOSTIC RÉSEAU')}",
            (
                f"{diagnostic.get('message', '')}\n\n"
                f"Recommandation : "
                f"{diagnostic.get('recommendation', 'Aucune recommandation.')}"
            ),
        )

    # =====================================================
    # DÉMARRAGE
    # =====================================================

    def show_startup(self):
        """Affiche le diagnostic des programmes au démarrage."""

        self.page_title.config(
            text="▶ Programmes au démarrage"
        )

        if self.report is None:
            self._show_no_diagnostic()
            return

        self._clear_content()

        startup = self.report.get(
            "startup",
            {},
        )

        programs = startup.get("programs", [])

        # -------------------------------------------------
        # RÉSUMÉ
        # -------------------------------------------------

        summary_frame = tk.Frame(
            self.content,
            bg=COLOR_WHITE,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
        )

        summary_frame.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=6,
            pady=6,
        )

        inner = tk.Frame(
            summary_frame,
            bg=COLOR_WHITE,
        )

        inner.pack(
            fill="both",
            padx=18,
            pady=15,
        )

        tk.Label(
            inner,
            text="NOMBRE DE PROGRAMMES AU DÉMARRAGE",
            bg=COLOR_WHITE,
            fg=COLOR_MUTED,
            font=FONT_CARD_TITLE,
            anchor="w",
        ).pack(
            fill="x",
        )

        tk.Label(
            inner,
            text=str(startup.get("count", 0)),
            bg=COLOR_WHITE,
            fg=COLOR_TEXT,
            font=FONT_CARD_VALUE,
            anchor="w",
        ).pack(
            fill="x",
            pady=(10, 2),
        )

        status_frame = tk.Frame(
            inner,
            bg=COLOR_WHITE,
        )

        status_frame.pack(
            fill="x",
        )

        status = startup.get("status", "N/A")
        color = self._status_color(status)

        tk.Label(
            status_frame,
            text="●",
            bg=COLOR_WHITE,
            fg=color,
            font=("Segoe UI", 8),
        ).pack(
            side="left",
        )

        tk.Label(
            status_frame,
            text=f"  {status}",
            bg=COLOR_WHITE,
            fg=color,
            font=("Segoe UI", 9, "bold"),
        ).pack(
            side="left",
        )

        tk.Label(
            inner,
            text=startup.get("message", ""),
            bg=COLOR_WHITE,
            fg=COLOR_MUTED,
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
            wraplength=900,
        ).pack(
            fill="x",
            pady=(8, 0),
        )

        # -------------------------------------------------
        # RECOMMANDATION
        # -------------------------------------------------

        self._create_information_box(
            1,
            "◆ RECOMMANDATION AVS",
            startup.get(
                "recommendation",
                "Aucune recommandation disponible.",
            ),
        )

        # -------------------------------------------------
        # TABLEAU DES PROGRAMMES
        # -------------------------------------------------

        if not programs:
            return

        table_header = tk.Frame(
            self.content,
            bg=COLOR_WHITE,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
        )

        table_header.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=6,
            pady=6,
        )

        tk.Label(
            table_header,
            text=f"▶  {len(programs)} programme(s) détecté(s)",
            bg=COLOR_WHITE,
            fg=COLOR_TEXT,
            font=("Segoe UI", 11, "bold"),
        ).pack(
            anchor="w",
            padx=15,
            pady=12,
        )

        table = tk.Frame(
            self.content,
            bg=COLOR_WHITE,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
        )

        table.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=6,
            pady=6,
        )

        columns = [
            ("#", 5),
            ("Programme", 45),
            ("Source", 25),
        ]

        for column, (title, width) in enumerate(columns):

            tk.Label(
                table,
                text=title,
                bg=COLOR_NAVY,
                fg=COLOR_WHITE,
                font=("Segoe UI", 9, "bold"),
                width=width,
                anchor="w",
                padx=8,
                pady=8,
            ).grid(
                row=0,
                column=column,
                sticky="ew",
            )

        for index, program in enumerate(
            programs,
            start=1,
        ):

            values = [
                str(index),
                program.get("name", "Inconnu"),
                program.get("source", "N/A"),
            ]

            for column, value in enumerate(values):

                tk.Label(
                    table,
                    text=value,
                    bg=COLOR_WHITE,
                    fg=COLOR_TEXT,
                    font=("Segoe UI", 9, "normal"),
                    anchor="w",
                    padx=8,
                    pady=7,
                ).grid(
                    row=index,
                    column=column,
                    sticky="ew",
                )

    # =====================================================
    # CAUSES
    # =====================================================

    def show_causes(self):
        """Affiche l'analyse des causes."""

        self.page_title.config(
            text="◇ Causes probables"
        )

        if self.report is None:
            self._show_no_diagnostic()
            return

        self._clear_content()

        causes = self.report.get(
            "causes",
            {},
        )

        # Etat

        self._create_information_box(
            0,
            "ÉTAT DE L'ANALYSE",
            (
                f"Statut : {causes.get('status', 'N/A')}\n"
                f"Priorité : {causes.get('priority', 'N/A')}\n\n"
                f"{causes.get('summary', '')}"
            ),
        )

        # Causes

        cause_text = ""

        for cause in causes.get(
            "causes",
            [],
        ):

            cause_text += f"• {cause}\n"

        if not cause_text:
            cause_text = (
                "• Aucune cause préoccupante identifiée."
            )

        self._create_information_box(
            1,
            "◇ CAUSES IDENTIFIÉES",
            cause_text,
        )

        # Evidence

        evidence_text = ""

        for evidence in causes.get(
            "evidence",
            [],
        ):

            evidence_text += f"• {evidence}\n"

        if not evidence_text:
            evidence_text = (
                "• Aucun élément préoccupant."
            )

        self._create_information_box(
            2,
            "● ÉLÉMENTS OBSERVÉS",
            evidence_text,
        )

    # =====================================================
    # ACTIONS
    # =====================================================

    def show_actions(self):
        """Affiche les actions recommandées."""

        self.page_title.config(
            text="⚙ Actions recommandées"
        )

        if self.report is None:
            self._show_no_diagnostic()
            return

        self._clear_content()

        actions = self.report.get(
            "actions",
            {},
        )

        self._create_information_box(
            0,
            "ÉTAT DU MOTEUR D'ACTION",
            (
                f"Statut : {actions.get('status', 'N/A')}\n"
                f"Priorité : {actions.get('priority', 'N/A')}"
            ),
        )

        action_list = actions.get(
            "actions",
            [],
        )

        for index, action in enumerate(
            action_list,
            start=1,
        ):

            text = (
                f"{index}.  "
                f"[{action.get('priority', 'N/A')}]  "
                f"{action.get('type', 'SYSTEME')}\n\n"
                f"{action.get('action', '')}"
            )

            self._create_information_box(
                index,
                "ACTION AVS",
                text,
            )

    # =====================================================
    # RAPPORT
    # =====================================================

    def show_report(self):
        """Affiche le rapport technique complet."""

        self.page_title.config(
            text="▤ Rapport système"
        )

        if self.report is None:
            self._show_no_diagnostic()
            return

        self._clear_content()

        text = tk.Text(
            self.content,
            bg=COLOR_WHITE,
            fg=COLOR_TEXT,
            font=FONT_MONO,
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=20,
            wrap="word",
            height=32,
        )

        text.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=6,
            pady=6,
        )

        ram = self.report.get(
            "ram",
            {},
        )

        cpu = self.report.get(
            "cpu",
            {},
        )

        disk = self.report.get(
            "disk",
            {},
        )

        processes = self.report.get(
            "processes",
            {},
        )

        network = self.report.get(
            "network",
            {},
        )

        startup = self.report.get(
            "startup",
            {},
        )

        causes = self.report.get(
            "causes",
            {},
        )

        actions = self.report.get(
            "actions",
            {},
        )

        ram_m = ram.get("measurement", {})
        ram_d = ram.get("diagnostic", {})

        cpu_m = cpu.get("measurement", {})
        cpu_d = cpu.get("diagnostic", {})

        disk_m = disk.get("measurement", {})
        disk_d = disk.get("diagnostic", {})

        network_ping = network.get("ping", {})
        network_dns = network.get("dns", {})
        network_d = network.get("diagnostic", {})

        report_text = f"""
============================================================
                 AVS COMPUTER ASSISTANT
                    RAPPORT TECHNIQUE
============================================================

INFORMATIONS MACHINE
------------------------------------------------------------

Système       : {platform.system()} {platform.release()}
Version       : {platform.version()}
Architecture  : {platform.machine()}
Ordinateur    : {platform.node()}
Processeur    : {get_processor_info().name or platform.processor()}

============================================================
MEMOIRE RAM
============================================================

Total         : {ram_m.get('total_gb', 0)} Go
Utilisée      : {ram_m.get('used_gb', 0)} Go
Disponible    : {ram_m.get('available_gb', 0)} Go
Utilisation   : {ram_m.get('usage_percent', 0)} %

État          : {ram_d.get('usage_status', 'N/A')}
Capacité      : {ram_d.get('capacity_status', 'N/A')}

Recommandation :
{ram_d.get('recommendation', 'N/A')}

============================================================
PROCESSEUR
============================================================

Utilisation   : {cpu_m.get('usage_percent', 0)} %
Processeurs   : {cpu_m.get('logical_processors', 0)}

État CPU      : {cpu_d.get('usage_status', 'N/A')}
État processeurs :
{cpu_d.get('processor_status', 'N/A')}

============================================================
STOCKAGE
============================================================

Capacité      : {disk_m.get('total_gb', 0)} Go
Utilisé       : {disk_m.get('used_gb', 0)} Go
Libre         : {disk_m.get('free_gb', 0)} Go
Utilisation   : {disk_m.get('usage_percent', 0)} %

État stockage : {disk_d.get('usage_status', 'N/A')}

============================================================
PROCESSUS
============================================================

Nombre analysé : {processes.get('count', 0)}

"""

        for index, process in enumerate(
            processes.get("diagnostics", []),
            start=1,
        ):

            report_text += (
                f"{index}. "
                f"{process.get('name', 'Inconnu')} | "
                f"RAM : {process.get('memory_mb', 0):.2f} MB | "
                f"CPU : {process.get('cpu_percent', 0):.2f}% | "
                f"Statut : {process.get('status', 'N/A')}\n"
            )

        report_text += f"""

============================================================
RÉSEAU
============================================================

Connexion (ping)   : {'OK' if network_ping.get('success') else 'ECHEC'}
Hôte testé         : {network_ping.get('host', 'N/A')}
Résolution DNS     : {'OK' if network_dns.get('success') else 'ECHEC'}
Domaine testé      : {network_dns.get('hostname', 'N/A')}
Latence moyenne    : {network_ping.get('avg_latency_ms', 'N/A')} ms
Perte de paquets   : {network_ping.get('packet_loss_percent', 'N/A')} %

État réseau        : {network_d.get('status', 'N/A')}

{network_d.get('message', '')}

Recommandation :
{network_d.get('recommendation', 'N/A')}

"""

        report_text += f"""
============================================================
PROGRAMMES AU DÉMARRAGE
============================================================

Nombre de programmes : {startup.get('count', 0)}
Statut                : {startup.get('status', 'N/A')}

{startup.get('message', '')}

Recommandation :
{startup.get('recommendation', 'N/A')}

"""

        for program in startup.get("programs", []):

            report_text += (
                f"- {program.get('name', 'Inconnu')} "
                f"[{program.get('source', 'N/A')}]\n"
            )

        report_text += f"""
============================================================
CAUSES PROBABLES
============================================================

Statut       : {causes.get('status', 'N/A')}
Priorité     : {causes.get('priority', 'N/A')}

Résumé :
{causes.get('summary', 'N/A')}

"""

        for cause in causes.get(
            "causes",
            [],
        ):

            report_text += f"- {cause}\n"

        report_text += """

============================================================
ÉLÉMENTS OBSERVÉS
============================================================

"""

        for evidence in causes.get(
            "evidence",
            [],
        ):

            report_text += f"- {evidence}\n"

        report_text += f"""

============================================================
ACTIONS À EFFECTUER
============================================================

Statut       : {actions.get('status', 'N/A')}
Priorité     : {actions.get('priority', 'N/A')}

"""

        for index, action in enumerate(
            actions.get("actions", []),
            start=1,
        ):

            report_text += (
                f"{index}. "
                f"[{action.get('priority', 'N/A')}] "
                f"{action.get('type', 'SYSTEME')}\n"
                f"   {action.get('action', '')}\n\n"
            )

        report_text += """
============================================================
FIN DU RAPPORT AVS
============================================================
"""

        text.insert(
            "1.0",
            report_text,
        )

        text.config(
            state="disabled",
        )

        # Mémorise le texte pour permettre l'export.
        self._last_report_text = report_text

        # -------------------------------------------------
        # BOUTON EXPORT
        # -------------------------------------------------

        export_button = ttk.Button(
            self.content,
            text="▣  Exporter le rapport",
            command=self._export_report,
            style="Small.TButton",
        )

        export_button.grid(
            row=1,
            column=0,
            columnspan=2,
            pady=(10, 0),
            sticky="e",
        )

    # =====================================================
    # EXPORT DU RAPPORT
    # =====================================================

    def _export_report(self):
        """Exporte le rapport système actuel dans un fichier texte."""

        if not getattr(self, "_last_report_text", None):

            messagebox.showwarning(
                "AVS",
                "Aucun rapport à exporter pour le moment.",
            )

            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Fichier texte", "*.txt"),
                ("Tous les fichiers", "*.*"),
            ],
            initialfile="rapport_avs.txt",
            title="Exporter le rapport AVS",
        )

        # L'utilisateur a annulé la boîte de dialogue.
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self._last_report_text)

        except OSError as error:

            messagebox.showerror(
                "Erreur AVS",
                (
                    "Impossible d'enregistrer le rapport.\n\n"
                    f"Détail : {error}"
                ),
            )

            return

        messagebox.showinfo(
            "AVS",
            f"Rapport exporté avec succès vers :\n{file_path}",
        )

    # =====================================================
    # INFORMATIONS SYSTEME
    # =====================================================

    def show_hardware_info(self):
        """Affiche les informations matérielles statiques de la machine."""

        self.page_title.config(
            text="▢ Informations système"
        )

        self._clear_content()

        self.status_label.config(
            text="Récupération des informations matérielles..."
        )

        self.update_idletasks()

        processor = get_processor_info()
        graphics = get_graphics_info()
        machine = get_machine_info()

        self.status_label.config(
            text="Informations matérielles de votre machine."
        )

        self._create_info_card(
            0,
            0,
            "PROCESSEUR",
            processor.name or "Non disponible",
            "OK" if processor.name else "CRITIQUE",
            "Modèle du processeur installé.",
        )

        self._create_info_card(
            0,
            1,
            "CARTE GRAPHIQUE",
            graphics.name or "Non disponible",
            "OK" if graphics.name else "CRITIQUE",
            "Carte graphique principale détectée.",
        )

        self._create_info_card(
            1,
            0,
            "FABRICANT",
            machine.manufacturer or "Non disponible",
            "OK" if machine.manufacturer else "CRITIQUE",
            "Fabricant de la machine.",
        )

        self._create_info_card(
            1,
            1,
            "MODÈLE",
            machine.model or "Non disponible",
            "OK" if machine.model else "CRITIQUE",
            "Modèle exact de la machine.",
        )

    # =====================================================
    # INFORMATIONS
    # =====================================================

    def _create_information_box(
        self,
        row,
        title,
        message,
    ):
        """Crée un bloc d'information professionnel."""

        box = tk.Frame(
            self.content,
            bg=COLOR_WHITE,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
        )

        box.grid(
            row=row,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=6,
            pady=6,
        )

        tk.Label(
            box,
            text=title,
            bg=COLOR_WHITE,
            fg=COLOR_TEXT,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(
            fill="x",
            padx=18,
            pady=(14, 6),
        )

        tk.Label(
            box,
            text=message,
            bg=COLOR_WHITE,
            fg=COLOR_MUTED,
            font=FONT_MAIN,
            justify="left",
            anchor="w",
            wraplength=900,
        ).pack(
            fill="x",
            padx=18,
            pady=(0, 14),
        )

    def _show_message(self, message):
        """Affiche un message simple."""

        self._clear_content()

        self._create_information_box(
            0,
            "AVS",
            message,
        )


# =========================================================
# POINT D'ENTRÉE
# =========================================================

def main():
    """Lance la console AVS."""

    app = AVSApplication()
    app.mainloop()


if __name__ == "__main__":
    main()