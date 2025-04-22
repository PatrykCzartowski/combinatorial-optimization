import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import itertools
import math
import sys

def check_triangle_inequality(G):

    print("\nChecking triangle inequality condition...")
    
    nodes = list(G.nodes())
    all_shortest_paths = dict(nx.all_pairs_dijkstra_path_length(G, weight='weight'))
    
    for u, v, w in itertools.permutations(nodes, 3):
        direct_dist = all_shortest_paths[u][w]
        indirect_dist = all_shortest_paths[u][v] + all_shortest_paths[v][w]
        
        if direct_dist > indirect_dist + 1e-9:
            print(f"Triangle inequality violated for vertices {u}, {v}, {w}")
            print(f"Direct distance {u}→{w}: {direct_dist}")
            print(f"Indirect distance {u}→{v}→{w}: {indirect_dist}")
            return False
            
    print("Triangle inequality is satisfied for all vertex triples.")
    return True

def calculate_mst(G):

    print("\n=== STEP 1: Computing Minimum Spanning Tree ===")
    mst = nx.minimum_spanning_tree(G, weight='weight')
    
    print(f"MST contains {mst.number_of_edges()} edges with total weight {sum(d['weight'] for _, _, d in mst.edges(data=True))}")
    print("MST edges:")
    for u, v, data in sorted(mst.edges(data=True)):
        print(f"({u}, {v}): {data['weight']}")
    
    return mst

def find_odd_degree_vertices(graph):

    print("\n=== STEP 2: Finding Vertices with Odd Degree ===")
    odd_degree_vertices = [v for v, d in graph.degree() if d % 2 == 1]
    print(f"Found {len(odd_degree_vertices)} vertices with odd degree: {odd_degree_vertices}")
    return odd_degree_vertices

def minimum_weight_perfect_matching(G, odd_vertices):

    print("\n=== STEP 3: Computing Minimum-Weight Perfect Matching ===")
    
    subgraph = nx.Graph()
    for u in odd_vertices:
        for v in odd_vertices:
            if u != v:
                if G.has_edge(u, v):
                    weight = G[u][v]['weight']
                else:
                    try:
                        weight = nx.shortest_path_length(G, source=u, target=v, weight='weight')
                    except nx.NetworkXNoPath:
                        weight = float('inf')
                subgraph.add_edge(u, v, weight=weight)
    
    matching = []
    unmatched = set(odd_vertices)
    
    while unmatched:
        min_weight = float('inf')
        min_edge = None
        
        u = next(iter(unmatched))
        for v in unmatched:
            if u != v and subgraph.has_edge(u, v):
                weight = subgraph[u][v]['weight']
                if weight < min_weight:
                    min_weight = weight
                    min_edge = (u, v)
        
        if min_edge:
            matching.append(min_edge)
            unmatched.remove(min_edge[0])
            unmatched.remove(min_edge[1])
        else:
            break
    
    print("Minimum-weight perfect matching:")
    total_weight = 0
    for u, v in matching:
        weight = subgraph[u][v]['weight']
        total_weight += weight
        print(f"({u}, {v}): {weight}")
    print(f"Total matching weight: {total_weight}")
    
    return matching

def create_eulerian_multigraph(G, mst, matching):

    print("\n=== STEP 4: Creating Eulerian Multigraph ===")
    
    eulerian_graph = nx.MultiGraph()
    
    for u, v, data in mst.edges(data=True):
        eulerian_graph.add_edge(u, v, weight=data['weight'])
    
    for u, v in matching:
        if G.has_edge(u, v):
            eulerian_graph.add_edge(u, v, weight=G[u][v]['weight'])
        else:
            path = nx.shortest_path(G, source=u, target=v, weight='weight')
            for i in range(len(path)-1):
                eulerian_graph.add_edge(path[i], path[i+1], weight=G[path[i]][path[i+1]]['weight'])
    
    print(f"Eulerian multigraph has {eulerian_graph.number_of_nodes()} vertices and {eulerian_graph.number_of_edges()} edges")
    
    odd_vertices = [v for v, d in eulerian_graph.degree() if d % 2 == 1]
    if odd_vertices:
        print(f"WARNING: Multigraph still contains {len(odd_vertices)} vertices with odd degree: {odd_vertices}")
    else:
        print("All vertices in the multigraph have even degree - graph is Eulerian")
    
    return eulerian_graph

def find_eulerian_circuit(multigraph):

    print("\n=== STEP 5: Finding Eulerian Circuit ===")
    
    try:
        eulerian_circuit = list(nx.eulerian_circuit(multigraph))
        
        vertices_path = [eulerian_circuit[0][0]]
        for edge in eulerian_circuit:
            vertices_path.append(edge[1])
        
        print(f"Found Eulerian circuit of length {len(vertices_path)} vertices")
        print(f"Eulerian circuit: {' -> '.join(str(v) for v in vertices_path)}")
        
        return vertices_path
    except nx.NetworkXError:
        print("ERROR: Graph is not Eulerian! Cannot find Eulerian circuit.")
        return None

