from tkinter import *
from tkinter import ttk
import mysql.connector as mysc
from tkinter import messagebox

# Connexion à la base de données
def connect_to_db():
    return mysc.connect(host="localhost", user="root", password="ROOT", database="hopital")

# Compter les patients pour générer le matricule
def count_patient():
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT MAX(CAST(SUBSTRING(matricule, 6) AS UNSIGNED)) FROM patients")
        dernier_num = cur.fetchone()[0]
        if dernier_num is None:
            return "24SJI1"
        return f"24SJI{dernier_num + 1}"
    except:
        return "24SJI1"
    finally:
        cur.close()
        conn.close()


# Fonctions CRUD
def ajouter():
    if not modifier_mode[0]:
        matricule = matricule_var.get()
        nom = nom_entry.get()
        prenom = prenom_entry.get()
        age = age_entry.get()
        adresse = adresse_entry.get()
        telephone = telephone_entry.get()
        remarque = remarque_entry.get()

        try:
            conn = connect_to_db()
            cur = conn.cursor()
            cur.execute("SELECT matricule FROM patients WHERE matricule=%s", (matricule,))
            if cur.fetchone():
                messagebox.showwarning("Attention", "Ce matricule existe déjà !")
                return
            cur.execute("INSERT INTO patients (matricule, nom, prenom, age, adresse, telephone, remarque) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (matricule, nom, prenom, age, adresse, telephone, remarque))
            conn.commit()
            messagebox.showinfo("Succès", "Patient enregistré avec succès !")
            vider_champs()
            actualiser_liste_patients()
        except mysc.Error as e:
            messagebox.showerror("Erreur", str(e))
        finally:
            cur.close()
            conn.close()
    else:
        matricule = matricule_var.get()
        try:
            conn = connect_to_db()
            cur = conn.cursor()
            cur.execute("UPDATE patients SET nom=%s, prenom=%s, age=%s, adresse=%s, telephone=%s, remarque=%s WHERE matricule=%s",
                        (nom_entry.get(), prenom_entry.get(), age_entry.get(), adresse_entry.get(), telephone_entry.get(), remarque_entry.get(), matricule))
            conn.commit()
            messagebox.showinfo("Succès", "Modifications enregistrées avec succès.")
            vider_champs()
            actualiser_liste_patients()
            modifier_mode[0] = False
        except mysc.Error as e:
            messagebox.showerror("Erreur", str(e))
        finally:
            cur.close()
            conn.close()

def modifier():
    if not matricule_var.get():
        messagebox.showwarning("Alerte", "Veuillez d'abord sélectionner un patient.")
        return
    modifier_mode[0] = True
    for entry in [nom_entry, prenom_entry, age_entry, adresse_entry, telephone_entry, remarque_entry]:
        entry.config(state=NORMAL)
    messagebox.showinfo("Modification", "Une fois la modification terminée, Cliquez sur 'Enregistrer' pour valider.")

def supprimer():
    if messagebox.askquestion("Confirmation", "Voulez-vous supprimer ce patient ?") == 'yes':
        matricule = matricule_var.get()
        try:
            conn = connect_to_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM patients WHERE matricule=%s", (matricule,))
            conn.commit()
            messagebox.showinfo("Succès", "Patient supprimé.")
            vider_champs()
            actualiser_liste_patients()
        except mysc.Error as e:
            messagebox.showerror("Erreur", str(e))
        finally:
            cur.close()
            conn.close()

# Vider les champs et générer un nouveau matricule
def vider_champs():
    matricule_var.set(count_patient())
    for entry in [nom_entry, prenom_entry, age_entry, adresse_entry, telephone_entry, remarque_entry]:
        entry.config(state=NORMAL)
        entry.delete(0, END)

# Suivi du dernier patient sélectionné
dernier_patient_selectionne = [""]

def reagir_clic(event):
    global dernier_patient_selectionne
    selected = tableau.focus()
    if not selected:
        return

    valeurs = tableau.item(selected, 'values')
    matricule_actuel = valeurs[0]

    if matricule_actuel == dernier_patient_selectionne[0]:
        vider_champs()
        for entry in [nom_entry, prenom_entry, age_entry, adresse_entry, telephone_entry, remarque_entry]:
            entry.config(state=NORMAL)
        tableau.selection_remove(tableau.focus())
        modifier_mode[0] = False
        dernier_patient_selectionne[0] = ""
    else:
        matricule_var.set(matricule_actuel)
        entries_data = [valeurs[1], valeurs[2], valeurs[3], valeurs[4], valeurs[5], valeurs[6]]
        for entry, value in zip([nom_entry, prenom_entry, age_entry, adresse_entry, telephone_entry, remarque_entry], entries_data):
            entry.config(state=NORMAL)
            entry.delete(0, END)
            entry.insert(0, value)
            entry.config(state=DISABLED)
        modifier_mode[0] = False
        dernier_patient_selectionne[0] = matricule_actuel

def actualiser_liste_patients():
    for i in tableau.get_children():
        tableau.delete(i)
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM patients")
        for row in cur.fetchall():
            tableau.insert("", END, values=row)
    except Exception as e:
        print("Erreur lors du chargement :", e)
    finally:
        cur.close()
        conn.close()

# Interface
root = Tk()
root.title("Gestion des patients - Saint Jean Hôpital")
root.configure(bg="#adeca5")

matricule_var = StringVar(value=count_patient())
modifier_mode = [False]

titre = Label(root, text="APPLICATION DE GESTION DES PATIENTS", font=("Helvetica", 18, "bold"), fg='black', bg='#adeca5')
titre.grid(row=0, column=0, columnspan=2, pady=20)

form_frame = Frame(root, bg='#adeca5')
form_frame.grid(row=1, column=0, padx=20, sticky="n")

Label(form_frame, text="Matricule:", bg='#adeca5').grid(row=0, column=0, sticky="w")
matricule_entry = Entry(form_frame, textvariable=matricule_var, state=DISABLED)
matricule_entry.grid(row=0, column=1, pady=5)

labels = ["Nom", "Prénom", "Âge", "Adresse", "Téléphone", "Remarque"]
entries = []
for i, lab in enumerate(labels):
    Label(form_frame, text=f"{lab}:", bg='#adeca5').grid(row=i+1, column=0, sticky="w")
    e = Entry(form_frame)
    e.grid(row=i+1, column=1, pady=5)
    entries.append(e)

nom_entry, prenom_entry, age_entry, adresse_entry, telephone_entry, remarque_entry = entries

Button(form_frame, text="Enregistrer", command=ajouter, bg='#adeca5', fg='black').grid(row=7, column=0, pady=10)
Button(form_frame, text="Modifier", command=modifier, bg='#adeca5', fg='black').grid(row=7, column=1)
Button(form_frame, text="Supprimer", command=supprimer, bg='#adeca5', fg='black').grid(row=8, column=0, columnspan=2, pady=5)

# Affichage liste patients
liste_frame = Frame(root, bg='#adeca5')
liste_frame.grid(row=1, column=1, padx=10)

Label(liste_frame, text="Liste des patients", font=("Helvetica", 14, "bold"), bg="#adeca5", fg="black").pack(pady=5)

scrollbar = Scrollbar(liste_frame)
scrollbar.pack(side=RIGHT, fill=Y)

entetes = ["Matricule", "Nom", "Prénom", "Age", "Adresse", "Téléphone", "Remarque"]
tableau = ttk.Treeview(liste_frame, columns=entetes, show="headings", yscrollcommand=scrollbar.set, height=15)
for col in entetes:
    tableau.heading(col, text=col)
    tableau.column(col, width=100)
tableau.pack()
tableau.bind("<ButtonRelease-1>", reagir_clic)
scrollbar.config(command=tableau.yview)

actualiser_liste_patients()
root.mainloop()