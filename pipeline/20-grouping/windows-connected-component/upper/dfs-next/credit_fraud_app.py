import streamlit as st
import pandas as pd
from neo4j import GraphDatabase
from datetime import datetime
from collections import Counter
from streamlit_agraph import agraph, Node, Edge, Config

# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"
NEO4J_DATABASE = "fraudwcctemporal"

BIPARTITE = (
    "EMAIL_ROOT|TELEPHONE|ADRESSE_IP|DEVICE|CARTE_BANCAIRE|"
    "COMPTE|ETAT_CIVIL|ADRESSE_EMPRUNTEUR|FOYER_SICLID"
)

IDENT_COLOR = "#00D9FF"
FRAUD_COLOR = "#FF2222"
NORMAL_COLOR = "#44BB44"
SELECTED_COLOR = "#FFFF00"

st.set_page_config(page_title="Credit — Point-in-time communities", layout="wide")

if "driver" not in st.session_state:
    st.session_state.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def run(query, **params):
    with st.session_state.driver.session(database=NEO4J_DATABASE) as s:
        return s.run(query, **params).data()


# ---------------------------------------------------------------------------
# Header + connection check
# ---------------------------------------------------------------------------
st.title("🏦 Credit communities — point-in-time view")
try:
    run("RETURN 1 AS ok")
    st.sidebar.success("✅ Connected to Neo4j")
except Exception as e:
    st.sidebar.error(f"❌ {e}")
    st.stop()

# ---------------------------------------------------------------------------
# Select a dossier (by default: dossiers belonging to a community)
# ---------------------------------------------------------------------------
st.sidebar.header("Selection")

candidates = run(
    """
    MATCH (d:Dossier)
    WHERE coalesce(d.IND_COM_TAILLE, 0) >= 2 AND d.IND_COM_TAILLE <= 50
    WITH d.IND_COM_TAILLE AS taille, collect(d.NODOS)[0] AS nodos
    RETURN nodos, taille
    ORDER BY taille ASC
    """
)
options = [c["nodos"] for c in candidates]
sizes = {c["nodos"]: c["taille"] for c in candidates}

# By default: community whose size is closest to 20 (avoids loading the huge communities)
default_index = 0
if options:
    default_index = min(range(len(options)), key=lambda k: abs(sizes[options[k]] - 20))

selected = st.sidebar.selectbox(
    "Dossier (sorted by increasing size)",
    options,
    index=default_index,
    format_func=lambda n: f"{n}  (community ~{sizes.get(n, '?')})" if options else n,
) if options else None

manual = st.sidebar.text_input("… or enter a NODOS", "")
if manual.strip():
    selected = manual.strip()

view_mode = st.sidebar.radio(
    "Temporal view of the community",
    ["Before dossier", "At dossier", "Latest state"],
    index=1,
    help=(
        "Before dossier: community as it existed just BEFORE this application was added.\n"
        "At dossier: community at the application date (application included).\n"
        "Latest state: community as it exists today (after all later merges)."
    ),
)

# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------
Q_COMMUNITY = """
MATCH (d:Dossier {NODOS: $nodos})(()-[:DFS_NEXT]->(m))*(last)<-[:LAST_DFS_NODE_IN_COMP]-(d)
WITH d, [d] + m AS members
UNWIND members AS ev
OPTIONAL MATCH (ev)-[:%s]->(x)
WITH ev, d, collect(DISTINCT {eid: elementId(x), type: labels(x)[0]}) AS idents
RETURN ev.NODOS AS nodos,
       toString(ev.DATE_COMMANDE) AS date,
       ev.TOP_FRAUDE AS fraude,
       ev.pattern AS pattern,
       (ev.NODOS = d.NODOS) AS is_selected,
       idents
ORDER BY date
""" % BIPARTITE

# Sizes of the 3 views (COUNT only, very fast) to visualize the growth
Q_SIZES = """
MATCH (d:Dossier {NODOS: $nodos})
CALL (d) { MATCH (d)-[:DFS_NEXT]->*(x) RETURN count(x) AS au_dossier }
CALL (d) {
  MATCH (d)-[:COMPONENT_PARENT]->*(head:Dossier WHERE NOT EXISTS {(head)-[:COMPONENT_PARENT]->()})
  MATCH (head)-[:DFS_NEXT]->*(y)
  RETURN count(y) AS dernier
}
RETURN (au_dossier - 1) AS avant, au_dossier AS au_dossier, dernier AS dernier
"""

