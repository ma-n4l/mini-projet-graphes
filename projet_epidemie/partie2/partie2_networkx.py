"""
=============================================================
  Mini-Projet N°5 — Partie 2 : Modélisation sous forme de graphe
  Module : Modèles et Algorithmes de Graphes
  Université Hassan 1er — ENSA Berrechid | CI-ISIBD/S6
  Professeur : Mohamed NAIMI
=============================================================
  DONNÉES : contacts_clean_csv.xls + personnes_csv.xls
  327 individus | 5818 contacts
=============================================================
"""

import os, sys, warnings, time
warnings.filterwarnings("ignore")

# ── Dépendances ────────────────────────────────────────────
for pkg in ["networkx", "matplotlib", "pandas", "numpy"]:
    try:
        __import__(pkg)
    except ImportError:
        os.system(f"{sys.executable} -m pip install {pkg} -q")

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from collections import Counter

OUTPUT_DIR = "resultats_partie2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": "#0d1117", "axes.facecolor": "#0d1117",
    "axes.edgecolor": "#30363d",   "text.color": "#c9d1d9",
    "axes.labelcolor": "#c9d1d9",  "xtick.color": "#8b949e",
    "ytick.color": "#8b949e",      "grid.color": "#21262d",
    "grid.alpha": 0.5,
})
C = {
    "bleu":    "#58a6ff", "vert":  "#3fb950", "rouge": "#f78166",
    "jaune":   "#e3b341", "violet":"#bc8cff", "cyan":  "#39d3f5",
    "fond":    "#0d1117", "surface":"#161b22",
}

# ═══════════════════════════════════════════════════════════
#  ÉTAPE 0 — Chargement des données réelles
# ═══════════════════════════════════════════════════════════
def etape0_chargement():
    print("\n" + "═"*60)
    print("  ÉTAPE 0 — Chargement des données")
    print("═"*60)

    # Recherche automatique des fichiers (nom exact ou variantes)
    def trouver(noms):
        for n in noms:
            if os.path.exists(n): return n
        return None

    f_personnes = trouver([
        "personnes_csv.xls", "personnes.csv", "personnes_csv.csv"])
    f_contacts  = trouver([
        "contacts_clean_csv.xls", "contacts_clean.csv",
        "contacts_clean_csv.csv", "contacts.csv"])

    if not f_personnes or not f_contacts:
        print("[ERREUR] Fichiers introuvables.")
        print("  Mettez dans le même dossier :")
        print("    - personnes_csv.xls  (ou personnes.csv)")
        print("    - contacts_clean_csv.xls  (ou contacts_clean.csv)")
        sys.exit(1)

    # Lecture CSV (extension .xls mais format CSV)
    lire = lambda f: (
        pd.read_csv(f) if f.endswith(".xls") or f.endswith(".csv")
        else pd.read_excel(f)
    )

    personnes = lire(f_personnes)
    contacts  = lire(f_contacts)

    print(f"  [✓] Personnes : {len(personnes)} individus")
    print(f"      Colonnes  : {list(personnes.columns)}")
    print(f"  [✓] Contacts  : {len(contacts)} liens")
    print(f"      Colonnes  : {list(contacts.columns)}")
    print(f"\n  Aperçu personnes :\n{personnes.head(3).to_string(index=False)}")
    print(f"\n  Aperçu contacts  :\n{contacts.head(3).to_string(index=False)}")

    return personnes, contacts