def find_hamiltonian_cycle(G, eulerian_circuit):

    print("\n=== STEP 6: Transforming Eulerian Circuit into Hamiltonian Cycle ===")
    
    visited = set()
    hamiltonian_cycle = []
    
    for vertex in eulerian_circuit:
        if vertex not in visited:
            hamiltonian_cycle.append(vertex)
            visited.add(vertex)
    
    hamiltonian_cycle.append(hamiltonian_cycle[0])
    
    print(f"Resulting Hamiltonian cycle: {' -> '.join(str(v) for v in hamiltonian_cycle)}")
    
    total_weight = sum(G[hamiltonian_cycle[i]][hamiltonian_cycle[i+1]]['weight'] 
                       for i in range(len(hamiltonian_cycle)-1))
    print(f"Total Hamiltonian cycle weight: {total_weight}")
    
    return hamiltonian_cycle

def christofides_algorithm(G, verbose=True):

    if verbose:
        print("\n==== CHRISTOFIDES ALGORITHM ====\n")
    
    n = G.number_of_nodes()
    if G.number_of_edges() < n * (n - 1) / 2:
        print("WARNING: Graph is not complete, which may affect algorithm performance.")
    
    mst = calculate_mst(G) if verbose else nx.minimum_spanning_tree(G, weight='weight')
    
    odd_vertices = find_odd_degree_vertices(mst) if verbose else [v for v, d in mst.degree() if d % 2 == 1]
    
    matching = minimum_weight_perfect_matching(G, odd_vertices) if verbose else []
    
    eulerian_graph = create_eulerian_multigraph(G, mst, matching) if verbose else nx.MultiGraph()
    
    eulerian_circuit = find_eulerian_circuit(eulerian_graph) if verbose else []
    if not eulerian_circuit:
        return None
    
    hamiltonian_cycle = find_hamiltonian_cycle(G, eulerian_circuit) if verbose else []
    
    return hamiltonian_cycle

def create_graph_from_adjacency_list():
    G = nx.Graph()
    
    print("\n=== Graph Input ===")
    print("Enter adjacency list in the format:")
    print("vertex: neighbor1 neighbor2 neighbor3")
    print("Press Enter after each line")
    print("Enter an empty line to finish input")
    print("Example: '1: 2 3 4' means vertex 1 is connected to vertices 2, 3, and 4")
    print("After entering all connections, you'll be asked to provide edge weights")
    
    adj_lists = {}
    
    while True:
        line = input("Enter adjacency list (or empty line to finish): ")
        if not line.strip():
            break
        try:
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
            print("Invalid data. Vertex and neighbors must be integers.")
            
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
                    if weight < 0:
                        print("Weight cannot be negative. Using absolute value.")
                        weight = abs(weight)
                    G.add_edge(vertex, neighbor, weight=weight)
                except ValueError:
                    print("Invalid weight. Using default weight of 1.")
                    G.add_edge(vertex, neighbor, weight=1)
    
    return G

def create_complete_graph():
    try:
        n = int(input("\nEnter number of vertices: "))
        if n <= 0:
            print("Number of vertices must be positive.")
            return None
    except ValueError:
        print("Invalid data. Enter an integer.")
        return None
    
    G = nx.complete_graph(n)
    
    print("\nEnter edge weights for the complete graph:")
    print("(Make sure the weights satisfy the triangle inequality)")
    
    for u, v in G.edges():
        try:
            weight = float(input(f"Weight for edge ({u}, {v}): "))
            if weight < 0:
                print("Weight cannot be negative. Using absolute value.")
                weight = abs(weight)
            G[u][v]['weight'] = weight
        except ValueError:
            print(f"Invalid weight for edge ({u}, {v}). Using default weight of 1.")
            G[u][v]['weight'] = 1
    
    return G

def generate_euclidean_graph():
    try:
        n = int(input("\nEnter number of vertices: "))
        if n <= 0:
            print("Number of vertices must be positive.")
            return None
    except ValueError:
        print("Invalid data. Enter an integer.")
        return None
    
    G = nx.Graph()
    
    points = {}
    for i in range(n):
        x = np.random.uniform(0, 100)
        y = np.random.uniform(0, 100)
        points[i] = (x, y)
        G.add_node(i, pos=(x, y))
    
    for i in range(n):
        for j in range(i+1, n):
            x1, y1 = points[i]
            x2, y2 = points[j]
            weight = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            G.add_edge(i, j, weight=weight)
    
    print("Generated Euclidean graph with random vertex positions.")
    print("This graph automatically satisfies the triangle inequality.")
    
    return G

