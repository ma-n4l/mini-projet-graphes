// ============================================================
// MINI-PROJET N°5 — Requêtes Cypher Neo4j
// Base de données : epidemie
// ============================================================


// ============================================================
// 1. INITIALISATION DE LA BASE
// ============================================================

//1.1 Verification des fichiers
// Verifier personnes . csv
LOAD CSV WITH HEADERS FROM ’ file :/// personnes . csv ’ AS row
RETURN row LIMIT 5
//Verifier contacts_clean . csv
LOAD CSV WITH HEADERS FROM ’ file :/// contacts_clean . csv ’ AS row
RETURN row LIMIT 5

// 1.2 Création de la contrainte d'unicité
CREATE CONSTRAINT personne_id IF NOT EXISTS
FOR (p:Personne) REQUIRE p.id IS UNIQUE

// 1.3 Vérification des contraintes
SHOW CONSTRAINTS

// 1.4 Import des noeuds
LOAD CSV WITH HEADERS FROM 'file:///personnes.csv' AS row
CREATE (:Personne {
  id:         toInteger(row.id),
  nom:        row.nom,
  age:        toInteger(row.age),
  classe:     row.classe,
  region:     row.region,
  infected:   toBoolean(row.infected),
  vaccinated: toBoolean(row.vaccinated)
})

// 1.5 Vérification import noeuds
MATCH (p:Personne) RETURN COUNT(p) AS total_noeuds

// 1.6 Import des relations
LOAD CSV WITH HEADERS FROM 'file:///contacts_clean.csv' AS row
MATCH (a:Personne {id: toInteger(row.source)})
MATCH (b:Personne {id: toInteger(row.target)})
CREATE (a)-[:CONTACT {
  nb_contacts: toInteger(row.nb_contacts)
}]->(b)

// 1.7 Vérification import relations
MATCH ()-[r:CONTACT]->() RETURN COUNT(r) AS total_relations


// ============================================================
// 2. STATISTIQUES GÉNÉRALES
// ============================================================

// 2.1 Nombre total des personnes
MATCH (p:Personne)
RETURN COUNT(p) AS total_personnes

// 2.2 Nombre de personnes infectées
MATCH (p:Personne {infected: true})
RETURN COUNT(p) AS total_infectes

// 2.3 Nombre de personnes vaccinées
MATCH (p:Personne {vaccinated: true})
RETURN COUNT(p) AS total_vaccines

// 2.4 Taux d'infection par classe
MATCH (p:Personne {infected: true})
RETURN p.classe AS classe,
       COUNT(p) AS nb_infectes
ORDER BY nb_infectes DESC


// ============================================================
// 3. ANALYSE DES ZONES À RISQUE
// ============================================================

// 3.1 Régions les plus touchées
MATCH (p:Personne {infected: true})
RETURN p.region AS region,
       COUNT(p) AS nb_infectes,
       COUNT(CASE WHEN p.vaccinated = true
             THEN 1 END) AS vaccines
ORDER BY nb_infectes DESC

// 3.2 Cas urgents (infectés et non vaccinés)
MATCH (p:Personne {infected: true, vaccinated: false})
RETURN p.region AS region,
       p.classe AS classe,
       COUNT(p) AS cas_urgents
ORDER BY cas_urgents DESC


// ============================================================
// 4. IDENTIFICATION DES SUPER-PROPAGATEURS
// ============================================================

// 4.1 Top 10 personnes avec le plus de contacts
MATCH (p:Personne)-[:CONTACT]->(other)
RETURN DISTINCT p.nom AS nom,
       p.classe AS classe,
       p.infected AS infecte,
       p.region AS region,
       COUNT(other) AS nb_contacts
ORDER BY nb_contacts DESC
LIMIT 10

// 4.2 Super-propagateurs infectés (les plus dangereux)
MATCH (p:Personne {infected: true})-[:CONTACT]->(other)
RETURN DISTINCT p.nom AS nom,
       p.classe AS classe,
       p.region AS region,
       COUNT(other) AS nb_contacts
ORDER BY nb_contacts DESC
LIMIT 10


// ============================================================
// 5. ANALYSE DE PROPAGATION
// ============================================================

// 5.1 Qui a été en contact avec une personne infectée ?
MATCH (infecte:Personne {infected: true})
      -[:CONTACT]->(contact:Personne)
RETURN DISTINCT infecte.nom AS personne_infectee,
       contact.nom AS contact_a_risque,
       contact.vaccinated AS est_vaccine,
       contact.region AS region
ORDER BY contact.vaccinated ASC
LIMIT 20

// 5.2 Chaîne de propagation sur 2 niveaux
MATCH (p1:Personne {infected: true})
      -[:CONTACT*1..2]->(p2:Personne)
WHERE p1 <> p2
RETURN DISTINCT p1.nom AS source_infection,
       p2.nom AS personne_exposee,
       p2.vaccinated AS est_vaccine
LIMIT 20

// 5.3 Contacts entre 2 personnes infectées
MATCH (a:Personne {infected: true})
      -[:CONTACT]->(b:Personne {infected: true})
RETURN DISTINCT a.nom AS infecte1,
       b.nom AS infecte2,
       a.region AS region
LIMIT 20


// ============================================================
// 6. ANALYSE PAR CLASSE
// ============================================================

// 6.1 Taux d'infection et vaccination par classe
MATCH (p:Personne)
RETURN p.classe AS classe,
       COUNT(p) AS total,
       SUM(CASE WHEN p.infected = true
           THEN 1 ELSE 0 END) AS infectes,
       SUM(CASE WHEN p.vaccinated = true
           THEN 1 ELSE 0 END) AS vaccines
ORDER BY infectes DESC

// 6.2 Classes avec le plus de contacts
MATCH (p:Personne)-[:CONTACT]->(other)
RETURN p.classe AS classe,
       COUNT(other) AS total_contacts
ORDER BY total_contacts DESC


// ============================================================
// 7. RECOMMANDATIONS VACCINATION
// ============================================================

// 7.1 Priorité vaccination : infectés non vaccinés
//     avec beaucoup de contacts
MATCH (p:Personne {infected: true, vaccinated: false})
      -[:CONTACT]->(other)
RETURN DISTINCT p.nom AS nom,
       p.classe AS classe,
       p.region AS region,
       COUNT(other) AS nb_contacts
ORDER BY nb_contacts DESC
LIMIT 10

// 7.2 Régions prioritaires pour la vaccination
MATCH (p:Personne {vaccinated: false})
RETURN p.region AS region,
       COUNT(p) AS non_vaccines,
       SUM(CASE WHEN p.infected = true
           THEN 1 ELSE 0 END) AS infectes_non_vaccines
ORDER BY infectes_non_vaccines DESC


// ============================================================
// 8. VISUALISATION DU GRAPHE
// ============================================================

// 8.1 Visualiser infectés et leurs contacts
MATCH (p:Personne {infected: true})-[r:CONTACT]->(other)
RETURN p, r, other
LIMIT 50

// 8.2 Visualiser par région
MATCH (p:Personne {region: "Casablanca"})-[r:CONTACT]->(other)
RETURN p, r, other
LIMIT 30


// ============================================================
// 9. NETTOYAGE (À UTILISER AVEC PRÉCAUTION)
// ============================================================

// 9.1 Supprimer toutes les relations
// MATCH ()-[r:CONTACT]->() DELETE r

// 9.2 Supprimer tout le graphe
// MATCH (n) DETACH DELETE n

// ============================================================
// FIN DES REQUÊTES
// ============================================================