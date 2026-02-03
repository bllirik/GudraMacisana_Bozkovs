import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_NAME = "Datubaze_projekts_Bozkovs.db"


def q(name: str) -> str:
    """SQL identifikatoru pēdiņas. Vajag, jo ir kolonna 'e-pasts' ar defisi."""
    return '"' + name.replace('"', '""') + '"'


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GudrāMācīšanās — Klienti (SQLite + Tkinter)")
        self.geometry("950x550")

        
        try:
            self.con = sqlite3.connect(DB_NAME)
        except Exception as e:
            messagebox.showerror("DB kļūda", f"Nevar atvērt datubāzi:\n{DB_NAME}\n\n{e}")
            raise

        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

        self.selected_id = None  

        self.build_ui()
        self.refresh_table()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        try:
            self.con.commit()
            self.con.close()
        finally:
            self.destroy()

    
    def build_ui(self):
        form = ttk.LabelFrame(self, text="Klients")
        form.pack(fill="x", padx=10, pady=10)

        self.vards = tk.StringVar()
        self.uzvards = tk.StringVar()
        self.talrunis = tk.StringVar()
        self.epasts = tk.StringVar()
        self.search = tk.StringVar()

       
        ttk.Label(form, text="Vārds").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        ttk.Entry(form, textvariable=self.vards, width=18).grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(form, text="Uzvārds").grid(row=0, column=2, padx=8, pady=8, sticky="w")
        ttk.Entry(form, textvariable=self.uzvards, width=18).grid(row=0, column=3, padx=8, pady=8)

        ttk.Label(form, text="Tālrunis").grid(row=0, column=4, padx=8, pady=8, sticky="w")
        ttk.Entry(form, textvariable=self.talrunis, width=18).grid(row=0, column=5, padx=8, pady=8)

        ttk.Label(form, text="E-pasts").grid(row=0, column=6, padx=8, pady=8, sticky="w")
        ttk.Entry(form, textvariable=self.epasts, width=22).grid(row=0, column=7, padx=8, pady=8)

      
        btns = ttk.Frame(form)
        btns.grid(row=1, column=0, columnspan=8, sticky="w", padx=8, pady=(0, 10))

        ttk.Button(btns, text="Pievienot", command=self.add_client).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Labot", command=self.update_client).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Dzēst", command=self.delete_client).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Notīrīt formu", command=self.clear_form).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Refresh", command=self.refresh_table).pack(side="left")

     
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=(0, 8))

        ttk.Label(search_frame, text="Meklēt:").pack(side="left")
        ttk.Entry(search_frame, textvariable=self.search, width=35).pack(side="left", padx=8)
        ttk.Button(search_frame, text="Meklēt", command=self.refresh_table).pack(side="left")
        ttk.Button(search_frame, text="Parādīt visu", command=self.reset_search).pack(side="left", padx=8)

      
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        cols = ("klients_id", "vards", "uzvards", "talrunis", "e-pasts")
        self.tv = ttk.Treeview(table_frame, columns=cols, show="headings")

        for c in cols:
            self.tv.heading(c, text=c)
            self.tv.column(c, width=170, anchor="w")
        self.tv.column("klients_id", width=90, anchor="center")

        ysb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tv.yview)
        self.tv.configure(yscroll=ysb.set)

        self.tv.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.tv.bind("<<TreeviewSelect>>", self.on_select)

 
    def run(self, sql: str, params=()):
        try:
            self.cur.execute(sql, params)
            self.con.commit()
            return True
        except Exception as e:
            messagebox.showerror("DB kļūda", f"{e}\n\nSQL:\n{sql}\n\nParams:\n{params}")
            return False

    def fetchall(self, sql: str, params=()):
        try:
            self.cur.execute(sql, params)
            return self.cur.fetchall()
        except Exception as e:
            messagebox.showerror("DB kļūda", f"{e}\n\nSQL:\n{sql}\n\nParams:\n{params}")
            return []

  
    def clear_form(self):
        self.selected_id = None
        self.vards.set("")
        self.uzvards.set("")
        self.talrunis.set("")
        self.epasts.set("")
        self.tv.selection_remove(self.tv.selection())

    def reset_search(self):
        self.search.set("")
        self.refresh_table()

    def on_select(self, _event):
        sel = self.tv.selection()
        if not sel:
            return
        values = self.tv.item(sel[0])["values"]
        self.selected_id = values[0]
        self.vards.set(values[1] or "")
        self.uzvards.set(values[2] or "")
        self.talrunis.set(values[3] or "")
        self.epasts.set(values[4] or "")

    def refresh_table(self):
        
        for item in self.tv.get_children():
            self.tv.delete(item)

        text = self.search.get().strip()
        where = ""
        params = []

        if text:
            
            where = f"""
                WHERE CAST({q('vards')} AS TEXT) LIKE ?
                   OR CAST({q('uzvards')} AS TEXT) LIKE ?
                   OR CAST({q('talrunis')} AS TEXT) LIKE ?
                   OR CAST({q('e-pasts')} AS TEXT) LIKE ?
            """
            like = f"%{text}%"
            params = [like, like, like, like]

        sql = f"""
            SELECT {q('klients_id')}, {q('vards')}, {q('uzvards')}, {q('talrunis')}, {q('e-pasts')}
            FROM {q('Klienti')}
            {where}
            ORDER BY {q('klients_id')} DESC
        """

        rows = self.fetchall(sql, params)
        for r in rows:
            self.tv.insert("", "end", values=[r["klients_id"], r["vards"], r["uzvards"], r["talrunis"], r["e-pasts"]])

    def add_client(self):
        v = self.vards.get().strip()
        u = self.uzvards.get().strip()
        t = self.talrunis.get().strip()
        e = self.epasts.get().strip()

        if not (v and u and t and e):
            messagebox.showwarning("Nepietiek dati", "Aizpildi visus laukus!")
            return

        sql = f"""
            INSERT INTO {q('Klienti')} ({q('vards')}, {q('uzvards')}, {q('talrunis')}, {q('e-pasts')})
            VALUES (?, ?, ?, ?)
        """
        if self.run(sql, (v, u, t, e)):
            self.clear_form()
            self.refresh_table()

    def update_client(self):
        if self.selected_id is None:
            messagebox.showinfo("Nav izvēlēts", "Izvēlies klientu tabulā, lai labotu.")
            return

        v = self.vards.get().strip()
        u = self.uzvards.get().strip()
        t = self.talrunis.get().strip()
        e = self.epasts.get().strip()

        if not (v and u and t and e):
            messagebox.showwarning("Nepietiek dati", "Aizpildi visus laukus!")
            return

        sql = f"""
            UPDATE {q('Klienti')}
            SET {q('vards')}=?, {q('uzvards')}=?, {q('talrunis')}=?, {q('e-pasts')}=?
            WHERE {q('klients_id')}=?
        """
        if self.run(sql, (v, u, t, e, self.selected_id)):
            self.clear_form()
            self.refresh_table()

    def delete_client(self):
        if self.selected_id is None:
            messagebox.showinfo("Nav izvēlēts", "Izvēlies klientu tabulā, lai dzēstu.")
            return

        if not messagebox.askyesno("Apstiprināt", f"Dzēst klientu klients_id={self.selected_id}?"):
            return

        sql = f"DELETE FROM {q('Klienti')} WHERE {q('klients_id')}=?"
        if self.run(sql, (self.selected_id,)):
            self.clear_form()
            self.refresh_table()


if __name__ == "__main__":
    App().mainloop()
