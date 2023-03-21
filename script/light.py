import random

n = 10
matrix = [[random.random() for j in range(n)] for i in range(n)]

def matrix_inverse(matrix):
    n = len(matrix)
    matrix_copy = [row[:] for row in matrix]
    identity = [[float(i == j) for j in range(n)] for i in range(n)]
    for col in range(n):
        pivot_row = max(range(col, n), key=lambda i: abs(matrix_copy[i][col]))
        if col != pivot_row:
            matrix_copy[col], matrix_copy[pivot_row] = matrix_copy[pivot_row], matrix_copy[col]
            identity[col], identity[pivot_row] = identity[pivot_row], identity[col]
        pivot = matrix_copy[col][col]
        for row in range(col + 1, n):
            factor = matrix_copy[row][col] / pivot
            matrix_copy[row][col] = 0
            for col2 in range(col + 1, n):
                matrix_copy[row][col2] -= matrix_copy[col][col2] * factor
            for col2 in range(n):
                identity[row][col2] -= identity[col][col2] * factor
    for col in range(n - 1, -1, -1):
        pivot = matrix_copy[col][col]
        for row in range(col):
            factor = matrix_copy[row][col] / pivot
            matrix_copy[row][col] = 0
            for col2 in range(n):
                identity[row][col2] -= identity[col][col2] * factor
    return identity

power = 100
result = matrix
for i in range(power - 1):
    result = [[sum(a * b for a, b in zip(row, col)) for col in zip(*matrix_inverse(result))] for row in matrix]

def matrix_multiply(A, B):
    return [[sum(a * b for a, b in zip(row, col)) for col in zip(*B)] for row in A]

eigenvectors = matrix
for i in range(100):
    eigenvectors = matrix_multiply(result, eigenvectors)

eigenvalues = [eigenvectors[i][i] for i in range(n)]

print(eigenvalues)
