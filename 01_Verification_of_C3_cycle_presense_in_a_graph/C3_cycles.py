def find_C3_naive(adj_matrix):
    n = len(adj_matrix)
    for i in range(n):
        for j in range(n):
            if adj_matrix[i][j] == 1:
                for k in range(n):
                    if adj_matrix[j][k] == 1 and adj_matrix[k][i] == 1:
                        return print(f"->   Found C3 cycle: {i+1} -> {j+1} -> {k+1} -> {i+1}")
    return print("->   No C3 cycle found")

def find_C3_matrix_multiplication(adj_matrix):
    import numpy as np
    
    A = np.array(adj_matrix)
    A_squared = np.matmul(A, A)
    n = A.shape[0]
    for i in range(n):
        for j in range(n):
            if i != j and A[i, j] == 1 and A_squared[i, j] > 0:
                return True
    return False 

def convert_adj_list_to_adj_matrix(adj_list):
    max_node = max(max(adj_list.keys()), max([max(neighbors) if neighbors else 0 for neighbors in adj_list.values()]))
    
    adj_matrix = [[0] * max_node for _ in range(max_node)]
    
    for node, neighbors in adj_list.items():
        for neighbor in neighbors:
            adj_matrix[node - 1][neighbor - 1] = 1
            adj_matrix[neighbor - 1][node - 1] = 1 
    
    return adj_matrix

def main():
    adj_list = {}
    print("Enter adjacency list:")
    try:
        while True:
            line = input().strip()
            if not line:
                break
            node, *neighbors = map(int, line.split())
            adj_list[node] = neighbors
    except EOFError:
        pass
    
    adj_matrix = convert_adj_list_to_adj_matrix(adj_list)
    
    print("Adjacency matrix:")
    for row in adj_matrix:
        print(" ".join(map(str, row)))
    print("")
    print("Finding C3 using naive algorithm:")
    find_C3_naive(adj_matrix)
    print("Finding C3 using matrix multiplication:")
    print("->   TAK" if find_C3_matrix_multiplication(adj_matrix) else "->   NIE")
    
if __name__ == "__main__":
    main()