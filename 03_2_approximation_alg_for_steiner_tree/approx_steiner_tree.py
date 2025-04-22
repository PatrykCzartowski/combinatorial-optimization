import networkx as nx
import numpy as np
from itertools import combinations


def steiner_tree_2_approximation(G, terminals, verbose=False):
    
    if verbose:
        print("\n=== STEP 1: Creating complete graph on terminal vertices ===")
        print(f"Terminal vertices: {terminals}")
    
    G1 = nx.Graph() # construct complete graph G1
    for node in terminals:
        G1.add_node(node)
    
    shortest_paths = dict(nx.all_pairs_dijkstra_path(G, weight='weight'))
    shortest_paths_length = dict(nx.all_pairs_dijkstra_path_length(G, weight='weight'))
    
    for u, v in combinations(terminals, 2):
        G1.add_edge(u, v, weight=shortest_paths_length[u][v])
        if verbose:
            print(f"Added edge ({u}, {v}) with weight {shortest_paths_length[u][v]}")
            print(f"  This represents shortest path: {shortest_paths[u][v]}")
    
    if verbose:
        print("\n")
        print("\n=== STEP 2: Finding minimum spanning tree (MST) of the complete graph ===")
    
    MST = nx.minimum_spanning_tree(G1, weight='weight') # minimum spanning tree of G1
    
    if verbose:
        print("MST edges:")
        total_mst_weight = 0
        for u, v, data in MST.edges(data=True):
            weight = data['weight']
            total_mst_weight += weight
            print(f"Edge ({u}, {v}) with weight {weight}")
        print(f"Total MST weight: {total_mst_weight}")
        print("\n")
        print("\n=== STEP 3: Constructing subgraph by replacing MST edges with shortest paths ===")
    
    # replacing MST edges with shortest paths in G
    G2 = nx.Graph()
    
    for u, v in MST.edges():
        path = shortest_paths[u][v]
        if verbose:
            print(f"Replacing edge ({u}, {v}) with path: {path}")
        for i in range(len(path) - 1):
            if G2.has_edge(path[i], path[i+1]): # Edge already exists, keep the smallest weight
                existing_weight = G2[path[i]][path[i+1]]['weight']
                new_weight = G[path[i]][path[i+1]]['weight']
                G2[path[i]][path[i+1]]['weight'] = min(existing_weight, new_weight)
                if verbose and existing_weight != new_weight:
                    print(f"  Edge ({path[i]}, {path[i+1]}) already exists, keeping minimum weight: {min(existing_weight, new_weight)}")
            else:
                # Add new edge with weight from original graph
                weight = G[path[i]][path[i+1]]['weight']
                G2.add_edge(path[i], path[i+1], weight=G[path[i]][path[i+1]]['weight'])
                if verbose:
                    print(f"  Added edge ({path[i]}, {path[i+1]}) with weight {weight}")

    if verbose:
        print("\nG2 edges after replacing paths:")
        for u, v, data in sorted(G2.edges(data=True)):
            print(f"Edge ({u}, {v}) with weight {data['weight']}")
        print("\n")
        print("\n=== STEP 4: Finding minimum spanning tree of the expanded graph ===")
    
    MST_G2 = nx.minimum_spanning_tree(G2, weight='weight')
    
    if verbose:
        print("MST of G2 edges:")
        total_mst_g2_weight = 0
        for u, v, data in sorted(MST_G2.edges(data=True)):
            weight = data['weight']
            total_mst_g2_weight += weight
            print(f"Edge ({u}, {v}) with weight {weight}")
        print(f"Total MST of G2 weight: {total_mst_g2_weight}")
        print("\n")
        print("\n=== STEP 5: Pruning non-terminal leaves (if any) ===")
    
    MST_G_prime = MST_G2.copy()
    
    # Removing leaves that are not terminals
    pruned_count = 0
    pruned = True
    while pruned:
        pruned = False
        for node in list(MST_G_prime.nodes()):
            if (MST_G_prime.degree(node) == 1) and (node not in terminals):
                neighbor = list(MST_G_prime.neighbors(node))[0]
                weight = MST_G_prime[node][neighbor]['weight']
                if verbose:
                    print(f"Pruning leaf node {node} (connected to {neighbor} with weight {weight})")
                MST_G_prime.remove_node(node)
                pruned = True
                pruned_count += 1
    
    if verbose:
        if pruned_count > 0:
            print(f"\nPruned {pruned_count} non-terminal leaf nodes")
            print("\nFinal Steiner tree edges after pruning:")
            total_final_weight = 0
            for u, v, data in sorted(MST_G_prime.edges(data=True)):
                weight = data['weight']
                total_final_weight += weight
                print(f"Edge ({u}, {v}) with weight {weight}")
            print(f"Total weight of final Steiner tree: {total_final_weight}")
        else:
            print("No non-terminal leaf nodes to prune")
    
    return MST_G_prime