# "Latest state" community: walk up COMPONENT_PARENT to the current head,
# then traverse its whole DFS_NEXT chain (state as of today, after later merges).
Q_LATEST = """
MATCH (d:Dossier {NODOS: $nodos})
MATCH (d)-[:COMPONENT_PARENT]->*(head:Dossier
      WHERE NOT EXISTS {(head)-[:COMPONENT_PARENT]->()})
MATCH (head)(()-[:DFS_NEXT]->(m))*(last)<-[:LAST_DFS_NODE_IN_COMP]-(head)
WITH d, [head] + m AS members
UNWIND members AS ev
OPTIONAL MATCH (ev)-[:%s]->(x)
WITH ev, d, collect(DISTINCT {eid: elementId(x), type: labels(x)[0]}) AS idents
RETURN ev.NODOS AS nodos,
       toString(ev.DATE_COMMANDE) AS date,
       ev.TOP_FRAUDE AS fraude,
       ev.pattern AS pattern,
       (ev.NODOS = d.NODOS) AS is_selected,
       idents
ORDER BY date
""" % BIPARTITE

Q_PROPS = """
MATCH (d:Dossier {NODOS: $nodos})
RETURN d.NODOS AS NODOS, toString(d.DATE_COMMANDE) AS DATE_COMMANDE,
       d.TOP_FRAUDE AS TOP_FRAUDE, d.pattern AS pattern,
       d.FPD AS FPD, d.SPD AS SPD, d.TPD AS TPD,
       d.FEU_INITIAL AS FEU_INITIAL, d.FEU_FINAL AS FEU_FINAL,
       d.VILLE_EMPRUNTEUR AS VILLE_EMPRUNTEUR,
       coalesce(d.IND_COM_TAILLE, 0) AS IND_COM_TAILLE,
       coalesce(d.IND_COM_NB_DDE_7J, 0) AS IND_COM_NB_DDE_7J,
       coalesce(d.IND_COM_NB_DDE_30J, 0) AS IND_COM_NB_DDE_30J,
       coalesce(d.IND_COM_NB_DDE_7M, 0) AS IND_COM_NB_DDE_7M,
       coalesce(d.IND_COM_NB_DDE_1AN, 0) AS IND_COM_NB_DDE_1AN,
       coalesce(d.IND_COM_AGE, 0) AS IND_COM_AGE,
       coalesce(d.IND_COM_RECENCE, -1) AS IND_COM_RECENCE,
       coalesce(d.IND_COM_STRONG_FANOUT, 0) AS IND_COM_STRONG_FANOUT,
       coalesce(d.IND_COM_NB_STRONG_SHARED, 0) AS IND_COM_NB_STRONG_SHARED,
       coalesce(d.IND_COM_NB_FRAUDE_CONF_1AN, 0) AS IND_COM_NB_FRAUDE_CONF_1AN,
       coalesce(d.IND_COM_NB_FRAUDE_CONF_2AN, 0) AS IND_COM_NB_FRAUDE_CONF_2AN,
       coalesce(d.IND_COM_NB_FPD_1AN, 0) AS IND_COM_NB_FPD_1AN,
       coalesce(d.IND_COM_NB_SPD_1AN, 0) AS IND_COM_NB_SPD_1AN,
       coalesce(d.IND_COM_NB_TPD_1AN, 0) AS IND_COM_NB_TPD_1AN
"""

# Generic node inspection (used by the "Node properties" screen).
# Works for a Dossier (keyed by NODOS) or any identifier node (keyed by elementId).
Q_NODE_DOSSIER = """
MATCH (d:Dossier {NODOS: $nodos})
RETURN elementId(d) AS eid, labels(d) AS labels, properties(d) AS props
"""

Q_NODE_BY_EID = """
MATCH (n) WHERE elementId(n) = $eid
RETURN elementId(n) AS eid, labels(n) AS labels, properties(n) AS props
"""

Q_NODE_NEIGHBORS = """
MATCH (n) WHERE elementId(n) = $eid
MATCH (n)-[r]-(m)
RETURN type(r) AS rel,
       CASE WHEN startNode(r) = n THEN '→ out' ELSE '← in' END AS dir,
       labels(m)[0] AS neighbor_label,
       coalesce(m.NODOS, toString(m.value), elementId(m)) AS neighbor_id
ORDER BY rel, dir
LIMIT 200
"""


def node_details(node_id):
    """Resolve a graph node id (a Dossier NODOS or an identifier elementId) to its record."""
    res = run(Q_NODE_DOSSIER, nodos=node_id)
    if res:
        return res[0]
    res = run(Q_NODE_BY_EID, eid=node_id)
    return res[0] if res else None


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
if not selected:
    st.info("Select a dossier in the sidebar.")
    st.stop()

# Reset the inspected node whenever the sidebar selection changes
if st.session_state.get("_last_selected") != selected:
    st.session_state["inspected_node"] = selected
    st.session_state["_last_selected"] = selected

