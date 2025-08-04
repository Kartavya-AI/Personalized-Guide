import sqlite3
import pandas as pd

DB_NAME = "travel_guide.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            place_name TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def add_favorite(city: str, place_name: str) -> str:
    if not city or not place_name:
        return "⚠️ Error: City and Place Name cannot be empty."
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO favorites (city, place_name) VALUES (?, ?)", (city, place_name))
        conn.commit()
        response = f"✅ **{place_name}** has been saved to your favorites!"
    except sqlite3.IntegrityError:
        response = f"🤔 Looks like **{place_name}** is already in your favorites list."
    except Exception as e:
        response = f"🚨 An error occurred: {e}"
    finally:
        conn.close()
    return response

def get_favorites() -> pd.DataFrame:
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT city as City, place_name as 'Favorite Place' FROM favorites", conn)
    except Exception as e:
        df = pd.DataFrame(columns=["City", "Favorite Place"])
    finally:
        conn.close()
    return df

def clear_favorites():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorites")
    conn.commit()
    conn.close()