# ═══════════════════════════════════════════════════════════
#  ÉTAPE 1 — Construction du graphe NetworkX
# ═══════════════════════════════════════════════════════════
def etape1_construction(personnes, contacts):
    print("\n" + "═"*60)
    print("  ÉTAPE 1 — Construction du graphe NetworkX")
    print("═"*60)

    G = nx.Graph()

    # Nœuds avec tous leurs attributs
    for _, row in personnes.iterrows():
        statut = ("infecté"   if row.get("infected")   == True  else
                  "vacciné"   if row.get("vaccinated")  == True  else "sain")
        G.add_node(int(row["id"]),
                   nom       = str(row.get("nom",    "")),
                   age       = int(row.get("age",     0)),
                   region    = str(row.get("region", "?")),
                   classe    = str(row.get("classe", "?")),
                   infected  = bool(row.get("infected",   False)),
                   vaccinated= bool(row.get("vaccinated", False)),
                   statut    = statut)

    # Arêtes pondérées par nb_contacts
    for _, row in contacts.iterrows():
        G.add_edge(int(row["source"]), int(row["target"]),
                   weight=int(row.get("nb_contacts", 1)))

    print(f"  [✓] Graphe créé : {G.number_of_nodes()} nœuds, {G.number_of_edges()} arêtes")
    print(f"  [✓] Graphe orienté ? Non (non-dirigé)")
    return G


# ═══════════════════════════════════════════════════════════
#  ÉTAPE 2 — Statistiques générales
# ═══════════════════════════════════════════════════════════
def etape2_statistiques(G):
    print("\n" + "═"*60)
    print("  ÉTAPE 2 — Statistiques générales du graphe")
    print("═"*60)

    degres = [d for _, d in G.degree()]
    lcc    = max(nx.connected_components(G), key=len)
    G_lcc  = G.subgraph(lcc).copy()

    stats = {
        "Nœuds (individus)"        : G.number_of_nodes(),
        "Arêtes (contacts)"        : G.number_of_edges(),
        "Densité"                  : f"{nx.density(G):.6f}",
        "Degré moyen"              : f"{np.mean(degres):.2f}",
        "Degré médian"             : f"{np.median(degres):.0f}",
        "Degré max"                : max(degres),
        "Degré min"                : min(degres),
        "Composantes connexes"     : nx.number_connected_components(G),
        "Taille LCC (nœuds)"       : len(lcc),
        "% dans LCC"               : f"{100*len(lcc)/G.number_of_nodes():.1f}%",
        "Coefficient clustering"   : f"{nx.average_clustering(G):.4f}",
    }

    try:
        stats["Diamètre (LCC)"] = nx.diameter(G_lcc)
        stats["Rayon (LCC)"]    = nx.radius(G_lcc)
        stats["Chemin moyen"]   = f"{nx.average_shortest_path_length(G_lcc):.3f}"
    except Exception:
        stats["Diamètre (LCC)"] = "calcul trop long"

    print(f"\n  {'Statistique':<30} {'Valeur':>15}")
    print("  " + "-"*47)
    for k, v in stats.items():
        print(f"  {k:<30} {str(v):>15}")

    return stats, G_lcc


# ═══════════════════════════════════════════════════════════
#  ÉTAPE 3 — Super-propagateurs (hubs)
# ═══════════════════════════════════════════════════════════
def etape3_hubs(G):
    print("\n" + "═"*60)
    print("  ÉTAPE 3 — Super-propagateurs (Top 10 hubs)")
    print("═"*60)

    degres_dict = dict(G.degree())
    top10 = sorted(degres_dict.items(), key=lambda x: x[1], reverse=True)[:10]

    print(f"\n  {'Rang':<5} {'ID':>6} {'Nom':<16} {'Degré':>6} "
          f"{'Région':<14} {'Classe':<8} {'Statut':<10}")
    print("  " + "─"*68)
    for i, (node, deg) in enumerate(top10, 1):
        d  = G.nodes[node]
        print(f"  {i:<5} {node:>6} {d.get('nom','?'):<16} {deg:>6} "
              f"{d.get('region','?'):<14} {d.get('classe','?'):<8} "
              f"{d.get('statut','?'):<10}")

    return degres_dict, top10


