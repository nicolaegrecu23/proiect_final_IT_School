"""
Tab pentru gestionarea indisponibilitatilor.
"""

from datetime import date
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
 
from clase import Indisponibilitate
 
class TabIndisponibilitati:
    """Tab CRUD pentru indisponibilitatile medicilor."""
    
    def __init__(self, parent, db):
        self._parent = parent
        self._db = db

        self._mapare_medici = {}
        
        self._build_interface()
        self._refresh_combo_medici()
        self._refresh_treeview()
    
    def _build_interface(self):
        tk.Label(self._parent, text="Medic").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self._medic_combo = ttk.Combobox(self._parent, width=40)
        self._medic_combo.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self._parent, text="Data inceput (YYYY-MM-DD)").grid(row=1, column=0, padx=5, pady=5)
        self._data_start_entry = tk.Entry(self._parent, width=15)
        self._data_start_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(self._parent, text="Data sfarsit (YYYY-MM-DD)").grid(row=2, column=0, padx=5, pady=5)
        self._data_stop_entry = tk.Entry(self._parent, width=15)
        self._data_stop_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Button(self._parent, text="Adauga", command=self._adauga, width=12).grid(row=3, column=0, padx=5, pady=5)
        
        tk.Button(self._parent, text="Sterge", command=self._sterge, width=12).grid(row=3, column=1, padx=5, pady=5)
        
        tk.Button(self._parent, text="Aplica filtru", command=self._refresh_treeview, width=12).grid(row=3, column=2, padx=5, pady=5)

        tk.Button(self._parent, text="Refresh medici", command=self._refresh_combo_medici, width=15).grid(row=3, column=3, padx=5, pady=5)
        
        coloane = ("id", "medic", "data_start", "data_stop")
        self._tree = ttk.Treeview(self._parent, columns=coloane, show="headings", height=10)
        
        self._tree.heading("id", text="ID")
        self._tree.heading("medic", text="Medic")
        self._tree.heading("data_start", text="Data inceput")
        self._tree.heading("data_stop", text="Data sfarsit")
        
        self._tree.column("id", width=50)
        self._tree.column("medic", width=200)
        self._tree.column("data_start", width=120)
        self._tree.column("data_stop", width=120)
        
        self._tree.grid(row=4, column=0, columnspan=4, padx=10, pady=10)
    
    def _refresh_combo_medici(self):
        """Populeaza combobox-ul cu medicii din DB."""
        medici = self._db.listare_medici()
        self._mapare_medici = {}
        valori = []
        for m in medici:
            text = f"{m.id} - {m.nume} {m.prenume} ({m.grad})"
            self._mapare_medici[text] = m.id
            valori.append(text)
        self._medic_combo["values"] = valori
    
    def _get_medic_id_selectat(self):
        """Returneaza id-ul medicului selectat in combobox, sau None."""
        text = self._medic_combo.get()
        if not text:
            return None
        return self._mapare_medici.get(text)
    
    def _refresh_treeview(self):
        """Reincarca lista de indisponibilitati."""
        for item in self._tree.get_children():
            self._tree.delete(item)
        medic_id = self._get_medic_id_selectat()
        indisp_list = self._db.listare_indisponibilitati(medic_id=medic_id)
        for indisp in indisp_list:
            medic = self._db.gaseste_medic_dupa_id(indisp.medic_id)
            if medic:
                nume_medic = f"{medic.nume} {medic.prenume}"
            else:
                nume_medic = f"id={indisp.medic_id}"
            self._tree.insert("", tk.END, values=(indisp.id, nume_medic, indisp.data_start, indisp.data_stop))
    
    def _adauga(self):
        """Adauga o indisponibilitate noua."""
        medic_id = self._get_medic_id_selectat()
        if medic_id is None:
            tkinter.messagebox.showwarning("Atentie", "Selecteaza un medic.")
            return
        data_start_text = self._data_start_entry.get().strip()
        data_stop_text = self._data_stop_entry.get().strip()
        if not data_start_text or not data_stop_text:
            tkinter.messagebox.showwarning("Atentie", "Completeaza ambele date in format YYYY-MM-DD.")
            return
        try:
            data_start = date.fromisoformat(data_start_text)
            data_stop = date.fromisoformat(data_stop_text)
        except ValueError:
            tkinter.messagebox.showerror("Eroare", "Format dat gresit. Foloseste YYYY-MM-DD (ex: 2025-11-15).")
            return
        try:
            indisp = Indisponibilitate(medic_id=medic_id, data_start=data_start, data_stop=data_stop)
            self._db.adauga_indisponibilitate(indisp)
            self._refresh_treeview()
            tkinter.messagebox.showinfo("Succes!", f"Indisponibilitate adaugata: {data_start} - {data_stop}")
        except Exception as e:
            tkinter.messagebox.showerror("Eroare", str(e))
    
    def _sterge(self):
        """Sterge indisponibilitatea selectata."""
        selected = self._tree.focus()
        if not selected:
            tkinter.messagebox.showwarning("Atentie", "Selecteaza o indisponibilitate pentru a o sterge.")
            return
        id_indisp = self._tree.item(selected, "values")[0]
        try:
            self._db.sterge_indisponibilitate(id_indisp)
            self._refresh_treeview()
            tkinter.messagebox.showinfo("Succes", "Indisponibilitate stearsa.")
        except Exception as e:
            tkinter.messagebox.showerror("Eroare", str(e))