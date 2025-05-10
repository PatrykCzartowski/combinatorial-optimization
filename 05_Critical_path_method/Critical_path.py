import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import sys

class Task:
    def __init__(self, id, name, duration, dependencies=None):
        self.id = id
        self.name = name
        self.duration = duration
        self.dependencies = dependencies if dependencies else []
        self.earliest_start = 0
        self.earliest_finish = 0
        self.latest_start = 0
        self.latest_finish = 0
        self.slack = 0
        self.is_critical = False
    
    def __repr__(self):
        return f"Task {self.id}: {self.name} (duration: {self.duration})"

def calculate_earliest_times(tasks, task_dict):
    G = nx.DiGraph()
    
    for task in tasks:
        G.add_node(task.id)
        for dep in task.dependencies:
            G.add_edge(dep, task.id)
    
    try:
        sorted_task_ids = list(nx.topological_sort(G))
    except nx.NetworkXUnfeasible:
        print("Error: Cycle detected in task dependencies. Cannot proceed with CPM.")
        return False
    
    for task_id in sorted_task_ids:
        task = task_dict[task_id]
        
        if not task.dependencies:
            task.earliest_start = 0
        else:
            task.earliest_start = max(task_dict[dep].earliest_finish for dep in task.dependencies)
        
        task.earliest_finish = task.earliest_start + task.duration
    
    return True

def calculate_latest_times(tasks, task_dict):
    
    project_end = max(task.earliest_finish for task in tasks)
    
    G = nx.DiGraph()
    
    for task in tasks:
        G.add_node(task.id)
        for dep in task.dependencies:
            G.add_edge(task.id, dep)  # Edge direction is reversed
    
    sorted_task_ids = list(reversed(list(nx.topological_sort(nx.DiGraph([(v, u) for u, v in G.edges()])))))
    
    for task in tasks:
        task.latest_finish = project_end
    
    for task_id in sorted_task_ids:
        task = task_dict[task_id]
        
        successors = [t for t in tasks if task.id in t.dependencies]
        
        if successors:
            task.latest_finish = min(succ.latest_start for succ in successors)
        
        task.latest_start = task.latest_finish - task.duration
        
        task.slack = task.latest_start - task.earliest_start
        
        task.is_critical = task.slack == 0

def identify_critical_path(tasks):
    critical_tasks = [task for task in tasks if task.is_critical]
    critical_path = sorted(critical_tasks, key=lambda x: x.earliest_start)
    
    return critical_path

def print_schedule_info(tasks, critical_path):
    project_duration = max(task.earliest_finish for task in tasks)
    
    print("\n=== Project Schedule Information ===")
    print(f"Project Duration: {project_duration} time units")
    print("\nCritical Path:")
    cp_str = " -> ".join([f"{task.id} ({task.name})" for task in critical_path])
    print(cp_str)
    
    print("\nDetailed Task Information:")
    print("-------------------------------------------------------------------------------------")
    print("| ID | Task Name                | Duration | ES  | EF  | LS  | LF  | Slack | Critical |")
    print("-------------------------------------------------------------------------------------")
    
    for task in sorted(tasks, key=lambda x: x.id):
        name = task.name[:22] + "..." if len(task.name) > 25 else task.name
        name = name.ljust(24)
        print(f"| {task.id:<2} | {name} | {task.duration:<8} | {task.earliest_start:<3} | "
              f"{task.earliest_finish:<3} | {task.latest_start:<3} | {task.latest_finish:<3} | "
              f"{task.slack:<5} | {'Yes' if task.is_critical else 'No':<8} |")
    
    print("-------------------------------------------------------------------------------------")
    print("ES = Earliest Start, EF = Earliest Finish, LS = Latest Start, LF = Latest Finish")

def create_activity_on_node_network(tasks):
    G = nx.DiGraph()
    
    for task in tasks:
        G.add_node(task.id, label=f"{task.id}: {task.name}\nDur: {task.duration}", 
                   duration=task.duration, is_critical=task.is_critical)
    
    for task in tasks:
        for dep in task.dependencies:
            G.add_edge(dep, task.id)
    
    return G

