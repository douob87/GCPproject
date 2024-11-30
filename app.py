from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json

app = Flask(__name__)
users_data = {}


def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def solve_sudoku(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:  # 找到未填的格子
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0  # 回溯
                return False
    return True


def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def solve(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve(board):
                            return True
                        board[row][col] = 0
                return False
    return True


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/solve", methods=["POST"])
def solve():
    data = request.get_json()
    board = data.get("board")

    if not board or len(board) != 9 or any(len(row) != 9 for row in board):
        return jsonify({"error": "Invalid board format. Must be a 9x9 grid."}), 400

    if solve_sudoku(board):
        return jsonify({"solved": True, "board": board})
    else:
        return jsonify({"solved": False, "message": "No solution exists."})


@app.route("/password")
def password():
    return render_template("password.html")


if __name__ == "__main__":
    app.run(debug=True)
