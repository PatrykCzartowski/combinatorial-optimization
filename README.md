# Combinatorial Optimization Algorithms

This repository contains implementations of various combinatorial optimization algorithms, focusing on approximation algorithms for NP-hard problems.

## Algorithms Implemented

### 1. Verification of C3 Cycle Presence in a Graph
- Located in `/01_Verification_of_C3_cycle_presense_in_a_graph/`
- Implements two methods for detecting C3 cycles (triangles) in graphs:
  - Naive approach (checking all possible triplets)
  - Matrix multiplication approach (more efficient)

### 2. 2-Approximation Algorithm for Vertex Cover
- Located in `/02_2_approximation_alg_for_vertex_cover/`
- Provides a polynomial-time algorithm that guarantees a vertex cover at most twice the size of the optimal solution
- Features:
  - Interactive graph creation
  - Random graph generation
  - Visualization of the solution

### 3. 2-Approximation Algorithm for Steiner Tree
- Located in `/03_2_approximation_alg_for_steiner_tree/`
- Implements the classic 2-approximation algorithm for the Steiner Tree problem:
  1. Creating a complete graph on terminal vertices
  2. Finding MST of the complete graph
  3. Expanding MST edges into shortest paths
  4. Finding MST of the expanded graph
  5. Pruning non-terminal leaves
- Features:
  - Interactive mode with detailed steps
  - Example graph with visualization
  - Support for custom graph input

### 4. 1.5-Approximation Christofides Algorithm for TSP
- Located in `/04_Christofides_algorithm/`
- Implements the Christofides algorithm for the Traveling Salesman Problem:
  1. Computing a minimum spanning tree
  2. Finding vertices with odd degree in the MST
  3. Computing minimum-weight perfect matching for odd-degree vertices
  4. Creating an Eulerian multigraph
  5. Finding an Eulerian circuit
  6. Converting the Eulerian circuit to a Hamiltonian cycle
- Features:
  - Triangle inequality verification (required for 1.5-approximation guarantee)
  - Multiple graph creation options including Euclidean graphs
  - Detailed step-by-step explanation
  - Visualization of the solution
  - Interactive user interface

### 5. Critical Path Method (CPM) for Project Scheduling
- Located in `/05_Critical_path_method/`
- Implements the Critical Path Method for project scheduling and management:
  1. Task dependency modeling with directed acyclic graphs
  2. Calculation of earliest and latest start/finish times
  3. Identification of critical path and slack time
  4. Generation of project schedule and duration
- Features:
  - Interactive task input with dependency validation
  - Multiple network representations (Activity-on-Node and Activity-on-Arc)
  - Visual Gantt chart for project schedule
  - Critical path highlighting in all visualizations
  - Support for custom projects or example task set
  - Detection of circular dependencies

### 6. Hu's Algorithm for P|p_j=1,in-tree|C_max
- Located in `/06_Hu_algorithm/`
- Implements Hu's algorithm for scheduling unit-time tasks with precedence constraints:
  1. Verification of graph structure (in-tree, out-tree, forest)
  2. Conversion of out-tree to in-tree if necessary
  3. Calculation of task levels (longest path from any leaf)
  4. Task scheduling based on decreasing level order
- Features:
  - Support for both in-trees and out-trees
  - Automatic conversion to in-tree when needed
  - Optimal scheduling with minimum required processors
  - Visualization of task dependency graph with levels
  - Visual representation of the final schedule
  - Interactive graph creation and example graphs

## Usage

Each algorithm can be run independently from its directory. Most implementations include:

- Interactive command-line interface
- Visualization capabilities (requires matplotlib)
- Step-by-step explanations of algorithm execution
- Options to input custom graphs or use provided examples

### Requirements
- Python 3.x
- NetworkX
- NumPy
- Matplotlib (for visualization)

## Background

These implementations are designed for educational purposes to demonstrate common approximation techniques for NP-hard combinatorial optimization problems.

## License

This project is open source and available under the [MIT License](LICENSE).