def create_activity_on_arc_network(tasks, task_dict):
    G = nx.DiGraph()
    
    events = {}  # Map from task.id to (start_event, end_event)
    event_counter = 0
    
    start_event = event_counter
    G.add_node(start_event, label=f"Event {start_event}")
    event_counter += 1
    
    for task in tasks:
        if not task.dependencies:
            start_node = start_event
        else:
            pred_ends = [events[dep][1] for dep in task.dependencies if dep in events]
            
            if not pred_ends:
                start_node = start_event
            else:
                start_node = max(pred_ends)
        
        end_node = event_counter
        G.add_node(end_node, label=f"Event {end_node}")
        event_counter += 1
        
        G.add_edge(start_node, end_node, 
                  label=f"{task.id}: {task.name}",
                  task_id=task.id,
                  duration=task.duration,
                  is_critical=task.is_critical)
        
        events[task.id] = (start_node, end_node)
    
    return G

def visualize_aon_network(G):
    try:
        plt.figure(figsize=(15, 10))
        
        pos = nx.spring_layout(G, seed=42)
        
        critical_nodes = [node for node, attrs in G.nodes(data=True) if attrs.get('is_critical', False)]
        non_critical_nodes = [node for node in G.nodes() if node not in critical_nodes]
        
        nx.draw_networkx_nodes(G, pos, nodelist=critical_nodes, node_color='red', node_size=1000, alpha=0.8)
        nx.draw_networkx_nodes(G, pos, nodelist=non_critical_nodes, node_color='lightblue', node_size=1000, alpha=0.8)
        
        nx.draw_networkx_edges(G, pos, arrows=True)
        
        labels = {node: attrs['label'] for node, attrs in G.nodes(data=True)}
        
        for node, label in labels.items():
            x, y = pos[node]
            plt.text(x, y, label, fontsize=10, ha='center', va='center',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='black', boxstyle='round,pad=0.5'))
        
        plt.title("Activity-on-Node (AoN) Network", fontsize=16)
        plt.legend([Rectangle((0, 0), 1, 1, fc="red", alpha=0.8),
                   Rectangle((0, 0), 1, 1, fc="lightblue", alpha=0.8)],
                   ["Critical Tasks", "Non-Critical Tasks"],
                   loc="upper right")
        plt.axis('off')
        plt.tight_layout()
        plt.show()
        
    except ImportError:
        print("Visualization requires matplotlib which is not installed.")
        return False

def visualize_aoa_network(G):
    try:
        plt.figure(figsize=(15, 10))
        
        pos = nx.spring_layout(G, seed=42)
        
        nx.draw_networkx_nodes(G, pos, node_color='lightgrey', node_size=800, alpha=0.8)
        
        critical_edges = [(u, v) for u, v, attrs in G.edges(data=True) if attrs.get('is_critical', False)]
        non_critical_edges = [(u, v) for u, v in G.edges() if (u, v) not in critical_edges]
        
        nx.draw_networkx_edges(G, pos, edgelist=critical_edges, width=2.5, edge_color='red', arrows=True)
        nx.draw_networkx_edges(G, pos, edgelist=non_critical_edges, width=1.5, edge_color='black', alpha=0.7, arrows=True)
        
        node_labels = {node: attrs['label'] for node, attrs in G.nodes(data=True)}
        
        edge_labels = {(u, v): attrs['label'] for u, v, attrs in G.edges(data=True)}
        
        nx.draw_networkx_labels(G, pos, labels=node_labels)
        
        for (u, v), label in edge_labels.items():
            x = (pos[u][0] + pos[v][0]) / 2
            y = (pos[u][1] + pos[v][1]) / 2
            plt.text(x, y, label, fontsize=10, ha='center', va='center',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='black'))
        
        plt.title("Activity-on-Arc (AoA) Network", fontsize=16)
        plt.legend([Rectangle((0, 0), 1, 1, fc="red", alpha=0.8, linewidth=2.5),
                   Rectangle((0, 0), 1, 1, fc="black", alpha=0.7, linewidth=1.5)],
                   ["Critical Path", "Non-Critical Path"],
                   loc="upper right")
        plt.axis('off')
        plt.tight_layout()
        plt.show()
        
    except ImportError:
        print("Visualization requires matplotlib which is not installed.")
        return False

