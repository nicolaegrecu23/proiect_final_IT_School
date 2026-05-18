"""
Fisier principal. Initializeaza baza de date, algoritmul, creeaza interfata grafica.
"""

import tkinter as tk
import logger_config
from baza_de_date import DatabaseManager
from algoritm import Algoritm
from interfata.fereastra_principala import FereastraPrincipala

def main():
    db = DatabaseManager()
    algoritm = Algoritm(db)
    window = tk.Tk()
    FereastraPrincipala(window, db, algoritm)
    window.mainloop()

if __name__ == "__main__":
    main()