def create_graph_from_adjacency_list():
    G = nx.Graph()
    
    print("\n=== Graph Input ===")
    print("Enter the adjacency list as follows:")
    print("vertex: neighbor1 neighbor2 neighbor3")
    print("Press Enter after each line")
    print("Enter an empty line to finish graph input")
    print("Example: '1: 2 3 4' means vertex 1 is connected to vertices 2, 3, and 4")
    print("You'll be prompted for edge weights after entering all connections")
    
    adj_lists = {}
    
    while True:
        line = input("Enter adjacency list (or empty line to finish): ")
        if not line.strip():
            break
        try:
            # Parse the line "vertex: neighbor1 neighbor2 neighbor3"
            if ':' not in line:
                print("Invalid format. Expected 'vertex: neighbor1 neighbor2 neighbor3'")
                continue
            
            parts = line.split(':', 1)
            vertex = int(parts[0].strip())
            
            if len(parts) > 1 and parts[1].strip():
                neighbors = [int(n.strip()) for n in parts[1].strip().split()]
            else:
                neighbors = []
            
            adj_lists[vertex] = neighbors
            G.add_node(vertex)
        
        except ValueError:
            print("Invalid input. Vertex and neighbors must be integers.")
            
    for vertex in adj_lists:
        for neighbor in adj_lists[vertex]:
            if neighbor not in G:
                G.add_node(neighbor)
    
    print("\n=== Edge Weights ===")
    print("Enter weights for each edge:")
    
    for vertex in adj_lists:
        for neighbor in adj_lists[vertex]:
            if neighbor > vertex or neighbor not in adj_lists or vertex not in adj_lists[neighbor]:
                try:
                    weight = float(input(f"Weight for edge ({vertex}, {neighbor}): "))
                    G.add_edge(vertex, neighbor, weight=weight)
                except ValueError:
                    print("Invalid weight. Using default weight of 1.")
                    G.add_edge(vertex, neighbor, weight=1)
    
    return G

def get_terminal_vertices(G):
    while True:
        terminals_input = input("\nEnter terminal vertices separated by spaces: ")
        terminals = []
        
        try:
            terminals = [int(v) for v in terminals_input.strip().split()]
            valid_terminals = all(v in G.nodes() for v in terminals)
            
            if not valid_terminals:
                print("Some terminals are not in the graph. Please try again.")
                continue
                
            if len(terminals) < 2:
                print("You need at least 2 terminal vertices. Please try again.")
                continue
                
            break
        except ValueError:
            print("Invalid input. Please enter numeric vertex IDs.")
    
    return terminals

def print_graph_info(G):
    print("\n=== Graph Information ===")
    print(f"Number of vertices: {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")
    print("Vertices:", sorted(list(G.nodes())))
    
    print("\nEdges with weights:")
    for u, v, data in sorted(G.edges(data=True)):
        print(f"({u}, {v}): {data['weight']}")
        