def visualize_schedule_gantt(tasks):
    try:
        sorted_tasks = sorted(tasks, key=lambda x: x.earliest_start)
        
        project_duration = max(task.earliest_finish for task in tasks)
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        y_labels = [f"{task.id}: {task.name}" for task in sorted_tasks]
        y_pos = np.arange(len(y_labels))
        
        for i, task in enumerate(sorted_tasks):
            ax.barh(i, task.duration, left=task.earliest_start, 
                   color='darkred' if task.is_critical else 'steelblue', alpha=0.8)
            
            if task.slack > 0:
                ax.barh(i, task.slack, left=task.earliest_finish, 
                       color='lightgrey', alpha=0.5)
                
            ax.text(task.earliest_start + task.duration / 2, i, 
                   f"{task.id}", ha='center', va='center', color='white')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(y_labels)
        ax.set_xlabel('Time')
        ax.set_title('Project Schedule (Gantt Chart)', fontsize=16)
        ax.grid(axis='x', alpha=0.3)
        
        # Set x-axis to cover the project duration with some margin
        ax.set_xlim(0, project_duration * 1.1)
        
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='darkred', label='Critical Task'),
            Patch(facecolor='steelblue', label='Non-Critical Task'),
            Patch(facecolor='lightgrey', alpha=0.5, label='Slack Time')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        plt.show()
        
    except ImportError:
        print("Visualization requires matplotlib which is not installed.")
        return False

def input_tasks():
    tasks = []
    existing_ids = set()
    
    print("\n=== Task Input ===")
    print("Enter task details in the following format:")
    print("ID Name Duration Dependencies(comma-separated,optional)")
    print("Example: 'A Design 5 ' means task A named 'Design' takes 5 time units with no dependencies")
    print("Example: 'B Build 7 A' means task B depends on task A")
    print("Enter an empty line to finish input")
    
    while True:
        line = input("\nEnter task details (or empty line to finish): ").strip()
        if not line:
            break
        
        parts = line.split(" ", 3)  # Split into max 4 parts: ID Name Duration Dependencies
        
        try:
            if len(parts) < 3:
                print("Invalid format. Please use: ID Name Duration [Dependencies]")
                continue
            
            task_id = parts[0]
            name = parts[1]
            
            try:
                duration = int(parts[2])
                if duration <= 0:
                    print("Duration must be positive.")
                    continue
            except ValueError:
                print("Duration must be a positive number.")
                continue
            
            if task_id in existing_ids:
                print(f"Task ID '{task_id}' already exists. Please use a unique ID.")
                continue
            
            dependencies = []
            if len(parts) > 3 and parts[3].strip():
                dependencies = [dep.strip() for dep in parts[3].split(",")]
            
            task = Task(task_id, name, duration, dependencies)
            tasks.append(task)
            existing_ids.add(task_id)
            
            print(f"Added task: {task}")
            
        except Exception as e:
            print(f"Error adding task: {e}")
    
    return tasks

def use_example_tasks():
    tasks = [
        Task("A", "Planning", 3, []),
        Task("B", "Design", 4, ["A"]),
        Task("C", "Prototype", 5, ["A"]),
        Task("D", "Testing", 3, ["B", "C"]),
        Task("E", "Documentation", 2, ["B"]),
        Task("F", "Production", 6, ["D"]),
        Task("G", "Delivery", 2, ["E", "F"]),
        Task("H", "Feedback", 3, ["G"]),
        Task("I", "Refinement", 4, ["H"])
    ]
    
    print("Example tasks created:")
    for task in tasks:
        deps = ", ".join(task.dependencies) if task.dependencies else "None"
        print(f"{task.id}: {task.name} (Duration: {task.duration}, Dependencies: {deps})")
        
    return tasks

