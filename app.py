import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random

# Inisialisasi session state
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'visited_order' not in st.session_state:
    st.session_state.visited_order = []
if 'edges_classified' not in st.session_state:
    st.session_state.edges_classified = []
if 'pos' not in st.session_state:
    st.session_state.pos = None
if 'start_node' not in st.session_state:
    st.session_state.start_node = 0  # default

# Buat graf directed
G = nx.DiGraph()
edges = [(0, 1), (0, 2), (1, 3), (2, 4), (4, 1), (4, 3)]
G.add_edges_from(edges)

# Fungsi DFS manual
def dfs_step_by_step(graph, start):
    visited = set()
    stack = [(start, None)]
    visited_order = []
    edges_classified = []

    while stack:
        node, parent = stack.pop()
        if node not in visited:
            visited.add(node)
            visited_order.append(node)
            if parent is not None:
                edges_classified.append((parent, node, "tree"))
            neighbors = list(graph.neighbors(node))[::-1]
            for nbr in neighbors:
                if nbr not in visited:
                    stack.append((nbr, node))
                else:
                    if nbr in visited_order:
                        edges_classified.append((node, nbr, "back"))
                    else:
                        edges_classified.append((node, nbr, "cross"))
    return visited_order, edges_classified

# Callback saat simpul awal diganti
def update_dfs():
    st.session_state.step = 0
    st.session_state.visited_order, st.session_state.edges_classified = dfs_step_by_step(G, st.session_state.start_node)

# ===========================
#           SIDEBAR
# ===========================
st.sidebar.title("💻 Algoritma DFS")
st.sidebar.code("""
def dfs(graph, start):
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            for neighbor in reversed(graph[node]):
                if neighbor not in visited:
                    stack.append(neighbor)
""")

# ===========================
#        MAIN SECTION
# ===========================
st.title("🔍 Visualisasi Algoritma DFS (Depth-First Search)")

st.markdown("Pilih simpul awal dan tekan tombol untuk memulai atau melangkah dalam proses traversalnya.")

# Pilihan simpul awal
st.selectbox(
    "Pilih simpul awal:",
    sorted(G.nodes()),
    index=0,
    key="start_node",
    on_change=update_dfs
)
start_node = st.session_state.start_node

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button("🔄 Reshuffle Graph"):
        st.session_state.step = 0
        st.session_state.pos = nx.spring_layout(G, seed=random.randint(0, 1000))
        st.session_state.visited_order, st.session_state.edges_classified = dfs_step_by_step(G, start_node)
with col2:
    if st.button("🔁 Reset Traversal"):
        st.session_state.step = 0
        st.session_state.visited_order, st.session_state.edges_classified = dfs_step_by_step(G, start_node)
with col3:
    if st.button("➡️ Langkah Berikutnya"):
        if st.session_state.step < len(st.session_state.visited_order):
            st.session_state.step += 1

# Gambar graf
if st.session_state.pos is None:
    st.session_state.pos = nx.spring_layout(G, seed=42)

pos = st.session_state.pos
plt.figure(figsize=(8, 6))

# Gambar edge default
nx.draw_networkx_edges(G, pos, edge_color='lightgray')

# Gambar edge yang sudah diklasifikasi
color_map = {"tree": "green", "back": "red", "cross": "orange"}
for u, v, typ in st.session_state.edges_classified:
    if u in st.session_state.visited_order[:st.session_state.step]:
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=color_map.get(typ, "gray"), width=2)

# Gambar node
visited = st.session_state.visited_order[:st.session_state.step]
unvisited = [n for n in G.nodes if n not in visited]
nx.draw_networkx_nodes(G, pos, nodelist=visited, node_color='skyblue')
nx.draw_networkx_nodes(G, pos, nodelist=unvisited, node_color='lightgray')
nx.draw_networkx_labels(G, pos)

plt.title(f"DFS Langkah ke-{st.session_state.step} (Mulai dari node {start_node})")
st.pyplot(plt)

# Tampilkan hasil DFS sejauh ini
if visited:
    st.markdown("### ✅ Urutan Node yang Sudah Dikunjungi")
    st.success(" → ".join(map(str, visited)))
else:
    st.info("Belum ada node yang dikunjungi. Klik 'Reset Traversal' atau 'Langkah Berikutnya'.")