# Curated dossier properties (also feeds the evolution vector below)
props = run(Q_PROPS, nodos=selected)
p = props[0] if props else None

# ---- Sidebar: dossier properties, below the whole selection block ----
with st.sidebar:
    st.divider()
    st.header("📋 Dossier properties")
    if p:
        is_fraud = bool(p["TOP_FRAUDE"])
        st.markdown(f"**{p['NODOS']}** — {'🚨 FRAUD' if is_fraud else '✅ legitimate'}")
        st.write({
            "DATE_COMMANDE": p["DATE_COMMANDE"],
            "pattern": p["pattern"],
            "VILLE": p["VILLE_EMPRUNTEUR"],
            "FEU_INITIAL": p["FEU_INITIAL"],
            "FEU_FINAL": p["FEU_FINAL"],
            "FPD/SPD/TPD": f"{p['FPD']}/{p['SPD']}/{p['TPD']}",
        })
    else:
        st.info("Dossier not found.")

TITLES = {
    "Before dossier": "👁️ Community just BEFORE the application was added",
    "At dossier": "👁️ Community AT THE DATE of the application (application included)",
    "Latest state": "👁️ Community TODAY (latest state, after later merges)",
}

col_graph, col_info = st.columns([2, 1])

with col_graph:
    st.subheader(TITLES[view_mode])

    # Growth of the community over time
    sz = run(Q_SIZES, nodos=selected)
    if sz:
        s = sz[0]
        m1, m2, m3 = st.columns(3)
        m1.metric("Before dossier", s["avant"])
        m2.metric("At dossier", s["au_dossier"], delta=int(s["au_dossier"] - s["avant"]))
        m3.metric("Latest state", s["dernier"], delta=int(s["dernier"] - s["au_dossier"]))

    query = Q_LATEST if view_mode == "Latest state" else Q_COMMUNITY
    community = run(query, nodos=selected)
    skip_selected = (view_mode == "Before dossier")

    MAX_RENDER = 120  # beyond this, rendering the (physics) graph freezes the browser -> show a table

    if not community:
        st.warning("Dossier not found or without a community.")
    elif len(community) > MAX_RENDER:
        st.warning(
            f"Community of {len(community)} dossiers — too large for the interactive graph "
            f"(threshold {MAX_RENDER}). Showing as a table instead. "
            f"Pick a smaller community from the list (sorted by increasing size)."
        )
        st.dataframe(
            [{"NODOS": r["nodos"], "date": r["date"], "fraude": r["fraude"], "pattern": r["pattern"]}
             for r in community],
            width="stretch",
        )
    else:
        nodes, edges, seen = [], [], set()
        fraud_count = 0
        patterns = Counter()

        for row in community:
            is_sel = row["is_selected"]
            if is_sel and skip_selected:
                continue  # "Before dossier" mode: hide the application to see the prior state

            nodos = row["nodos"]
            fraude = bool(row["fraude"])
            patterns[row["pattern"]] += 1
            if fraude and not is_sel:
                fraud_count += 1

            if nodos not in seen:
                if is_sel:
                    color = SELECTED_COLOR
                else:
                    color = FRAUD_COLOR if fraude else NORMAL_COLOR
                nodes.append(Node(
                    id=nodos,
                    label=nodos.replace("DOS_", ""),
                    size=28 if is_sel else 18,
                    color=color,
                    borderWidth=3 if is_sel else 1,
                    title=f"{nodos}\n{row['date']}\npattern={row['pattern']}\nfraude={fraude}",
                ))
                seen.add(nodos)

            for ident in row["idents"]:
                if not ident or not ident.get("eid"):
                    continue
                eid = ident["eid"]
                if eid not in seen:
                    nodes.append(Node(
                        id=eid,
                        label=ident["type"][:10],
                        size=12,
                        color=IDENT_COLOR,
                        shape="box",
                        title=ident["type"],
                    ))
                    seen.add(eid)
                edges.append(Edge(source=nodos, target=eid))

        n_dossiers = sum(1 for n in nodes if n.shape != "box")
        n_idents = sum(1 for n in nodes if n.shape == "box")
        st.caption(f"{n_dossiers} dossiers · {n_idents} shared identifiers")
        st.markdown(
            f"<span style='color:{FRAUD_COLOR}'>⬤</span> fraud &nbsp; "
            f"<span style='color:{NORMAL_COLOR}'>⬤</span> legitimate &nbsp; "
            f"<span style='color:{SELECTED_COLOR}'>⬤</span> selected application &nbsp; "
            f"<span style='color:{IDENT_COLOR}'>▪</span> shared identifier",
            unsafe_allow_html=True,
        )
        if fraud_count:
            st.error(f"🚨 {fraud_count} dossier(s) labeled fraud in the community (excluding the current application)")

        st.caption("💡 Click a node to inspect it in the “Node properties” panel (right).")
        clicked = agraph(nodes=nodes, edges=edges,
                         config=Config(width=850, height=600, directed=True, physics=True))
        if clicked:
            st.session_state["inspected_node"] = clicked

