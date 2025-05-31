import networkx as nx
import matplotlib.pyplot as plt
import sys
import numpy as np

class Task:
    def __init__(self, id, label=None):
        self.id = id
        self.label = label if label else f"Task {id}"
        self.level = 0
        self.processor = None
        self.start_time = None
        
    def __repr__(self):
        return f"Task {self.id} (level: {self.level})"

def verify_graph_type(G):
    print("\n=== Verifying Graph Structure ===")
    
    if not nx.is_directed_acyclic_graph(G):
        print("Error: Graph contains cycles. It must be a directed acyclic graph (DAG).")
        return False, False, False
    
    undirected = G.to_undirected()
    if nx.number_connected_components(undirected) > 1:
        print("Graph is a forest (multiple trees).")
    else:
        if len(G.edges()) == len(G.nodes()) - 1:
            print("Graph is a single tree.")
        else:
            print("Graph structure is not a proper tree or forest.")
            return False, False, False
    
    in_degrees = [d for _, d in G.in_degree()]
    out_degrees = [d for _, d in G.out_degree()]
    
    max_in_degree = max(in_degrees) if in_degrees else 0
    max_out_degree = max(out_degrees) if out_degrees else 0
    
    is_in_tree = all(d <= 1 for d in in_degrees)
    is_out_tree = all(d <= 1 for d in out_degrees)
    
    if is_in_tree and not is_out_tree:
        print("Graph is an out-tree (arcs point away from root).")
        return True, False, True
    elif is_out_tree and not is_in_tree:
        print("Graph is an in-tree (arcs point towards root).")
        return True, True, False
    elif is_in_tree and is_out_tree:
        print("Graph is both an in-tree and out-tree (single path).")
        return True, True, True
    else:
        print("Graph is neither an in-tree nor an out-tree.")
        return False, False, False

def convert_to_in_tree(G):
    print("\n=== Converting to In-Tree (if needed) ===")
    is_valid, is_in_tree, is_out_tree = verify_graph_type(G)
    
    if not is_valid:
        print("Graph structure is invalid. Cannot proceed.")
        return None
    
    if is_in_tree:
        print("Graph is already an in-tree. No conversion needed.")
        return G
    
    if is_out_tree:
        print("Converting out-tree to in-tree by reversing all edges.")
        reversed_G = G.reverse()
        return reversed_G
    
    return None

def calculate_levels(G):
    print("\n=== Calculating Node Levels ===")
    
    levels = {node: 0 for node in G.nodes()}

    leaves = [node for node in G.nodes() if G.in_degree(node) == 0]
    print(f"Leaf nodes: {leaves}")

    topo_sorted = list(nx.topological_sort(G))
    
    for node in topo_sorted:
        predecessors = list(G.predecessors(node))
        if predecessors:
            levels[node] = max(levels[pred] for pred in predecessors) + 1

    for node in sorted(G.nodes()):
        print(f"Node {node}: Level {levels[node]}")
    
    return levels

def hu_algorithm(G, num_processors=None):
    print("\n=== Executing Hu Algorithm ===")
    
    in_tree = convert_to_in_tree(G)
    if in_tree is None:
        return None
    
    tasks = {node: Task(node) for node in in_tree.nodes()}
    
    levels = calculate_levels(in_tree)
    for node, level in levels.items():
        tasks[node].level = level

    sorted_tasks = sorted(tasks.values(), key=lambda t: -t.level)
    
    max_level_count = 0
    level_counts = {}
    for level in levels.values():
        level_counts[level] = level_counts.get(level, 0) + 1
        max_level_count = max(max_level_count, level_counts[level])
    
    if num_processors is None:
        num_processors = max_level_count
        print(f"Using the minimum required number of processors: {num_processors}")
    else:
        if num_processors < max_level_count:
            print(f"Warning: At least {max_level_count} processors are required, but only {num_processors} specified.")
            print("The schedule might not be optimal.")
        print(f"Using {num_processors} processors.")

    current_time = 0
    processor_available_times = [0] * num_processors
    scheduled_tasks = []
    ready_tasks = []
    
    while len(scheduled_tasks) < len(tasks):
        for task in sorted_tasks:
            if task.start_time is None: 
                predecessors = list(in_tree.predecessors(task.id))
                if all(tasks[pred].start_time is not None and 
                       tasks[pred].start_time + 1 <= current_time for pred in predecessors):
                    ready_tasks.append(task)
        
        ready_tasks.sort(key=lambda t: -t.level)
        
        assigned = False
        while ready_tasks and not all(time > current_time for time in processor_available_times):
            task = ready_tasks.pop(0)
            
            for i in range(num_processors):
                if processor_available_times[i] <= current_time:
                    task.processor = i
                    task.start_time = current_time
                    processor_available_times[i] = current_time + 1
                    scheduled_tasks.append(task)
                    assigned = True
                    break
        
        if not assigned:
            current_time = min(time for time in processor_available_times if time > current_time)
        else:
            continue
    
    print("\n=== Final Schedule ===")
    schedule_length = max(task.start_time + 1 for task in tasks.values())
    print(f"Schedule length (makespan): {schedule_length}")
    
    for i in range(num_processors):
        tasks_on_processor = sorted([t for t in tasks.values() if t.processor == i], 
                                    key=lambda t: t.start_time)
        print(f"Processor {i}: {' -> '.join([f'{t.id}@{t.start_time}' for t in tasks_on_processor])}")
    
    return tasks