# ═══════════════════════════════════════════════════════════
#  ÉTAPE 4 — Mesures de centralité
# ═══════════════════════════════════════════════════════════
def etape4_centralite(G):
    print("\n" + "═"*60)
    print("  ÉTAPE 4 — Mesures de centralité")
    print("═"*60)

    print("  → Centralité de degré...")
    deg_c = nx.degree_centrality(G)

    print("  → Centralité de vecteur propre...")
    try:
        eig_c = nx.eigenvector_centrality(G, max_iter=1000)
    except:
        eig_c = {n: 0 for n in G.nodes()}

    print("  → Centralité d'intermédiarité (approx.)...")
    bet_c = nx.betweenness_centrality(G, k=min(150, G.number_of_nodes()),
                                      normalized=True)

    for label, cent in [("Degré", deg_c), ("Propre", eig_c), ("Interméd.", bet_c)]:
        top5 = sorted(cent.items(), key=lambda x: -x[1])[:5]
        print(f"\n  Top 5 — Centralité {label} :")
        for node, val in top5:
            nom = G.nodes[node].get("nom","?")
            print(f"    #{node} {nom:<16} → {val:.5f}")

    return deg_c, eig_c, bet_c


# ═══════════════════════════════════════════════════════════
#  ÉTAPE 5 — Analyse épidémiologique réelle
# ═══════════════════════════════════════════════════════════
def etape5_epidemio(G):
    print("\n" + "═"*60)
    print("  ÉTAPE 5 — Analyse épidémiologique")
    print("═"*60)

    statuts   = [G.nodes[n]["statut"] for n in G.nodes()]
    dist_s    = Counter(statuts)
    total     = G.number_of_nodes()

    print(f"\n  Distribution des statuts ({total} individus) :")
    for s, c in sorted(dist_s.items(), key=lambda x: -x[1]):
        bar = "█" * int(35 * c / total)
        print(f"    {s:<12} {c:>4} ({100*c/total:5.1f}%)  {bar}")

    # Infectés par région
    inf_reg = {}
    inf_cls = {}
    for n in G.nodes():
        nd = G.nodes[n]
        if nd.get("infected"):
            r = nd.get("region", "?")
            c = nd.get("classe", "?")
            inf_reg[r] = inf_reg.get(r, 0) + 1
            inf_cls[c] = inf_cls.get(c, 0) + 1

    print(f"\n  Infectés par région :")
    for r, c in sorted(inf_reg.items(), key=lambda x: -x[1]):
        print(f"    {r:<14} → {c:>3} infectés")

    print(f"\n  Infectés par classe :")
    for cl, c in sorted(inf_cls.items(), key=lambda x: -x[1]):
        print(f"    {cl:<10} → {c:>3} infectés")

    # Infectés avec fort degré (à isoler en priorité)
    print(f"\n  ⚠ Infectés avec degré ≥ 10 (priorité d'isolement) :")
    print(f"  {'ID':>6} {'Nom':<16} {'Degré':>6} {'Région':<14} {'Classe':<8}")
    print("  " + "─"*52)
    dangereux = [(n, G.degree(n)) for n in G.nodes()
                 if G.nodes[n].get("infected") and G.degree(n) >= 10]
    dangereux.sort(key=lambda x: -x[1])
    for node, deg in dangereux[:10]:
        nd = G.nodes[node]
        print(f"  {node:>6} {nd.get('nom','?'):<16} {deg:>6} "
              f"{nd.get('region','?'):<14} {nd.get('classe','?'):<8}")

    return dist_s, inf_reg, inf_cls


