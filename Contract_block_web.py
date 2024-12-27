#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 15:21:00 2024

@author: dmytrobarabin
"""

from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Ініціалізація бази даних
def init_db():
    conn = sqlite3.connect("blocks.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocks (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            text TEXT NOT NULL,
            type TEXT NOT NULL DEFAULT 'Інше'
        )
    """)
    conn.commit()
    conn.close()

# Завантаження блоків із бази даних
def get_blocks(block_type):
    conn = sqlite3.connect("blocks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, text FROM blocks WHERE type = ?", (block_type,))
    blocks = cursor.fetchall()
    conn.close()
    return blocks

# Додавання нового блоку
def add_block_to_db(name, text, block_type):
    conn = sqlite3.connect("blocks.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO blocks (name, text, type) VALUES (?, ?, ?)", (name, text, block_type))
    conn.commit()
    conn.close()

# Оновлення блоку
def update_block_in_db(block_id, name, text, block_type):
    conn = sqlite3.connect("blocks.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE blocks SET name = ?, text = ?, type = ? WHERE id = ?", (name, text, block_type, block_id))
    conn.commit()
    conn.close()

# Видалення блоку
def delete_block_from_db(block_id):
    conn = sqlite3.connect("blocks.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blocks WHERE id = ?", (block_id,))
    conn.commit()
    conn.close()

# Головна сторінка
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/blocks")
def blocks():
    return render_template("blocks.html")  # Відправляємо шаблон blocks.html до браузера

# API для отримання блоків
@app.route("/api/blocks", methods=["GET"])
def get_blocks_api():
    block_type = request.args.get("type", "Інше")
    blocks = get_blocks(block_type)
    return jsonify(blocks)

# API для додавання блоку
@app.route("/api/add_block", methods=["POST"])
def add_block_api():
    data = request.json
    name = data.get("name")
    text = data.get("text")
    block_type = data.get("type")
    if name and text and block_type:
        add_block_to_db(name, text, block_type)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid data"})

# API для оновлення блоку
@app.route("/api/update_block", methods=["POST"])
def update_block_api():
    data = request.json
    block_id = data.get("id")
    name = data.get("name")
    text = data.get("text")
    block_type = data.get("type")
    if block_id and name and text and block_type:
        update_block_in_db(block_id, name, text, block_type)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid data"})

# API для видалення блоку
@app.route("/api/delete_block", methods=["POST"])
def delete_block_api():
    data = request.json
    block_id = data.get("id")
    if block_id:
        delete_block_from_db(block_id)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid data"})

# Запуск програми
if __name__ == "__main__":
    init_db()
    app.run(debug=True)