def print_steiner_tree_info(steiner_tree, terminals):
    print("\n=== Steiner Tree Information ===")
    print(f"Number of vertices in Steiner tree: {steiner_tree.number_of_nodes()}")
    print(f"Number of edges in Steiner tree: {steiner_tree.number_of_edges()}")
    
    print("\nSteiner points (non-terminal vertices in the tree):")
    steiner_points = sorted([v for v in steiner_tree.nodes() if v not in terminals])
    print(steiner_points if steiner_points else "None")
    
    print("\nEdges in Steiner tree with weights:")
    for u, v, data in sorted(steiner_tree.edges(data=True)):
        print(f"({u}, {v}): {data['weight']}")
    
    total_weight = sum(data['weight'] for _, _, data in steiner_tree.edges(data=True))
    print(f"\nTotal weight of the Steiner tree: {total_weight}")
    
def use_example_graph():
    G = nx.Graph()
    edges = [
        (1, 2, 2), (1, 4, 1), (2, 3, 2), (2, 5, 3),
        (3, 6, 1), (4, 5, 2), (4, 7, 3), (5, 6, 3),
        (5, 8, 2), (6, 8, 1), (7, 8, 2)
    ]
    terminals = [1, 3, 7, 8]
    
    for i in range(1, 9):
        G.add_node(i)
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)
    
    return G, terminals

def visualize_graph(G, terminals=None, steiner_tree=None, filename=None):
    try:
        import matplotlib.pyplot as plt
        if steiner_tree is not None:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            plt.suptitle("Steiner Tree Approximation", fontsize=16)
            ax1.set_title("Original Graph")
            ax2.set_title("Steiner Tree Solution")
        else:
            fig, ax1 = plt.subplots(figsize=(10, 8))
            ax1.set_title("Graph")
        
        pos = nx.spring_layout(G, seed=42)
        
        edge_labels = {(u, v): f"{d['weight']}" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, ax=ax1)
        for (u, v), label in edge_labels.items():
            x = (pos[u][0] + pos[v][0]) / 2
            y = (pos[u][1] + pos[v][1]) / 2
            ax1.text(x, y, label, fontsize=10, rotation=0, ha='center', va='center', bbox=dict(facecolor='white', edgecolor='none', alpha=0.6))

        nx.draw_networkx_nodes(G, pos, node_size=500, alpha=0.8, ax=ax1)
        
        if terminals:
            nx.draw_networkx_nodes(G, pos, nodelist=terminals, node_size=500, node_color='red', alpha=0.8, ax=ax1)
        
        nx.draw_networkx_labels(G, pos, ax=ax1)
        ax1.axis('off')
        
        if steiner_tree is not None:
            steiner_edge_labels = {(u, v): f"{d['weight']}" for u, v, d in steiner_tree.edges(data=True)}
            nx.draw_networkx_edges(steiner_tree, pos, width=2.0, edge_color='blue', ax=ax2)
            for (u, v), label in steiner_edge_labels.items():
                x = (pos[u][0] + pos[v][0]) / 2
                y = (pos[u][1] + pos[v][1]) / 2
                ax2.text(x, y, label, fontsize=10, rotation=0, ha='center', va='center',bbox=dict(facecolor='white', edgecolor='none', alpha=0.6))
            
            steiner_nodes = list(steiner_tree.nodes())
            nx.draw_networkx_nodes(steiner_tree, pos, nodelist=steiner_nodes, node_size=500, node_color='lightblue', alpha=0.8, ax=ax2)

            if terminals:
                nx.draw_networkx_nodes(steiner_tree, pos, nodelist=terminals, 
                                      node_size=500, node_color='red', alpha=0.8, ax=ax2)
            
            steiner_points = [v for v in steiner_tree.nodes() if v not in terminals]
            if steiner_points:
                nx.draw_networkx_nodes(steiner_tree, pos, nodelist=steiner_points, node_size=500, node_color='green', alpha=0.8, ax=ax2)
            
            nx.draw_networkx_labels(steiner_tree, pos, ax=ax2)
            ax2.axis('off')
            
            ax2.legend([plt.Line2D([0], [0], color='w', marker='o', markerfacecolor='red', markersize=10),
                        plt.Line2D([0], [0], color='w', marker='o', markerfacecolor='green', markersize=10),
                        plt.Line2D([0], [0], color='blue', linewidth=2)],
                       ['Terminal Nodes', 'Steiner Points', 'Steiner Tree Edges'],
                       loc='upper right', bbox_to_anchor=(1, 0))
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename)
        else:
            plt.show()
        
        plt.close()
        return True
    except ImportError:
        print("Visualization requires matplotlib which is not installed.")
        return False    

