from flask import Flask, render_template, request, jsonify
import sqlite3
from openai import OpenAI
import os
from dotenv import load_dotenv

# Завантаження змінних із файлу Contract_block.env
load_dotenv("Contract_block.env")

# Отримання API ключа з змінних середовища
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY не знайдений! Перевірте ваш .env файл або налаштування середовища.")

# Налаштування API OpenAI
client = OpenAI(api_key=api_key)

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

# API для генерації договору через GPT-4
@app.route("/api/generate_contract", methods=["POST"])
def generate_contract_api():
    data = request.json
    description = data.get("description", "").strip()
    contract_text = data.get("contractText", "").strip()

    if not contract_text:
        return jsonify({"success": False, "error": "Текст договору порожній"})

    try:
        # Запит до GPT-4 для створення договору
        response = client.chat.completions.create(
            model="gpt-4",  # Використовуємо модель GPT-4
            messages=[
                {"role": "system", "content": "Ти — помічник для створення договорів."},
                {"role": "user", "content": f"Опис договору: {description}\n\nТекст договору: {contract_text}\n\nСтвори повний текст договору з логічною структурою та нумерацією пунктів."}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        # Отримання результату від GPT-4
        generated_contract = response.choices[0].message.content.strip()

        return jsonify({"success": True, "generated_contract": generated_contract})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Запуск програми
if __name__ == "__main__":
    init_db()
    app.run(debug=True)