def visualize_schedule(tasks, num_processors):
    try:
        if not tasks:
            print("No tasks to visualize.")
            return False
            
        schedule_length = max(task.start_time + 1 for task in tasks.values())
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for i in range(1, num_processors):
            ax.axhline(y=i, color='gray', linestyle='-', alpha=0.3)
            
        for i in range(1, schedule_length):
            ax.axvline(x=i, color='gray', linestyle='-', alpha=0.3)
        
        for task_id, task in tasks.items():
            ax.add_patch(plt.Rectangle((task.start_time, task.processor), 1, 0.8, 
                                       edgecolor='black', facecolor='skyblue', alpha=0.8))
            ax.text(task.start_time + 0.5, task.processor + 0.4, str(task_id), 
                   ha='center', va='center', fontsize=12)
        
        ax.set_xlim(0, schedule_length)
        ax.set_ylim(0, num_processors)
        
        ax.set_yticks(np.arange(0.4, num_processors, 1))
        ax.set_yticklabels([f'P{i}' for i in range(num_processors)])
        
        ax.set_xticks(np.arange(0.5, schedule_length, 1))
        ax.set_xticklabels(range(schedule_length))
        
        ax.set_xlabel('Time')
        ax.set_ylabel('Processor')
        
        ax.set_title('Hu Algorithm Task Schedule', fontsize=16)
        
        plt.tight_layout()
        plt.show()
        
        return True
    except ImportError:
        print("Visualization requires matplotlib library.")
        return False

def visualize_graph(G, levels=None, filename=None):
    try:
        plt.figure(figsize=(12, 10))
        
        pos = nx.spring_layout(G, seed=42) if levels is None else None
        
        if levels is not None:
            pos = {}
            level_groups = {}
            
            for node, level in levels.items():
                if level not in level_groups:
                    level_groups[level] = []
                level_groups[level].append(node)
            
            max_level = max(levels.values())
            level_width = 1.0
            
            for level, nodes in level_groups.items():
                nodes.sort()
                y_pos = (max_level - level) * level_width
                num_nodes = len(nodes)
                
                for i, node in enumerate(nodes):
                    x_pos = (i - (num_nodes - 1) / 2) * level_width
                    pos[node] = (x_pos, y_pos)
        
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=700)
        nx.draw_networkx_edges(G, pos, arrows=True)
        nx.draw_networkx_labels(G, pos)
        
        if levels is not None:
            for node in G.nodes():
                plt.text(pos[node][0], pos[node][1] - 0.1, f"L: {levels[node]}", 
                        fontsize=10, ha='center')
        
        plt.title("Task Dependency Graph", fontsize=16)
        plt.axis('off')
        
        if filename:
            plt.savefig(filename)
        else:
            plt.show()
            
        return True
    except ImportError:
        print("Visualization requires matplotlib library.")
        return False

def create_graph_from_adjacency_list():
    G = nx.DiGraph()
    
    print("\n=== Graph Input ===")
    print("Enter adjacency list in the format:")
    print("source: target1 target2 target3")
    print("Press Enter after each line")
    print("Enter an empty line to finish input")
    print("Example: '1: 2 3 4' means tasks 2, 3, and 4 depend on task 1")
    
    adj_lists = {}
    
    while True:
        line = input("Enter adjacency list (or empty line to finish): ")
        if not line.strip():
            break
        try:
            if ':' not in line:
                print("Invalid format. Expected 'source: target1 target2 target3'")
                continue
            
            parts = line.split(':', 1)
            source = int(parts[0].strip())
            
            if len(parts) > 1 and parts[1].strip():
                targets = [int(n.strip()) for n in parts[1].strip().split()]
            else:
                targets = []
            
            adj_lists[source] = targets
            G.add_node(source)
        
        except ValueError:
            print("Invalid data. Nodes must be integers.")
            
    for source in adj_lists:
        for target in adj_lists[source]:
            if target not in G:
                G.add_node(target)
            G.add_edge(source, target)
    
    return G

