import pandas as pd

# Lire avec séparateur ;
df = pd.read_csv('contacts_highschool.csv', sep=';')

# Vérifier
print("Colonnes:", df.columns.tolist())
print(df.head(3))

# Créer contacts.csv en forçant la virgule
contacts = df[['source', 'target', 'timestamp']].copy()

# Écrire manuellement avec virgule
with open('contacts.csv', 'w') as f:
    f.write('source,target,timestamp\n')
    for _, row in contacts.iterrows():
        f.write(f"{row['source']},{row['target']},{row['timestamp']}\n")

print(f"✅ contacts.csv créé : {len(contacts)} lignes")

# Créer personnes.csv
source_p = df[['source', 'class1']].rename(columns={'source':'id','class1':'classe'})
target_p = df[['target', 'class2']].rename(columns={'target':'id','class2':'classe'})
personnes = pd.concat([source_p, target_p]).drop_duplicates(subset='id').sort_values('id')

with open('personnes.csv', 'w') as f:
    f.write('id,classe\n')
    for _, row in personnes.iterrows():
        f.write(f"{row['id']},{row['classe']}\n")

print(f"✅ personnes.csv créé : {len(personnes)} personnes")