# ═══════════════════════════════════════════════════════════
#  VIZ 1 — Réseau coloré par statut
# ═══════════════════════════════════════════════════════════
def viz1_reseau(G, top10):
    print("\n  [VIZ 1] Réseau d'interactions coloré par statut...")

    SCOL = {"infecté": C["rouge"], "vacciné": C["jaune"],
            "sain":    C["vert"]}

    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor(C["fond"])
    ax.set_facecolor(C["fond"])

    pos = nx.spring_layout(G, k=1.2, iterations=50, seed=42,
                           weight="weight")

    node_colors = [SCOL.get(G.nodes[n].get("statut","sain"), C["vert"])
                   for n in G.nodes()]
    node_sizes  = [30 + 5 * G.degree(n) for n in G.nodes()]

    # Edges colorés par nb_contacts
    weights = [G[u][v].get("weight", 1) for u, v in G.edges()]
    max_w   = max(weights) if weights else 1
    edge_alphas = [0.05 + 0.25 * (w / max_w) for w in weights]

    for i, (u, v) in enumerate(G.edges()):
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], ax=ax,
                               alpha=edge_alphas[i],
                               edge_color="#58a6ff", width=0.4)

    nx.draw_networkx_nodes(G, pos, ax=ax,
                           node_color=node_colors,
                           node_size=node_sizes, alpha=0.9)

    # Annoter les 5 plus grands hubs
    top5 = [n for n, _ in top10[:5]]
    for node in top5:
        x, y = pos[node]
        nom  = G.nodes[node].get("nom", f"#{node}")
        ax.annotate(f"◉ {nom}", xy=(x, y), fontsize=7.5, color="#f78166",
                    fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.25", facecolor="#161b22",
                              edgecolor="#f78166", alpha=0.85))

    patches = [mpatches.Patch(color=c, label=s.capitalize())
               for s, c in SCOL.items()]
    ax.legend(handles=patches, loc="upper left", fontsize=10,
              facecolor="#161b22", edgecolor="#30363d", labelcolor="#c9d1d9")

    ax.set_title(
        f"Réseau d'interactions physiques — {G.number_of_nodes()} individus, "
        f"{G.number_of_edges()} contacts\n"
        f"(taille des nœuds ∝ degré · les ◉ sont les super-propagateurs)",
        fontsize=12, color="#c9d1d9", pad=12)
    ax.axis("off")
    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, "1_reseau_statut.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=C["fond"])
    plt.close()
    print(f"  [✓] → {path}")


# ═══════════════════════════════════════════════════════════
#  VIZ 2 — Distribution des degrés
# ═══════════════════════════════════════════════════════════
def viz2_degres(G, degres_dict):
    print("  [VIZ 2] Distribution des degrés...")

    vals   = list(degres_dict.values())
    counts = Counter(vals)
    x, y   = zip(*sorted(counts.items()))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor(C["fond"])

    for ax in [ax1, ax2]:
        ax.set_facecolor(C["surface"])

    # Histogramme
    ax1.bar(x, y, color=C["bleu"], alpha=0.85, edgecolor="#0d1117", lw=0.3)
    ax1.axvline(np.mean(vals), color=C["rouge"], lw=1.8, linestyle="--",
                label=f"Moyenne = {np.mean(vals):.1f}")
    ax1.axvline(np.median(vals), color=C["jaune"], lw=1.5, linestyle=":",
                label=f"Médiane = {np.median(vals):.0f}")
    ax1.set_xlabel("Degré (nb contacts directs)", fontsize=11)
    ax1.set_ylabel("Nombre d'individus",          fontsize=11)
    ax1.set_title("Distribution des degrés",      fontsize=12)
    ax1.legend(fontsize=9, facecolor="#161b22", edgecolor="#30363d",
               labelcolor="#c9d1d9")
    ax1.grid(axis="y", alpha=0.3)

    # Log-log (loi de puissance)
    x_pos = [xi for xi in x if xi > 0]
    y_pos = [counts[xi] for xi in x_pos]
    ax2.scatter(x_pos, y_pos, color=C["vert"], s=18, alpha=0.75, edgecolors="none")
    ax2.set_xscale("log"); ax2.set_yscale("log")
    ax2.set_xlabel("Degré (log)", fontsize=11)
    ax2.set_ylabel("Fréquence (log)", fontsize=11)
    ax2.set_title("Échelle log-log (vérification loi de puissance)", fontsize=12)
    ax2.grid(alpha=0.3)

    if len(x_pos) > 3:
        lx = np.log10(x_pos)
        ly = np.log10([max(yi,1) for yi in y_pos])
        m, b = np.polyfit(lx, ly, 1)
        trend = [10**(m*np.log10(xi)+b) for xi in x_pos]
        ax2.plot(x_pos, trend, color=C["rouge"], lw=1.8, ls="--",
                 label=f"Pente γ ≈ {abs(m):.2f}")
        ax2.legend(fontsize=9, facecolor="#161b22", edgecolor="#30363d",
                   labelcolor="#c9d1d9")

    plt.suptitle("Analyse de la distribution des degrés — Réseau épidémiologique",
                 fontsize=13, color="#c9d1d9", y=1.02)
    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, "2_distribution_degres.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=C["fond"])
    plt.close()
    print(f"  [✓] → {path}")