def print_graph_info(G):
    print("\n=== Graph Information ===")
    print(f"Number of nodes: {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")
    print("Nodes:", sorted(list(G.nodes())))
    
    print("\nEdges:")
    for u, v in sorted(G.edges()):
        print(f"{u} -> {v}")
        
    is_valid, is_in_tree, is_out_tree = verify_graph_type(G)
    
    if is_valid:
        if is_in_tree and is_out_tree:
            print("\nGraph is both an in-tree and out-tree (simple path)")
        elif is_in_tree:
            print("\nGraph is an in-tree")
        elif is_out_tree:
            print("\nGraph is an out-tree")
    else:
        print("\nGraph is not a valid tree or forest.")

def use_example_graph(example_type):
    G = nx.DiGraph()
    
    if example_type == 'in-tree':
        edges = [(1, 0), (2, 0), (3, 1), (4, 1), (5, 2), (6, 2)]
        G.add_nodes_from(range(7))
        G.add_edges_from(edges)
        print("Created example in-tree with 7 nodes.")
        
    elif example_type == 'out-tree':
        edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
        G.add_nodes_from(range(7))
        G.add_edges_from(edges)
        print("Created example out-tree with 7 nodes.")
        
    elif example_type == 'forest':
        edges = [(0, 1), (0, 2), (3, 4), (3, 5)]
        G.add_nodes_from(range(6))
        G.add_edges_from(edges)
        print("Created example forest with 6 nodes in two trees.")
        
    return G

def main_menu():
    G = None
    tasks = None
    num_processors = None
    
    while True:
        print("\n=== Hu Algorithm ===")
        print("1. Create graph manually (adjacency list)")
        print("2. Create example in-tree")
        print("3. Create example out-tree")
        print("4. Create example forest")
        print("5. Display graph information")
        print("6. Visualize graph")
        print("7. Run Hu algorithm")
        print("8. Visualize schedule")
        print("0. Exit")
        
        choice = input("\nChoose option (0-9): ")
        
        if choice == '1':
            G = create_graph_from_adjacency_list()
            if G.number_of_nodes() > 0:
                print(f"Created graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
                tasks = None
            else:
                print("Graph creation cancelled or empty graph created.")
                
        elif choice == '2':
            G = use_example_graph('in-tree')
            tasks = None
            
        elif choice == '3':
            G = use_example_graph('out-tree')
            tasks = None
            
        elif choice == '4':
            G = use_example_graph('forest')
            tasks = None
                
        elif choice == '5':
            if G is None:
                print("No graph available. Please create a graph first.")
            else:
                print_graph_info(G)
                
        elif choice == '6':
            if G is None:
                print("No graph available. Please create a graph first.")
            else:
                if tasks is None:
                    in_tree = convert_to_in_tree(G)
                    if in_tree is not None:
                        levels = calculate_levels(in_tree)
                        visualize_graph(in_tree, levels)
                    else:
                        visualize_graph(G)
                else:
                    levels = {task_id: task.level for task_id, task in tasks.items()}
                    in_tree = convert_to_in_tree(G)
                    visualize_graph(in_tree, levels)
                
        elif choice == '7':
            if G is None:
                print("No graph available. Please create a graph first.")
            else:
                try:
                    processor_input = input("Enter number of processors (leave blank for minimum required): ")
                    if processor_input.strip():
                        num_processors = int(processor_input)
                        if num_processors <= 0:
                            print("Number of processors must be positive.")
                            continue
                    else:
                        num_processors = None
                        
                    tasks = hu_algorithm(G, num_processors)
                    
                except ValueError as e:
                    print(f"Error: {e}")
                    
        elif choice == '8':
            if tasks is None:
                print("No schedule available. Please run Hu algorithm first.")
            else:
                visualize_schedule(tasks, num_processors if num_processors is not None else max(task.processor for task in tasks.values()) + 1)
                
        elif choice == '0':
            sys.exit(0)
            
        else:
            print("Invalid choice. Please enter a number between 0 and 9.")

if __name__ == "__main__":
    main_menu()