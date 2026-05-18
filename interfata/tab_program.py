import csv
import os
from datetime import date
 
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
 
from clase import EroareAtribuireGarda
  
LUNI_NUME = {1: "Ianuarie", 2: "Februarie", 3: "Martie", 4: "Aprilie",
    5: "Mai", 6: "Iunie", 7: "Iulie", 8: "August",
    9: "Septembrie", 10: "Octombrie", 11: "Noiembrie", 12: "Decembrie"}
 
FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
 
class TabProgram:
    """Tab pentru generarea si exportarea programului de garzi."""

    def __init__(self, parent, db, algoritm):
        self._parent = parent
        self._db = db
        self._algoritm = algoritm
        
        self._build_interface()
    
    def _build_interface(self):
        tk.Label(self._parent, text="Luna").grid(row=0, column=0, padx=5, pady=10)
        self._luna_combo = ttk.Combobox(self._parent, values=tuple(LUNI_NUME.values()), width=15)
        self._luna_combo.grid(row=0, column=1, padx=5, pady=10)
        
        astazi = date.today()
        self._luna_combo.set(LUNI_NUME[astazi.month])
        
        tk.Label(self._parent, text="An").grid(row=0, column=2, padx=5, pady=10)
        self._an_entry = tk.Entry(self._parent, width=8)
        self._an_entry.insert(0, str(astazi.year))
        self._an_entry.grid(row=0, column=3, padx=5, pady=10)
        
        tk.Button(self._parent, text="Genereaza si exporta program", command=self._genereaza_si_exporta_program, width=30).grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        
        tk.Button(self._parent, text="Genereaza si exporta statistici", command=self._genereaza_si_exporta_statistici, width=30).grid(row=1, column=2, columnspan=2, padx=5, pady=10)
        
    def _get_an_luna(self):
        """
        Citeste si valideaza luna si anul.
        Returneaza (an, luna) sau (None, None) cu warning.
        """
        luna_nume = self._luna_combo.get()
        if not luna_nume:
            tkinter.messagebox.showwarning("Atentie", "Selecteaza o luna.")
            return None, None
        
        luna = None
        for nr, nume in LUNI_NUME.items():
            if nume == luna_nume:
                luna = nr
                break
        
        an_str = self._an_entry.get().strip()
        if not an_str.isdigit():
            tkinter.messagebox.showwarning("Atentie", "Anul trebuie sa fie un numar.")
            return None, None
        
        return int(an_str), luna
    
    def _numara_garzi_pe_medic(self, garzi, doar_weekend=False):
        """
        Numara cate garzi are fiecare medic.
        Returneaza dict: {medic_id: nr_garzi}
        """
        contoare = {}
        for g in garzi:
            if doar_weekend and not g.este_weekend():
                continue
            if g.medic_id in contoare:
                contoare[g.medic_id] += 1
            else:
                contoare[g.medic_id] = 1
        return contoare
    
    def _genereaza_si_exporta_program(self):
        """Genereaza programul lunii si il exporta direct in CSV."""
        an, luna = self._get_an_luna()
        if an is None:
            return
        try:
            garzi = self._algoritm.genereaza_program(an, luna)
            
            linii = self._db.listare_linii_garda()
            medici_dict = {}
            for m in self._db.listare_medici():
                medici_dict[m.id] = m
            
            garzi_pe_data = {}
            for g in garzi:
                if g.data not in garzi_pe_data:
                    garzi_pe_data[g.data] = {}
                garzi_pe_data[g.data][g.linie_id] = g.medic_id
            
            nume_fisier = f"program_garzi_{an}_{luna:02d}.csv"
            cale = os.path.join(FOLDER, nume_fisier)
            with open(cale, "w", encoding="utf-8", newline="") as fisier:
                writer = csv.writer(fisier)
                header = ["Data", "Weekend"]
                for linie in linii:
                    header.append(linie.nume)
                writer.writerow(header)
                for data in sorted(garzi_pe_data.keys()):
                    if data.weekday() >= 5:
                        weekend = "DA"
                    else:
                        weekend = "NU"
                    rand = [data.isoformat(), weekend]
                    for linie in linii:
                        medic_id = garzi_pe_data[data].get(linie.id)
                        if medic_id is not None:
                            medic = medici_dict.get(medic_id)
                            if medic:
                                rand.append(f"{medic.nume} {medic.prenume}")
                            else:
                                rand.append("")
                        else:
                            rand.append("")
                    writer.writerow(rand)
            
            tkinter.messagebox.showinfo("Succes!", f"Program generat cu succes pentru {LUNI_NUME[luna]} {an}.\n\n")
                    
        except EroareAtribuireGarda as e:
            tkinter.messagebox.showerror("Conflict atribuire", str(e))
        except Exception as e:
            tkinter.messagebox.showerror("Eroare", str(e))
    
    def _genereaza_si_exporta_statistici(self):
        """Genereaza programul si exporta statisticile de echitate in CSV."""
        an, luna = self._get_an_luna()
        if an is None:
            return
        try:
            garzi = self._algoritm.genereaza_program(an, luna)
            
            contoare = self._numara_garzi_pe_medic(garzi)
            contoare_wknd = self._numara_garzi_pe_medic(garzi, doar_weekend=True)
            
            medici_dict = {}
            for m in self._db.listare_medici():
                medici_dict[m.id] = m
            
            nume_fisier = f"statistici_garzi_{an}_{luna:02d}.csv"
            cale = os.path.join(FOLDER, nume_fisier)
            with open(cale, "w", encoding="utf-8", newline="") as fisier:
                writer = csv.writer(fisier)
                writer.writerow(["Medic", "Grad", "Total garzi", "Garzi weekend"])
                for medic_id in sorted(contoare.keys()):
                    nr = contoare[medic_id]
                    medic = medici_dict.get(medic_id)
                    if medic:
                        writer.writerow([f"{medic.nume} {medic.prenume}", medic.grad, nr, contoare_wknd.get(medic_id, 0)])
            
            tkinter.messagebox.showinfo("Succes!", f"Statistica generata cu succes pentru {LUNI_NUME[luna]} {an}.\n\n")
        
        except EroareAtribuireGarda as e:
            tkinter.messagebox.showerror("Conflict atribuire", str(e))
        except Exception as e:
            tkinter.messagebox.showerror("Eroare", str(e))