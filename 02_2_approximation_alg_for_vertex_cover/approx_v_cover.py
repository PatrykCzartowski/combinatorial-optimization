import networkx as nx
import matplotlib.pyplot as plt
import random
import sys

def approx_vertex_cover(graph):
    G = graph.copy()
    vertex_cover = set()
    while G.edges():
        u, v = list(G.edges())[0]
        vertex_cover.add(u)
        vertex_cover.add(v)
        edges_to_remove = list(G.edges(u)) + list(G.edges(v))
        G.remove_edges_from(edges_to_remove)
    return vertex_cover

def generate_random_graph(n_nodes, edge_probability=0.3):
    return nx.gnp_random_graph(n_nodes, edge_probability)

def visualize_graph_with_vertex_cover(graph, vertex_cover):
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(graph, seed=42)
    node_colors = ['red' if node in vertex_cover else 'lightblue' for node in graph.nodes()]

    nx.draw(graph, pos, with_labels=True, node_color=node_colors, 
            node_size=500, font_weight='bold', font_color='black',
            edge_color='gray', width=1.5, alpha=0.8)
    plt.title(f"Vertex cover - number of vertices in cover: {len(vertex_cover)}", fontsize=16)

    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=15, label='In cover'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', markersize=15, label='Out of cover')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.show()

def create_graph_from_adjacency_list():
    G = nx.Graph()
    
    print("\nEnter adjacency list in:")
    print("vertex: neighbor1 neighbor2 neighbor3 ...")
    print("To end insert, enter a blank line.\n")
    
    while True:
        line = input("-> ").strip()
        if not line:
            break
            
        try:
            parts = line.split(":")
            if len(parts) != 2:
                print("Invalid format. Try again.")
                continue
                
            node = parts[0].strip()
            neighbors = parts[1].strip().split()
            
            for neighbor in neighbors:
                G.add_edge(node, neighbor)
                
        except Exception as e:
            print(f"Error: {e}. Try again.")
    
    return G

def display_menu():
    print("\n" + "="*50)
    print("             VERTEX COVER PROBLEM")
    print("="*50)
    print("1. Create your own graph (adjacency list)")
    print("2. Generate random graph")
    print("3. Calculate vertex cover")
    print("4. Visualize graph with vertex cover")
    print("5. Display info about graph")
    print("0. Exit")
    print("="*50)

def main():
    G = nx.Graph()
    vertex_cover = set()
    
    while True:
        display_menu()
        choice = input("\nChoose option (0-5): ").strip()
        
        if choice == "1":
            G = create_graph_from_adjacency_list()
            print(f"Generated graph with {G.number_of_nodes()} vertices and {G.number_of_edges()} edges.")
            
        elif choice == "2":
            try:
                n_nodes = int(input("Enter vertices count: "))
                edge_prob = float(input("Enter edge probability (0.0-1.0): "))
                
                if n_nodes <= 0 or edge_prob < 0 or edge_prob > 1:
                    print("Invalid values. Use positive numbers for vertices count and a range of 0-1 for the probability.")
                else:
                    G = generate_random_graph(n_nodes, edge_prob)
                    print(f"Generated random graph with {G.number_of_nodes()} vertices and {G.number_of_edges()} edges.")
            except ValueError:
                print("Error: Enter correct values.")
                
        elif choice == "3":
            if G.number_of_edges() == 0:
                print("Graph is empty or without any edges. Enter or generate graph first.")
            else:
                vertex_cover = approx_vertex_cover(G)
                print(f"Found vertex cover: {vertex_cover}")
                print(f"Coverage size: {len(vertex_cover)}")
                
                is_valid_cover = all(u in vertex_cover or v in vertex_cover for u, v in G.edges())
                print(f"Is found cover valid: {is_valid_cover}")
                
        elif choice == "4":
            if G.number_of_nodes() == 0:
                print("Graph is empty or without any edges. Enter or generate graph first.")
            else:
                if not vertex_cover:
                    print("Vertex cover was not calculated yet. Calculating now...")
                    vertex_cover = approx_vertex_cover(G)
                    
                print("Generating visualization...")
                visualize_graph_with_vertex_cover(G, vertex_cover)
                
        elif choice == "5":
            if G.number_of_nodes() == 0:
                print("Graph is empty. Enter or generate graph first.")
            else:
                print(f"\nGraph info:")
                print(f"- Number of vertices: {G.number_of_nodes()}")
                print(f"- Number of edges: {G.number_of_edges()}")
                print(f"- Vertices: {list(G.nodes())}")
                print(f"- Edges: {list(G.edges())}")
                
                if vertex_cover:
                    print(f"- Vertex cover: {vertex_cover}")
                    print(f"- Cover size: {len(vertex_cover)}")
                else:
                    print("- Vertex cover was not calculated yet.")
                        
        elif choice == "0":
            sys.exit(0)
            
        else:
            print("Incorrect option. Choose number between 0 and 5.")
            
        input("\nPress Enter, to continue...")

if __name__ == "__main__":
    main()