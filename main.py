"""
Fisier principal. Initializeaza baza de date, algoritmul, creeaza interfata grafica.
"""

import tkinter as tk
import logger_config
from baza_de_date import DatabaseManager
from algoritm import Algoritm
from clase import LinieGarda
from interfata.fereastra_principala import FereastraPrincipala

def populeaza_linii(db) -> None:
    """Adauga liniile de garda standard daca nu exista deja."""
    if len(db.listare_linii_garda()) == 0:
        db.adauga_linie_garda(LinieGarda(nume="Linia 1 - Sef de garda"))
        db.adauga_linie_garda(LinieGarda(nume="Linia 2 - Urgente"))
        db.adauga_linie_garda(LinieGarda(nume="Linia 3 - Sectie"))

def main():
    db = DatabaseManager()
    populeaza_linii(db)
    algoritm = Algoritm(db)
    window = tk.Tk()
    FereastraPrincipala(window, db, algoritm)
    window.mainloop()

if __name__ == "__main__":
    main()
