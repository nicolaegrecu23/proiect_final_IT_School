"""
Tab pentru gestionarea preferintelor
"""

from datetime import date
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
 
from clase import Preferinta
 
 
class TabPreferinte:
    """Tab CRUD pentru preferintele pozitive."""
    
    def __init__(self, parent, db):
        self._parent = parent
        self._db = db
        self._mapare_medici = {}
        
        self._build_interface()
        self._refresh_combo_medici()
        self._refresh_treeview()
    
    def _build_interface(self):
        tk.Label(self._parent, text="Medic").grid(row=0, column=0, padx=5, pady=5)
        self._medic_combo = ttk.Combobox(self._parent, width=40)
        self._medic_combo.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self._parent, text="Data preferata (YYYY-MM-DD)").grid(row=1, column=0, padx=5, pady=5)
        self._data_entry = tk.Entry(self._parent, width=15)
        self._data_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(self._parent, text="Prioritate (1=inalta, 2=moderata)").grid(row=2, column=0, padx=5, pady=5)
        self._prioritate_combo = ttk.Combobox(self._parent, values=("1", "2"), width=5)
        self._prioritate_combo.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Button(self._parent, text="Adauga", command=self._adauga, width=12).grid(row=3, column=0, padx=5, pady=5)
        
        tk.Button(self._parent, text="Sterge", command=self._sterge, width=12).grid(row=3, column=1, padx=5, pady=5)
        
        tk.Button(self._parent, text="Aplica filtru", command=self._refresh_treeview, width=12).grid(row=3, column=2, padx=5, pady=5)

        tk.Button(self._parent, text="Refresh medici", command=self._refresh_combo_medici, width=15).grid(row=3, column=3, padx=5, pady=5)
        
        coloane = ("id", "medic", "data", "prioritate")
        self._tree = ttk.Treeview(self._parent, columns=coloane, show="headings", height=10)
        
        self._tree.heading("id", text="ID")
        self._tree.heading("medic", text="Medic")
        self._tree.heading("data", text="Data")
        self._tree.heading("prioritate", text="Prioritate")
        
        self._tree.column("id", width=50)
        self._tree.column("medic", width=200)
        self._tree.column("data", width=120)
        self._tree.column("prioritate", width=100)
        
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
        text = self._medic_combo.get()
        if not text:
            return None
        return self._mapare_medici.get(text)
    
    def _refresh_treeview(self):
        """Reincarca lista de preferinte (filtrate optional)."""
        for item in self._tree.get_children():
            self._tree.delete(item)
        medic_id = self._get_medic_id_selectat()
        pref_list = self._db.listare_preferinte(medic_id=medic_id)
        for pref in pref_list:
            medic = self._db.gaseste_medic_dupa_id(pref.medic_id)
            if medic:
                nume_medic = f"{medic.nume} {medic.prenume}"
            else:
                nume_medic = f"id={pref.medic_id}"
            self._tree.insert("", tk.END, values=(pref.id, nume_medic, pref.data, pref.prioritate))
    
    def _adauga(self):
        """Adauga o preferinta noua."""
        medic_id = self._get_medic_id_selectat()
        if medic_id is None:
            tkinter.messagebox.showwarning("Atentie", "Selecteaza un medic.")
            return
        data_text = self._data_entry.get().strip()
        if not data_text:
            tkinter.messagebox.showwarning("Atentie", "Completeaza data in format YYYY-MM-DD.")
            return
        prioritate_text = self._prioritate_combo.get()
        if not prioritate_text:
            tkinter.messagebox.showwarning("Atentie", "Selecteaza o prioritate (1 sau 2).")
            return
        try:
            data_pref = date.fromisoformat(data_text)
            prioritate = int(prioritate_text)
            pref = Preferinta(medic_id=medic_id, data=data_pref, prioritate=prioritate)
            self._db.adauga_preferinta(pref)
            self._refresh_treeview()
            tkinter.messagebox.showinfo("Succes!", f"Preferinta adaugata: {data_pref} (prioritate {prioritate})")
        except ValueError:
            tkinter.messagebox.showerror("Eroare", "Format dat gresit. Foloseste YYYY-MM-DD (ex: 2025-11-15).")
        except Exception as e:
            tkinter.messagebox.showerror("Eroare", str(e))
    
    def _sterge(self):
        """Sterge preferinta selectata."""
        selected = self._tree.focus()
        if not selected:
            tkinter.messagebox.showwarning("Atentie", "Selecteaza o preferinta pentru a o sterge.")
            return
        id_pref = self._tree.item(selected, "values")[0]
        try:
            self._db.sterge_preferinta(id_pref)
            self._refresh_treeview()
            tkinter.messagebox.showinfo("Succes", "Preferinta stearsa.")
        except Exception as e:
            tkinter.messagebox.showerror("Eroare", str(e))