import pandas as pd
import networkx as nx
from networkx.algorithms.community import label_propagation_communities, modularity

print("=== ENCOURS : EXÉCUTION DE LA PARTIE 3 (LPA) ===")

# 1. Chargement des données de la Partie 1
noeuds_df = pd.read_csv("personnes.csv")
aretes_df = pd.read_csv("contacts_clean.csv")

# 2. Création du graphe NetworkX
G = nx.Graph()

# Ajout des nœuds avec leurs attributs
for _, row in noeuds_df.iterrows():
    G.add_node(
        int(row['id']), 
        label=str(row['nom']), 
        classe=str(row['classe']),
        age=int(row['age']), 
        region=str(row['region']),
        infected=str(row['infected']),
        vaccinated=str(row['vaccinated'])
    )

# Ajout des arêtes avec le nombre de contacts (poids)
for _, row in aretes_df.iterrows():
    G.add_edge(int(row['source']), int(row['target']), weight=int(row['nb_contacts']))

# 3. Application de l'algorithme LPA (Détection des communautés)
print("\n[Étape 1] Application de l'algorithme Label Propagation (LPA)...")
communautes_lpa = list(label_propagation_communities(G))

# 4. Mesure de la qualité avec la Modularité Q
print("[Étape 2] Calcul de la qualité du découpage...")
score_q = modularity(G, communautes_lpa)

print(f"\nRésultats de l'analyse :")
print(f" -> Nombre total d'individus (Nœuds) : {G.number_of_nodes()}")
print(f" -> Nombre de foyers/communautés détectés : {len(communautes_lpa)}")
print(f" -> Score de Modularité (Q) : {score_q:.4f}")

# 5. Injection des communautés dans le graphe pour Gephi
for id_communaute, communaute in enumerate(communautes_lpa):
    for noeud in communaute:
        G.nodes[noeud]['Community_LPA'] = str(id_communaute)

# 6. Exportation du fichier final pour Gephi
nom_export = "graphe_final_lpa.gexf"
nx.write_gexf(G, nom_export)
print(f"\n✅ Succès ! Le fichier '{nom_export}' a été généré.")
print("Tu peux maintenant l'ouvrir dans Gephi pour colorer tes communautés.")