def visualize_graph(G, cycle=None, filename=None):
    try:
        plt.figure(figsize=(12, 10))
        
        if all('pos' in G.nodes[v] for v in G.nodes()):
            pos = {v: G.nodes[v]['pos'] for v in G.nodes()}
        else:
            pos = nx.spring_layout(G, seed=42)
        
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
        
        nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue', alpha=0.8)
        
        nx.draw_networkx_labels(G, pos)
        
        edge_labels = {(u, v): f"{d['weight']:.1f}" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        
        if cycle:
            cycle_edges = [(cycle[i], cycle[i+1]) for i in range(len(cycle)-1)]
            
            nx.draw_networkx_edges(G, pos, edgelist=cycle_edges, width=2.0, edge_color='red')
            
            total_weight = sum(G[cycle[i]][cycle[i+1]]['weight'] for i in range(len(cycle)-1))
            plt.title(f"Hamiltonian Cycle: {' -> '.join(str(v) for v in cycle)}\nCycle Length: {total_weight:.2f}")
        else:
            plt.title("Graph")
        
        plt.axis('off')
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename)
        else:
            plt.show()
        
        plt.close()
        return True
    except ImportError:
        print("Visualization requires matplotlib library, which is not installed.")
        return False

def print_graph_info(G):

    print("\n=== Graph Information ===")
    print(f"Number of vertices: {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")
    print("Vertices:", sorted(list(G.nodes())))
    
    print("\nEdges with weights:")
    total_weight = 0
    for u, v, data in sorted(G.edges(data=True)):
        weight = data['weight']
        total_weight += weight
        print(f"({u}, {v}): {weight}")
    
    print(f"\nSum of all edge weights: {total_weight}")

def use_example_graph():

    G = nx.Graph()
    
    for i in range(6):
        G.add_node(i)
    
    edges = [
        (0, 1, 4), (0, 2, 3), (0, 3, 5), (0, 4, 6), (0, 5, 5),
        (1, 2, 5), (1, 3, 7), (1, 4, 8), (1, 5, 6),
        (2, 3, 5), (2, 4, 7), (2, 5, 6),
        (3, 4, 3), (3, 5, 4),
        (4, 5, 2)
    ]
    
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)
    
    print("Loaded example graph with 6 vertices.")
    print("This graph satisfies the triangle inequality and is a complete graph.")
    
    return G

def main_menu():

    G = None
    cycle = None
    
    while True:
        print("\n=== Christofides Algorithm - Menu ===")
        print("1. Enter custom graph (adjacency list)")
        print("2. Create complete graph")
        print("3. Generate random Euclidean graph")
        print("4. Use example graph")
        print("5. Display graph information")
        print("6. Check triangle inequality")
        print("7. Compute Hamiltonian cycle (Christofides algorithm)")
        print("8. Visualize graph and solution")
        print("0. Exit")
        
        choice = input("\nChoose option (0-8): ")
        
        if choice == '1':
            G = create_graph_from_adjacency_list()
            if G.number_of_nodes() > 0:
                print(f"Created graph with {G.number_of_nodes()} vertices and {G.number_of_edges()} edges.")
                cycle = None 
            else:
                print("Cancelled graph creation or created empty graph.")
                
        elif choice == '2':
            G = create_complete_graph()
            if G is not None:
                print(f"Created complete graph with {G.number_of_nodes()} vertices.")
                cycle = None
            
        elif choice == '3':
            G = generate_euclidean_graph()
            if G is not None:
                print(f"Generated Euclidean graph with {G.number_of_nodes()} vertices.")
                cycle = None
            
        elif choice == '4':
            G = use_example_graph()
            cycle = None
            
        elif choice == '5':
            if G is None:
                print("No graph available. Please create or load a graph first.")
            else:
                print_graph_info(G)
                
        elif choice == '6':
            if G is None:
                print("No graph available. Please create or load a graph first.")
            else:
                check_triangle_inequality(G)
                
        elif choice == '7':
            if G is None:
                print("No graph available. Please create or load a graph first.")
            elif not check_triangle_inequality(G):
                print("\nTRIANGLE INEQUALITY IS NOT SATISFIED!")
                print("Christofides algorithm requires edge weights to satisfy the triangle inequality.")
                print("Without this condition, the 1.5-approximation guarantee is not ensured.")
                proceed = input("Do you want to continue anyway? (y/n): ")
                if proceed.lower() != 'y':
                    continue
            
            try:
                cycle = christofides_algorithm(G, verbose=True)
                if cycle is None:
                    print("Failed to find a solution.")
            except Exception as e:
                print(f"An error occurred: {e}")
                
        elif choice == '8':
            if G is None:
                print("No graph available. Please create or load a graph first.")
            else:
                if cycle is None:
                    print("Hamiltonian cycle not computed yet. Computing...")
                    if not check_triangle_inequality(G):
                        print("\nWARNING: Triangle inequality is not satisfied!")
                    cycle = christofides_algorithm(G, verbose=False)
                
                print("Generating visualization...")
                success = visualize_graph(G, cycle)
                if not success:
                    print("Failed to generate visualization.")
                
        elif choice == '0':
            sys.exit(0)
            
        else:
            print("Invalid choice. Please enter a number between 0 and 8.")
            
if __name__ == "__main__":
    main_menu()