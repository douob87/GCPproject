from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"


def init_db():
    with sqlite3.connect("users.db") as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """
        )


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


@app.route("/register", methods=["POST"])
def register():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return jsonify({"message": "請提供完整的 Email 和密碼"}), 400

    hashed_password = generate_password_hash(password)

    try:
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (email, password) VALUES (?, ?)",
                (email, hashed_password),
            )
            conn.commit()
            return jsonify({"message": "註冊成功"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "此 Email 已被註冊"}), 400


# 處理登錄請求
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()

    if row and check_password_hash(row[0], password):
        session["email"] = email
        return jsonify({"message": "登入成功"}), 200
    return jsonify({"message": "帳號或密碼錯誤"}), 401


if __name__ == "__main__":
    app.run(debug=True)
