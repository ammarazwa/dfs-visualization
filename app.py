import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random

# ========================== INISIALISASI SESSION ==========================
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'visited_order' not in st.session_state:
    st.session_state.visited_order = []
if 'edges_classified' not in st.session_state:
    st.session_state.edges_classified = []
if 'pos' not in st.session_state:
    st.session_state.pos = None
if 'start_node' not in st.session_state:
    st.session_state.start_node = 0
if 'custom_edges' not in st.session_state:
    st.session_state.custom_edges = [(0, 1), (0, 2), (1, 3), (2, 4), (4, 1), (4, 3)]
if 'last_start_node' not in st.session_state:
    st.session_state.last_start_node = None

# ========================== PARSE EDGE INPUT ==========================
def parse_edges(text):
    try:
        edges = eval(text.strip())
        if isinstance(edges, list) and all(isinstance(e, tuple) and len(e) == 2 for e in edges):
            return edges
    except:
        return None
    return None

# ========================== DFS FUNCTION ==========================
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
            neighbors = sorted(
                graph.neighbors(node),
                key=lambda n: st.session_state.pos[n][0],
                reverse=True 
            )
            for nbr in neighbors:
                if nbr not in visited:
                    stack.append((nbr, node))
                else:
                    if nbr in visited_order:
                        edges_classified.append((node, nbr, "back"))
                    else:
                        edges_classified.append((node, nbr, "cross"))
    return visited_order, edges_classified

# ========================== SIDEBAR ==========================
st.sidebar.title("💻 Algoritma DFS")
default_input = str(st.session_state.custom_edges)
user_input = st.sidebar.text_area("Masukkan Edge (format: [(0,1), (1,2)])", value=default_input, height=100)
parsed_edges = parse_edges(user_input)

if parsed_edges is not None:
    st.session_state.custom_edges = parsed_edges
else:
    st.sidebar.error("❌ Format input tidak sesuai. Gunakan format: [(0,1), (1,2)]")

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

# ========================== MAIN ==========================
st.title("🔍 Visualisasi Algoritma DFS (Depth-First Search)")
st.markdown("Masukkan graf dan pilih simpul awal untuk melihat proses DFS langkah demi langkah.")

# Update graf dari input
G = nx.Graph()  
G.add_edges_from(st.session_state.custom_edges)

# Update layout posisi node jika pos belum diset atau ada node baru
if st.session_state.pos is None or set(G.nodes()) != set(st.session_state.pos.keys()):
    st.session_state.pos = nx.spring_layout(G, seed=42)

# Dropdown simpul awal
def on_change_start():
    st.session_state.step = 0
    st.session_state.visited_order, st.session_state.edges_classified = dfs_step_by_step(G, st.session_state.start_node)
    st.session_state.last_start_node = st.session_state.start_node

st.selectbox(
    "Pilih simpul awal:",
    sorted(G.nodes()),
    index=0 if st.session_state.start_node not in G.nodes else list(G.nodes()).index(st.session_state.start_node),
    key="start_node",
    on_change=on_change_start
)

# Jalankan DFS jika belum ada hasil
if not st.session_state.visited_order:
    st.session_state.visited_order, st.session_state.edges_classified = dfs_step_by_step(G, st.session_state.start_node)
    st.session_state.last_start_node = st.session_state.start_node

# Tombol 
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button("🔄 Reshuffle Layout"):
        st.session_state.step = 0
        st.session_state.pos = nx.spring_layout(G, seed=random.randint(1, 999))
        st.session_state.visited_order, st.session_state.edges_classified = dfs_step_by_step(G, st.session_state.start_node)
        st.session_state.last_start_node = st.session_state.start_node
with col2:
    if st.button("🔁 Reset Traversal"):
        st.session_state.step = 0
        st.session_state.visited_order, st.session_state.edges_classified = dfs_step_by_step(G, st.session_state.start_node)
        st.session_state.last_start_node = st.session_state.start_node
with col3:
    if st.button("➡ Langkah Berikutnya"):
        if st.session_state.step < len(st.session_state.visited_order):
            st.session_state.step += 1

# Gambar graf
if st.session_state.pos is None:
    st.session_state.pos = nx.spring_layout(G, seed=42)

pos = st.session_state.pos
plt.figure(figsize=(8, 6))

# Gambar edge kemungkinan tujuan (next neighbors dari current node)
if st.session_state.step < len(st.session_state.visited_order):
    current_node = st.session_state.visited_order[st.session_state.step - 1] if st.session_state.step > 0 else st.session_state.start_node
    next_neighbors = [nbr for nbr in G.neighbors(current_node) if nbr not in st.session_state.visited_order[:st.session_state.step]]
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=[(current_node, nbr) for nbr in next_neighbors],
        edge_color='gray',
        width=2,
        style='dashed'
    )

# Tanpa arah panah
nx.draw_networkx_edges(G, pos, edge_color='lightgray')

# Gambar edge DFS yang sudah diklasifikasi
color_map = {"tree": "green", "back": "red", "cross": "orange"}
for u, v, typ in st.session_state.edges_classified:
    if u in st.session_state.visited_order[:st.session_state.step]:
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=color_map.get(typ, "gray"), width=2)

# Node
visited = st.session_state.visited_order[:st.session_state.step]
unvisited = [n for n in G.nodes if n not in visited]
nx.draw_networkx_nodes(G, pos, nodelist=visited, node_color='skyblue')
nx.draw_networkx_nodes(G, pos, nodelist=unvisited, node_color='lightgray')
nx.draw_networkx_labels(G, pos)

plt.title(f"DFS Langkah ke-{st.session_state.step} (Mulai dari simpul {st.session_state.start_node})")
st.pyplot(plt)

# Notifikasi jika selesai
if st.session_state.step >= len(st.session_state.visited_order):
    st.warning("✅ DFS selesai. Tidak ada simpul lain yang dapat dikunjungi dari sini.")

# Output teks urutan node yang dikunjungi
if visited:
    st.markdown("### ✅ Urutan Simpul yang Telah Dikunjungi")
    st.success(" → ".join(map(str, visited)))
else:
    st.info("Belum ada simpul yang dikunjungi. Klik 'Reset Traversal' atau 'Langkah Berikutnya'.")