with col_info:
    if p:
        st.subheader("📈 Community features (point-in-time)")

        # DISJOINT application buckets (leak-safe volume), differencing cumulative windows:
        #   0–7 d / 7–30 d / 30 d–7 mo / 7 mo–1 y
        b_7j  = p["IND_COM_NB_DDE_7J"]
        b_30j = max(0, p["IND_COM_NB_DDE_30J"] - p["IND_COM_NB_DDE_7J"])
        b_7m  = max(0, p["IND_COM_NB_DDE_7M"]  - p["IND_COM_NB_DDE_30J"])
        b_1an = max(0, p["IND_COM_NB_DDE_1AN"] - p["IND_COM_NB_DDE_7M"])

        # Acceleration: recent daily rate vs monthly rate (> 1 = the community is speeding up)
        accel = (p["IND_COM_NB_DDE_7J"] / 7.0) / (p["IND_COM_NB_DDE_30J"] / 30.0 + 1e-6)

        c1, c2, c3 = st.columns(3)
        c1.metric("Comm. size", p["IND_COM_TAILLE"])
        c2.metric("Strong-id fan-out", p["IND_COM_STRONG_FANOUT"])
        c3.metric("Acceleration 7/30d", f"{accel:.1f}×")

        # X axis from most recent to oldest, disjoint buckets
        ordre = ["0–7 d", "7–30 d", "30 d–7 mo", "7 mo–1 y"]
        chart_df = pd.DataFrame(
            {"Applications": [b_7j, b_30j, b_7m, b_1an]},
            index=pd.CategoricalIndex(ordre, categories=ordre, ordered=True, name="bucket"),
        )
        st.bar_chart(chart_df)
        st.caption(
            "Application growth (disjoint buckets), strictly BEFORE the dossier date → leak-free."
        )

        # Confirmation-aware risk signals: labels counted only once known at T
        st.markdown("**Confirmed risk signals** *(fraud after ~6 mo; FPD/SPD/TPD after 30/60/90 d)*")
        r1, r2, r3 = st.columns(3)
        r1.metric("Confirmed fraud ≤ 1 y", p["IND_COM_NB_FRAUDE_CONF_1AN"])
        r2.metric("Confirmed fraud ≤ 2 y", p["IND_COM_NB_FRAUDE_CONF_2AN"])
        r3.metric("FPD ≤ 1 y", p["IND_COM_NB_FPD_1AN"])
        r4, r5, _ = st.columns(3)
        r4.metric("SPD ≤ 1 y", p["IND_COM_NB_SPD_1AN"])
        r5.metric("TPD ≤ 1 y", p["IND_COM_NB_TPD_1AN"])

    # ---- Node properties (moved here, below the evolution vector) ----
    st.divider()
    st.subheader("🔎 Node properties")
    node_id = st.session_state.get("inspected_node", selected)
    st.caption(
        "Properties of the node selected in the graph (click a node in the community). "
        "Defaults to the selected dossier."
    )

    detail = node_details(node_id)
    if not detail:
        st.warning(f"Node `{node_id}` not found (it may have changed since the last graph render).")
    else:
        labels = detail["labels"] or ["Node"]
        node_props = detail["props"] or {}
        label = labels[0]

        st.markdown(f"**{'🚨 ' if node_props.get('TOP_FRAUDE') else ''}{label}** · `{node_id}`")
        if len(labels) > 1:
            st.caption("Labels: " + ", ".join(labels))

        st.markdown("**Properties**")
        prop_rows = [{"property": k, "value": str(node_props[k])} for k in sorted(node_props)]
        if prop_rows:
            st.dataframe(prop_rows, width="stretch", hide_index=True)
        else:
            st.info("This node has no properties.")

        st.markdown("**Relationships**")
        neigh = run(Q_NODE_NEIGHBORS, eid=detail["eid"])
        if neigh:
            st.dataframe(
                [{"direction": n["dir"], "relationship": n["rel"],
                  "neighbor": f"{n['neighbor_label']} · {n['neighbor_id']}"} for n in neigh],
                width="stretch", hide_index=True,
            )
            st.caption(f"{len(neigh)} relationship(s) shown (max 200).")
        else:
            st.info("No relationships for this node.")

st.caption("🕰️ Community rebuilt via DFS_NEXT / LAST_DFS_NODE_IN_COMP (state as of the dossier date).")
