"""
Tab pentru Medici.
"""

import csv
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import tkinter.filedialog
import os
from clase import construieste_medic, Rezident

FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TabMedici:
    """Tab pentru gestionarea medicilor (CRUD + filtrare + import/export CSV)."""
    
    def __init__(self, parent, db):
        self._parent = parent
        self._db = db
        
        self._build_interface()
        self._refresh_treeview()
    
    def _build_interface(self):
        """Construieste toate widget-urile tab-ului."""

        tk.Label(self._parent, text="Nume").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self._nume_entry = tk.Entry(self._parent, width=25)
        self._nume_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self._parent, text="Prenume").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self._prenume_entry = tk.Entry(self._parent, width=25)
        self._prenume_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(self._parent, text="Grad").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self._grad_combo = ttk.Combobox(self._parent, values=("primar", "specialist", "rezident"), state="readonly", width=12)
        self._grad_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(self._parent, text="An").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self._an_combo = ttk.Combobox(self._parent, values=("3", "4", "5"), state="readonly", width=5)
        self._an_combo.grid(row=2, column=3, padx=5, pady=5, sticky="w")
        
        tk.Label(self._parent, text="Telefon").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self._telefon_entry = tk.Entry(self._parent, width=15)
        self._telefon_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        tk.Button(self._parent, text="Adauga", command=self._adauga_medic, width=12).grid(row=4, column=0, padx=5, pady=5)
        
        tk.Button(self._parent, text="Modifica", command=self._modifica_medic, width=12).grid(row=4, column=1, padx=5, pady=5)
        
        tk.Button(self._parent, text="Sterge", command=self._sterge_medic, width=12).grid(row=4, column=2, padx=5, pady=5)
        
        tk.Button(self._parent, text="Curata formular", command=self._curata_formular, width=14).grid(row=4, column=3, padx=5, pady=5)
        
        tk.Button(self._parent, text="Exporta in CSV", command=self._export_csv, width=15).grid(row=5, column=0, padx=5, pady=5)
        
        tk.Label(self._parent, text="Filtreaza dupa grad:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self._filtru_grad_combo = ttk.Combobox(self._parent, values=("(toti)", "primar", "specialist", "rezident"), state="readonly", width=15)
        self._filtru_grad_combo.set("(toti)")
        self._filtru_grad_combo.grid(row=6, column=1, padx=5, pady=5, sticky="w")
        
        tk.Button(self._parent, text="Aplica filtru", command=self._refresh_treeview, width=12).grid(row=6, column=2, padx=5, pady=5)
        
        coloane = ("id", "nume", "prenume", "grad", "telefon")
        self._tree = ttk.Treeview(self._parent, columns=coloane, show="headings", height=15)
        
        self._tree.heading("id", text="ID")
        self._tree.heading("nume", text="Nume")
        self._tree.heading("prenume", text="Prenume")
        self._tree.heading("grad", text="Grad")
        self._tree.heading("telefon", text="Telefon")
        
        self._tree.column("id", width=50, anchor="center")
        self._tree.column("nume", width=150)
        self._tree.column("prenume", width=150)
        self._tree.column("grad", width=150)
        self._tree.column("telefon", width=120)
        
        self._tree.grid(row=7, column=0, columnspan=4, padx=10, pady=10)
        
        self._tree.bind("<ButtonRelease-1>", self._on_medic_select)
    
    def _refresh_treeview(self):
        """Reincarca lista de medici, aplicand filtrul daca e setat."""
        for item in self._tree.get_children():
            self._tree.delete(item)
        
        filtru = self._filtru_grad_combo.get()
        
        for medic in self._db.listare_medici():
            if filtru and filtru != "(toti)":
                grad_clasa = medic.__class__.__name__.lower()
                if grad_clasa != filtru:
                    continue
            
            if medic.telefon:
                telefon = medic.telefon
            else:
                telefon = "-"
            
            self._tree.insert("", tk.END, values=(medic.id, medic.nume, medic.prenume, medic.grad, telefon))
    
    def _curata_formular(self):
        """Goleste toate campurile formularului."""
        self._nume_entry.delete(0, tk.END)
        self._prenume_entry.delete(0, tk.END)
        self._telefon_entry.delete(0, tk.END)
        self._grad_combo.set("")
        self._an_combo.set("")
    
    def _on_medic_select(self, event):
        """La click pe un rand din treeview, completeaza formularul."""
        selected = self._tree.focus()
        if not selected:
            return
        
        values = self._tree.item(selected, "values")
        nume = values[1]
        prenume = values[2]
        grad_complet = str(values[3])
        if values[4] != "-":
            telefon = values[4]
        else:
            telefon = ""
        
        self._curata_formular()
        self._nume_entry.insert(0, nume)
        self._prenume_entry.insert(0, prenume)
        self._telefon_entry.insert(0, telefon)
        
        if grad_complet.startswith("rezident"):
            self._grad_combo.set("rezident")
            parti = grad_complet.split()
            an = parti[-1]
            self._an_combo.set(an)
        else:
            self._grad_combo.set(grad_complet)
            self._an_combo.set("")
    
    def _citeste_formular(self):
        """
        Citeste si valideaza datele din formular. Returneaza dict sau None (cu warning afisat).
        """
        nume = self._nume_entry.get().strip()
        prenume = self._prenume_entry.get().strip()
        
        telefon = self._telefon_entry.get().strip()
        if telefon == "":
            telefon = None
        
        grad = self._grad_combo.get()
        an = self._an_combo.get()
        
        if not nume or not prenume:
            tkinter.messagebox.showwarning("Atentie", "Numele si prenumele sunt obligatorii.")
            return None
        if not grad:
            tkinter.messagebox.showwarning("Atentie", "Selecteaza un grad.")
            return None
        if grad == "rezident" and not an:
            tkinter.messagebox.showwarning("Atentie", "Selecteaza anul pentru rezident.")
            return None
        if an:
            an_int = int(an)
        else:
            an_int = None
        
        return {
            "nume": nume,
            "prenume": prenume,
            "telefon": telefon,
            "grad": grad,
            "an": an_int,
        }
    
    def _adauga_medic(self):
        """Adauga un medic nou pe baza datelor din formular."""
        date_form = self._citeste_formular()
        if date_form is None:
            return
        try:
            medic = construieste_medic(
                nume=date_form["nume"],
                prenume=date_form["prenume"],
                grad=date_form["grad"],
                an=date_form["an"],
                telefon=date_form["telefon"],
            )
            self._db.adauga_medic(medic)
            self._refresh_treeview()
            self._curata_formular()
            tkinter.messagebox.showinfo("Succes", f"Medicul {date_form['nume']} {date_form['prenume']} a fost adaugat cu succes!")
        except Exception as e:
            tkinter.messagebox.showerror("Eroare", str(e))
    
    def _modifica_medic(self):
        """Modifica un medic existent (selectat in treeview)."""
        selected = self._tree.focus()
        if not selected:
            tkinter.messagebox.showwarning("Atentie!", "Selecteaza un medic din lista pentru a-l modifica.")
            return
        id_medic = self._tree.item(selected, "values")[0]
        date_form = self._citeste_formular()
        if date_form is None:
            return
        try:
            medic = construieste_medic(
                nume=date_form["nume"],
                prenume=date_form["prenume"],
                grad=date_form["grad"],
                an=date_form["an"],
                telefon=date_form["telefon"],
                id=id_medic,
            )
            self._db.update_medic(medic)
            self._refresh_treeview()
            self._curata_formular()
            tkinter.messagebox.showinfo("Succes!", "Datele medicului au fost modificate cu succes!")
        except Exception as e:
            tkinter.messagebox.showerror("Eroare", str(e))
    
    def _sterge_medic(self):
        """Sterge medicul selectat dupa confirmare."""
        selected = self._tree.focus()
        if not selected:
            tkinter.messagebox.showwarning("Atentie!", "Selecteaza un medic din lista pentru a-l sterge.")
            return
        values = self._tree.item(selected, "values")
        id_medic = values[0]
        try:
            self._db.sterge_medic(id_medic)
            self._refresh_treeview()
            self._curata_formular()
            tkinter.messagebox.showinfo("Succes", "Medic sters.")
        except Exception as e:
            tkinter.messagebox.showerror("Eroare", str(e))
    
    def _export_csv(self):
        """Exporta toti medicii in fisier CSV."""
        cale = os.path.join(FOLDER, "medici.csv")
        try:
            with open(cale, "w", encoding="utf-8", newline="") as fisier:
                writer = csv.writer(fisier)
                writer.writerow(["id", "nume", "prenume", "grad", "an", "telefon"])
                for medic in self._db.listare_medici():
                    if isinstance(medic, Rezident):
                        grad_simplu = "rezident"
                        an = medic.an
                    else:
                        grad_simplu = medic.grad
                        an = ""
                    if medic.telefon:
                        telefon = medic.telefon
                    else:
                        telefon = ""
                    
                    writer.writerow([medic.id, medic.nume, medic.prenume, grad_simplu, an, telefon])
            tkinter.messagebox.showinfo("Exportare reusita!", f"Datele au fost salvate in:\n{cale}")
        except Exception as e:
            tkinter.messagebox.showerror("Eroare", str(e))