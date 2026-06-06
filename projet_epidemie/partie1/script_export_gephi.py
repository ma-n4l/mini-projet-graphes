from neo4j import GraphDatabase
import networkx as nx

# Connexion
driver = GraphDatabase.driver(
    "bolt://127.0.0.1:7687", 
    auth=("neo4j", "projet_epidemiedb"))

G = nx.Graph()

with driver.session(database="epidemie") as session:
    
    # Récupérer les nœuds
    nodes = session.run("""
        MATCH (p:Personne) 
        RETURN p.id AS id, p.nom AS nom, 
               p.classe AS classe, p.region AS region,
               p.infected AS infected
    """)
    
    for record in nodes:
        G.add_node(record["id"], 
                   nom=record["nom"],
                   classe=record["classe"],
                   region=record["region"],
                   infected=record["infected"])
    
    # Récupérer les relations
    relations = session.run("""
        MATCH (a:Personne)-[:CONTACT]->(b:Personne)
        RETURN DISTINCT a.id AS source, b.id AS target
    """)
    
    for record in relations:
        G.add_edge(record["source"], record["target"])

# Exporter en GraphML pour Gephi
nx.write_graphml(G, "epidemie.graphml")
print(f"✅ Exporté : {G.number_of_nodes()} nœuds, "
      f"{G.number_of_edges()} relations")