def validate_tasks(tasks):
    task_ids = {task.id for task in tasks}
    
    for task in tasks:
        for dep in task.dependencies:
            if dep not in task_ids:
                print(f"Error: Task {task.id} depends on unknown task {dep}")
                return False
    
    G = nx.DiGraph()
    for task in tasks:
        G.add_node(task.id)
        for dep in task.dependencies:
            G.add_edge(dep, task.id)
    
    try:
        cycles = list(nx.simple_cycles(G))
        if cycles:
            print("Error: Circular dependencies detected:")
            for cycle in cycles:
                print(" -> ".join(cycle + [cycle[0]]))
            return False
    except nx.NetworkXNoCycle:
        pass
    
    return True

def main_menu():
    tasks = None
    
    while True:
        print("\n=== Critical Path Method (CPM) ===")
        print("1. Input tasks manually")
        print("2. Use example tasks")
        print("3. Calculate critical path and schedule")
        print("4. View Activity-on-Node (AoN) network")
        print("5. View Activity-on-Arc (AoA) network")
        print("6. View Gantt chart schedule")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ")
        
        if choice == '1':
            tasks = input_tasks()
            if tasks and len(tasks) > 0:
                print(f"Created {len(tasks)} tasks.")
            else:
                print("No tasks created.")
                
        elif choice == '2':
            tasks = use_example_tasks()
            
        elif choice == '3':
            if not tasks or len(tasks) == 0:
                print("No tasks available. Please input or create example tasks first.")
            else:
                if not validate_tasks(tasks):
                    print("Task validation failed. Please check your task dependencies.")
                    continue
                
                task_dict = {task.id: task for task in tasks}
                
                if calculate_earliest_times(tasks, task_dict):
                    calculate_latest_times(tasks, task_dict)
                    
                    critical_path = identify_critical_path(tasks)
                    
                    print_schedule_info(tasks, critical_path)
                else:
                    print("Could not calculate schedule due to errors.")
                
        elif choice == '4':
            if not tasks or len(tasks) == 0:
                print("No tasks available. Please input or create example tasks first.")
            else:
                if tasks[0].earliest_start == 0 and tasks[0].latest_start == 0:
                    print("Critical path not yet calculated. Calculating now...")
                    task_dict = {task.id: task for task in tasks}
                    if calculate_earliest_times(tasks, task_dict):
                        calculate_latest_times(tasks, task_dict)
                
                aon_network = create_activity_on_node_network(tasks)
                visualize_aon_network(aon_network)
                
        elif choice == '5':
            if not tasks or len(tasks) == 0:
                print("No tasks available. Please input or create example tasks first.")
            else:
                if tasks[0].earliest_start == 0 and tasks[0].latest_start == 0:
                    print("Critical path not yet calculated. Calculating now...")
                    task_dict = {task.id: task for task in tasks}
                    if calculate_earliest_times(tasks, task_dict):
                        calculate_latest_times(tasks, task_dict)
                
                task_dict = {task.id: task for task in tasks}
                aoa_network = create_activity_on_arc_network(tasks, task_dict)
                visualize_aoa_network(aoa_network)
                
        elif choice == '6':
            if not tasks or len(tasks) == 0:
                print("No tasks available. Please input or create example tasks first.")
            else:
                if tasks[0].earliest_start == 0 and tasks[0].latest_start == 0:
                    print("Critical path not yet calculated. Calculating now...")
                    task_dict = {task.id: task for task in tasks}
                    if calculate_earliest_times(tasks, task_dict):
                        calculate_latest_times(tasks, task_dict)
                
                visualize_schedule_gantt(tasks)
                
        elif choice == '0':
            sys.exit(0)
            
        else:
            print("Invalid choice. Please enter a number between 0 and 6.")
            
        input("\nPress Enter to continue...")
            
if __name__ == "__main__":
    main_menu()