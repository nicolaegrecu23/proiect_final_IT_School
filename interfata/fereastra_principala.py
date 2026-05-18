"""
Creeaza fereastra principala a interfetei grafice.
"""

import tkinter as tk
from tkinter import ttk

from interfata.tab_medici import TabMedici
from interfata.tab_indisponibilitati import TabIndisponibilitati
from interfata.tab_preferinte import TabPreferinte
from interfata.tab_program import TabProgram


class FereastraPrincipala:
    """Fereastra principala cu Notebook si tab-uri."""
    
    def __init__(self, window: tk.Tk, db, algoritm):
        self._window = window
        self._db = db
        self._algoritm = algoritm
        
        self._creare_interfata()
    
    def _creare_interfata(self):
        """Configureaza fereastra si creeaza Notebook-ul cu tab-uri."""
        self._window.title("Program gestionare garzi")
        self._window.geometry("1100x700")
        
        self._notebook = ttk.Notebook(self._window)
        self._notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._adauga_taburi()
    
    def _adauga_taburi(self):
        """Adauga toate tab-urile in Notebook."""
        
        frame_medici = tk.Frame(self._notebook)
        TabMedici(frame_medici, self._db)
        self._notebook.add(frame_medici, text="Medici")
        
        frame_indisp = tk.Frame(self._notebook)
        TabIndisponibilitati(frame_indisp, self._db)
        self._notebook.add(frame_indisp, text="Indisponibilitati")
        
        frame_pref = tk.Frame(self._notebook)
        TabPreferinte(frame_pref, self._db)
        self._notebook.add(frame_pref, text="Preferinte")
        
        frame_program = tk.Frame(self._notebook)
        TabProgram(frame_program, self._db, self._algoritm)
        self._notebook.add(frame_program, text="Program garzi")