def main_menu():
    G = None
    terminals = None
    steiner_tree = None
    
    while True:
        print("\n=== Steiner Tree Algorithm Menu ===")
        print("1. Input your own graph (adjacency list)")
        print("2. Use example graph")
        print("3. View current graph")
        print("4. Set terminal vertices")
        print("5. Calculate Steiner tree (with detailed steps)")
        print("6. Visualize graph and Steiner tree")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ")
        
        if choice == '1':
            G = create_graph_from_adjacency_list()
            if G.number_of_nodes() > 0:
                print(f"Graph created with {G.number_of_nodes()} vertices and {G.number_of_edges()} edges.")
                terminals = None  # Reset terminals when new graph is created
            else:
                print("Graph creation cancelled or empty graph created.")
                
        elif choice == '2':
            G, terminals = use_example_graph()
            print("Example graph loaded.")
            print(f"Graph has {G.number_of_nodes()} vertices and {G.number_of_edges()} edges.")
            print(f"Terminal vertices: {terminals}")
            
        elif choice == '3':
            if G is None:
                print("No graph exists. Please create or load a graph first.")
            else:
                print_graph_info(G)
                if terminals:
                    print(f"\nTerminal vertices: {terminals}")
                else:
                    print("\nNo terminal vertices set.")
                    
        elif choice == '4':
            if G is None:
                print("No graph exists. Please create or load a graph first.")
            else:
                terminals = get_terminal_vertices(G)
                print(f"Terminal vertices set: {terminals}")
                
        elif choice == '5':
            if G is None:
                print("No graph exists. Please create or load a graph first.")
            elif terminals is None or len(terminals) < 2:
                print("Terminal vertices not set or insufficient. Please set at least 2 terminal vertices.")
            else:
                try:
                    steiner_tree = steiner_tree_2_approximation(G, terminals, verbose=True)
                    print_steiner_tree_info(steiner_tree, terminals)
                except nx.NetworkXNoPath:
                    print("Error: No path exists between some terminal vertices. Graph may be disconnected.")
                except Exception as e:
                    print(f"An error occurred: {e}")
        elif choice == '6':
            if G is None:
                print("No graph exists. Please create or load a graph first.")
            elif terminals is None or len(terminals) < 2:
                print("Terminal vertices not set or insufficient. Please set at least 2 terminal vertices.")
            else:
                try:
                    if steiner_tree is None:
                        print("Calculating Steiner tree...")
                        steiner_tree = steiner_tree_2_approximation(G, terminals, verbose=False)
                        print("Steiner tree calculated.")
                        print_steiner_tree_info(steiner_tree, terminals)
                        
                    print("Visualizing graph and Steiner tree...")
                    success = visualize_graph(G, terminals, steiner_tree)
                    if not success:
                        print("Could not visualize graph. Make sure matplotlib is installed.")
                except nx.NetworkXNoPath:
                    print("Error: No path exists between some terminal vertices. Graph may be disconnected.")
                except Exception as e:
                    print(f"An error occurred: {e}")
        elif choice == '0':
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")
            
if __name__ == "__main__":
    main_menu()