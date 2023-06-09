import random
from flask import Flask, jsonify
import sys
from datetime import datetime
#Title: Non sense cpu cosuming code generated by Chatgpt
#Script from chatGpt
#https://chat.openai.com

app = Flask(__name__)

@app.route('/')
def main():
    strt_time = datetime.now()
    if len(sys.argv) != 2:
        return 'require more arguments'
    n = 10
    matrix = [[random.random() for j in range(n)] for i in range(n)]
    power = 100
    result = matrix
    for i in range(power - 1):
        result = [[sum(a * b for a, b in zip(row, col)) for col in zip(*matrix_inverse(result))] for row in matrix]
    eigenvectors = matrix
    for i in range(100):
        eigenvectors = matrix_multiply(result, eigenvectors)
    eigenvalues = [eigenvectors[i][i] for i in range(n)]
    a = len(eigenvalues)
    end_time = datetime.now()
    return "Input size: " + str(n) + "; from " + "medium server " + sys.argv[1] + "; start from " + str(strt_time) + " end at " + str(end_time)  + "\n"

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


def matrix_multiply(A, B):
    return [[sum(a * b for a, b in zip(row, col)) for col in zip(*B)] for row in A]


if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0' , port = 5000)
