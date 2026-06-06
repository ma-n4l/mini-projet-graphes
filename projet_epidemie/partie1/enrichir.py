import pandas as pd
import random

# Lire personnes.csv existant
personnes = pd.read_csv('personnes.csv')

print(f"Nombre de personnes: {len(personnes)}")
print(personnes.head(3))

random.seed(42)

# Noms fictifs
prenoms = ["Ahmed","Sara","Youssef","Fatima","Mohamed",
           "Aisha","Omar","Nadia","Hassan","Leila",
           "Karim","Meryem","Bilal","Houda","Anas",
           "Imane","Zakaria","Salma","Reda","Ghita"]

regions = ["Casablanca","Rabat","Fes","Marrakech",
           "Tanger","Agadir","Meknes","Oujda"]

# Ajouter les propriétés
personnes['nom'] = [f"{random.choice(prenoms)}_{i}" 
                    for i in personnes['id']]

personnes['age'] = [random.randint(15, 25) 
                    for _ in range(len(personnes))]

personnes['region'] = [random.choice(regions) 
                       for _ in range(len(personnes))]

# 20% infectés (réaliste pour une épidémie)
personnes['infected'] = [random.choices(
                         [True, False], 
                         weights=[20, 80])[0]
                         for _ in range(len(personnes))]

# 40% vaccinés
personnes['vaccinated'] = [random.choices(
                           [True, False], 
                           weights=[40, 60])[0]
                           for _ in range(len(personnes))]

# Sauvegarder
with open('personnes.csv', 'w') as f:
    f.write('id,classe,nom,age,region,infected,vaccinated\n')
    for _, row in personnes.iterrows():
        f.write(f"{row['id']},{row['classe']},{row['nom']},"
                f"{row['age']},{row['region']},"
                f"{row['infected']},{row['vaccinated']}\n")

print("✅ personnes.csv enrichi avec succès !")
print(f"Aperçu:")
print(personnes[['id','nom','age','region',
                  'infected','vaccinated']].head(10))