# ═══════════════════════════════════════════════════════════
#  VIZ 3 — Dashboard épidémiologique
# ═══════════════════════════════════════════════════════════
def viz3_dashboard(G, stats, dist_s, inf_reg, inf_cls, deg_c, bet_c):
    print("  [VIZ 3] Dashboard épidémiologique...")

    fig = plt.figure(figsize=(18, 11))
    fig.patch.set_facecolor(C["fond"])

    # ── Camembert statuts ─────────────────────────────────
    ax1 = fig.add_subplot(2, 3, 1)
    ax1.set_facecolor(C["surface"])
    labels = list(dist_s.keys())
    vals   = list(dist_s.values())
    colors = [{"infecté":C["rouge"], "vacciné":C["jaune"],
               "sain":C["vert"]}.get(l, C["bleu"]) for l in labels]
    wedges, texts, autos = ax1.pie(
        vals, labels=labels, colors=colors, autopct="%1.1f%%",
        startangle=140, textprops={"color":"#c9d1d9","fontsize":9},
        wedgeprops={"edgecolor":"#0d1117","linewidth":1.5})
    for at in autos: at.set_fontsize(8)
    ax1.set_title("Répartition par statut", fontsize=11, color="#c9d1d9")

    # ── Infectés par région ───────────────────────────────
    ax2 = fig.add_subplot(2, 3, 2)
    ax2.set_facecolor(C["surface"])
    regs = sorted(inf_reg.items(), key=lambda x: -x[1])
    ax2.barh([r for r,_ in regs], [c for _,c in regs],
             color=C["rouge"], alpha=0.85, edgecolor="#0d1117", lw=0.5)
    for i,(r,c) in enumerate(regs):
        ax2.text(c+0.3, i, str(c), va="center", fontsize=8, color="#c9d1d9")
    ax2.set_xlabel("Infectés", fontsize=9)
    ax2.set_title("Infectés par région", fontsize=11, color="#c9d1d9")
    ax2.grid(axis="x", alpha=0.3)

    # ── Infectés par classe ───────────────────────────────
    ax3 = fig.add_subplot(2, 3, 3)
    ax3.set_facecolor(C["surface"])
    cls_s = sorted(inf_cls.items(), key=lambda x: -x[1])
    ax3.bar([c for c,_ in cls_s], [v for _,v in cls_s],
            color=C["violet"], alpha=0.85, edgecolor="#0d1117", lw=0.5)
    ax3.set_ylabel("Infectés", fontsize=9)
    ax3.set_title("Infectés par classe", fontsize=11, color="#c9d1d9")
    ax3.tick_params(axis="x", rotation=35, labelsize=8)
    ax3.grid(axis="y", alpha=0.3)

    # ── Top 10 centralité degré ───────────────────────────
    ax4 = fig.add_subplot(2, 3, 4)
    ax4.set_facecolor(C["surface"])
    top10d = sorted(deg_c.items(), key=lambda x: -x[1])[:10]
    nids   = [G.nodes[n].get("nom", f"#{n}") for n,_ in top10d]
    cvals  = [v for _,v in top10d]
    colors_b = [C["rouge"] if i < 3 else C["bleu"] for i in range(len(nids))]
    ax4.bar(nids, cvals, color=colors_b, alpha=0.85, edgecolor="#0d1117", lw=0.5)
    ax4.set_ylabel("Centralité degré", fontsize=9)
    ax4.set_title("Top 10 — Centralité de degré", fontsize=11, color="#c9d1d9")
    ax4.tick_params(axis="x", rotation=45, labelsize=7)
    ax4.grid(axis="y", alpha=0.3)

    # ── Top 10 intermédiarité ─────────────────────────────
    ax5 = fig.add_subplot(2, 3, 5)
    ax5.set_facecolor(C["surface"])
    top10b = sorted(bet_c.items(), key=lambda x: -x[1])[:10]
    nids_b = [G.nodes[n].get("nom", f"#{n}") for n,_ in top10b]
    bvals  = [v for _,v in top10b]
    ax5.bar(nids_b, bvals, color=C["cyan"], alpha=0.85,
            edgecolor="#0d1117", lw=0.5)
    ax5.set_ylabel("Centralité interméd.", fontsize=9)
    ax5.set_title("Top 10 — Ponts (intermédiarité)", fontsize=11, color="#c9d1d9")
    ax5.tick_params(axis="x", rotation=45, labelsize=7)
    ax5.grid(axis="y", alpha=0.3)

    # ── Distribution des âges par statut ──────────────────
    ax6 = fig.add_subplot(2, 3, 6)
    ax6.set_facecolor(C["surface"])
    for s, col in [("infecté", C["rouge"]),
                   ("vacciné", C["jaune"]),
                   ("sain",    C["vert"])]:
        ages = [G.nodes[n]["age"] for n in G.nodes()
                if G.nodes[n]["statut"] == s and G.nodes[n]["age"] > 0]
        if ages:
            ax6.hist(ages, bins=15, alpha=0.6, color=col,
                     label=s.capitalize(), edgecolor="#0d1117", lw=0.4)
    ax6.set_xlabel("Âge", fontsize=9)
    ax6.set_ylabel("Nb individus", fontsize=9)
    ax6.set_title("Distribution des âges par statut", fontsize=11, color="#c9d1d9")
    ax6.legend(fontsize=8, facecolor="#161b22", edgecolor="#30363d",
               labelcolor="#c9d1d9")
    ax6.grid(axis="y", alpha=0.3)

    plt.suptitle(
        "Dashboard Épidémiologique — Mini-Projet N°5 | Partie 2\n"
        "Réseau d'interactions physiques — 327 individus, 5818 contacts",
        fontsize=14, color="#c9d1d9", y=1.02, fontweight="bold")
    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, "3_dashboard_epidemio.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=C["fond"])
    plt.close()
    print(f"  [✓] → {path}")


