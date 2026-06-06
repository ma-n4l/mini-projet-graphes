import pandas as pd

# Lire contacts.csv
contacts = pd.read_csv('contacts.csv')

# Compter le nombre de contacts entre chaque paire
contacts_grouped = contacts.groupby(
    ['source', 'target']).size().reset_index(name='nb_contacts')

# Sauvegarder
with open('contacts_clean.csv', 'w') as f:
    f.write('source,target,nb_contacts\n')
    for _, row in contacts_grouped.iterrows():
        f.write(f"{int(row['source'])},{int(row['target'])},"
                f"{int(row['nb_contacts'])}\n")

print(f"✅ Avant : {len(contacts)} relations")
print(f"✅ Après : {len(contacts_grouped)} relations uniques")