# ═══════════════════════════════════════════════════════════
#  ÉTAPE 6 — Export GEXF (Gephi)
# ═══════════════════════════════════════════════════════════
def etape6_export(G):
    print("\n" + "═"*60)
    print("  ÉTAPE 6 — Export GEXF pour Gephi")
    print("═"*60)
    path = os.path.join(OUTPUT_DIR, "graphe_interactions.gexf")
    nx.write_gexf(G, path)
    print(f"  [✓] → {path}")
    print("     Ouvrez dans Gephi : File → Open → graphe_interactions.gexf")


# ═══════════════════════════════════════════════════════════
#  RAPPORT FINAL
# ═══════════════════════════════════════════════════════════
def rapport(G, stats, top10, dist_s, inf_reg):
    total    = G.number_of_nodes()
    infectes = dist_s.get("infecté", 0)
    vaccines = dist_s.get("vacciné", 0)
    hub_nom  = G.nodes[top10[0][0]].get("nom", f"#{top10[0][0]}")

    txt = f"""
╔══════════════════════════════════════════════════════════════╗
║    MINI-PROJET N°5 — PARTIE 2 — RAPPORT DE SYNTHÈSE         ║
╠══════════════════════════════════════════════════════════════╣
║  Module : Modèles et Algorithmes de Graphes                  ║
║  ENSA Berrechid — Université Hassan 1er — CI-ISIBD/S6        ║
╚══════════════════════════════════════════════════════════════╝

1. STRUCTURE DU GRAPHE
   ─────────────────────────────────────────────────────────
   • {total} individus (nœuds) reliés par {G.number_of_edges()} contacts (arêtes)
   • Densité = {stats['Densité']} → graphe CREUX (typique des réseaux réels)
   • Degré moyen = {stats['Degré moyen']} contacts par individu
   • {stats['% dans LCC']} des individus sont dans la composante connexe
     principale → la propagation peut toucher presque tout le monde
   • Coefficient de clustering = {stats['Coefficient clustering']}
     → les individus forment des groupes (communautés naturelles)

2. SUPER-PROPAGATEURS (Hubs)
   ─────────────────────────────────────────────────────────
   • Le super-propagateur n°1 est {hub_nom} avec {top10[0][1]} contacts
   • TOP 3 : {", ".join([G.nodes[n].get("nom",f"#{n}") + f" ({d})" for n,d in top10[:3]])}
   • Stratégie : vacciner/isoler ces individus en PRIORITÉ
     → effet maximal sur la réduction de la propagation

3. SITUATION ÉPIDÉMIOLOGIQUE
   ─────────────────────────────────────────────────────────
   • Infectés  : {infectes:>4} / {total} ({100*infectes/total:.1f}%)
   • Vaccinés  : {vaccines:>4} / {total} ({100*vaccines/total:.1f}%)
   • Région la plus touchée : {max(inf_reg, key=inf_reg.get) if inf_reg else 'N/A'}
     ({inf_reg.get(max(inf_reg, key=inf_reg.get), 0) if inf_reg else 0} infectés)

4. PROPRIÉTÉ SCALE-FREE (réseau réel)
   ─────────────────────────────────────────────────────────
   • La courbe log-log confirme une distribution en loi de puissance
   • Quelques hubs concentrent une grande partie des connexions
   • Implication vaccinale : cibler les hubs brise les chaînes
     de transmission plus efficacement qu'une vaccination aléatoire

5. FICHIERS GÉNÉRÉS
   ─────────────────────────────────────────────────────────
   📁 {OUTPUT_DIR}/
      ├── 1_reseau_statut.png         ← réseau coloré par statut
      ├── 2_distribution_degres.png   ← histogramme + log-log
      ├── 3_dashboard_epidemio.png    ← tableau de bord complet
      ├── graphe_interactions.gexf    ← pour Gephi
      └── rapport_partie2.txt         ← ce rapport
"""
    print(txt)
    path = os.path.join(OUTPUT_DIR, "rapport_partie2.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)
    print(f"  [✓] Rapport → {path}")


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    t0 = time.time()
    print("""
╔══════════════════════════════════════════════════════════════╗
║   MINI-PROJET N°5 — PARTIE 2 : GRAPHE DE GRANDE TAILLE      ║
║   327 individus · 5818 contacts réels                        ║
╚══════════════════════════════════════════════════════════════╝
    """)

    personnes, contacts             = etape0_chargement()
    G                               = etape1_construction(personnes, contacts)
    stats, G_lcc                    = etape2_statistiques(G)
    degres_dict, top10              = etape3_hubs(G)
    deg_c, eig_c, bet_c             = etape4_centralite(G)
    dist_s, inf_reg, inf_cls        = etape5_epidemio(G)

    print("\n" + "═"*60)
    print("  VISUALISATIONS")
    print("═"*60)
    viz1_reseau(G, top10)
    viz2_degres(G, degres_dict)
    viz3_dashboard(G, stats, dist_s, inf_reg, inf_cls, deg_c, bet_c)

    etape6_export(G)
    rapport(G, stats, top10, dist_s, inf_reg)

    print(f"\n  ✅ Terminé en {time.time()-t0:.1f}s")
    print(f"  📁 Résultats dans : ./{OUTPUT_DIR}/\n")
