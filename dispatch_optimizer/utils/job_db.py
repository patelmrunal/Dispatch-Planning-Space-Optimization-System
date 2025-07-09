"""
job_db.py
Utility for storing and retrieving optimization jobs in SQLite.
"""

import sqlite3
import json
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'jobs.db')
DB_PATH = os.path.abspath(DB_PATH)

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def serialize_for_db(obj):
    """Serialize object to JSON string, handling datetime objects."""
    return json.dumps(obj, cls=DateTimeEncoder)

def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        input_csv TEXT,
        constraints TEXT,
        output_csv TEXT
    )''')
    
    # Add dispatch routes table
    c.execute('''CREATE TABLE IF NOT EXISTS dispatch_routes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  route_data TEXT,
                  route_summary TEXT,
                  products_data TEXT)''')
    
    conn.commit()
    conn.close()

def save_job(input_csv, constraints, output_csv):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO jobs (timestamp, input_csv, constraints, output_csv) VALUES (?, ?, ?, ?)",
              (datetime.now().isoformat(), input_csv, json.dumps(constraints), output_csv))
    conn.commit()
    conn.close()

def list_jobs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, timestamp FROM jobs ORDER BY id DESC")
    jobs = c.fetchall()
    conn.close()
    return jobs

def get_job_by_id(job_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, timestamp, input_csv, constraints, output_csv FROM jobs WHERE id=?", (job_id,))
    job = c.fetchone()
    conn.close()
    return job

def save_dispatch_routes(dispatch_routes, route_summary, products):
    """Save dispatch routes data to database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute("INSERT INTO dispatch_routes (timestamp, route_data, route_summary, products_data) VALUES (?, ?, ?, ?)",
              (timestamp, serialize_for_db(dispatch_routes), serialize_for_db(route_summary), serialize_for_db(products)))
    
    conn.commit()
    conn.close()
    return c.lastrowid

def get_latest_dispatch_routes():
    """Get the latest dispatch routes data."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM dispatch_routes ORDER BY id DESC LIMIT 1")
    result = c.fetchone()
    conn.close()
    
    if result:
        try:
            return {
                'id': result[0],
                'timestamp': result[1],
                'route_data': json.loads(result[2]) if result[2] else [],
                'route_summary': json.loads(result[3]) if result[3] else {},
                'products_data': json.loads(result[4]) if result[4] else []
            }
        except json.JSONDecodeError as e:
            print(f"Warning: Could not decode dispatch routes data: {e}")
            return None
    return None

def delete_job_by_id(job_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM jobs WHERE id=?", (job_id,))
    conn.commit()
    conn.close()

def init_drivers_vehicles_tables():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS drivers (
        id TEXT PRIMARY KEY,
        name TEXT,
        max_hours REAL,
        hourly_rate REAL,
        available INTEGER
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS vehicles (
        id TEXT PRIMARY KEY,
        capacity_weight REAL,
        capacity_volume REAL,
        fuel_efficiency REAL,
        operating_cost_per_km REAL,
        available INTEGER
    )''')
    conn.commit()
    conn.close()

def add_driver(driver):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO drivers (id, name, max_hours, hourly_rate, available) VALUES (?, ?, ?, ?, ?)",
              (driver['id'], driver['name'], driver['max_hours'], driver['hourly_rate'], int(driver.get('available', True))))
    conn.commit()
    conn.close()

def update_driver(driver):
    add_driver(driver)

def delete_driver(driver_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM drivers WHERE id=?", (driver_id,))
    conn.commit()
    conn.close()

def list_drivers():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, max_hours, hourly_rate, available FROM drivers")
    rows = c.fetchall()
    conn.close()
    return [
        {'id': r[0], 'name': r[1], 'max_hours': r[2], 'hourly_rate': r[3], 'available': bool(r[4])}
        for r in rows
    ]

def add_vehicle(vehicle):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO vehicles (id, capacity_weight, capacity_volume, fuel_efficiency, operating_cost_per_km, available) VALUES (?, ?, ?, ?, ?, ?)",
              (vehicle['id'], vehicle['capacity_weight'], vehicle['capacity_volume'], vehicle['fuel_efficiency'], vehicle['operating_cost_per_km'], int(vehicle.get('available', True))))
    conn.commit()
    conn.close()

def update_vehicle(vehicle):
    add_vehicle(vehicle)

def delete_vehicle(vehicle_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM vehicles WHERE id=?", (vehicle_id,))
    conn.commit()
    conn.close()

def list_vehicles():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, capacity_weight, capacity_volume, fuel_efficiency, operating_cost_per_km, available FROM vehicles")
    rows = c.fetchall()
    conn.close()
    return [
        {'id': r[0], 'capacity_weight': r[1], 'capacity_volume': r[2], 'fuel_efficiency': r[3], 'operating_cost_per_km': r[4], 'available': bool(r[5])}
        for r in rows
    ]

# Call in init_db
old_init_db = init_db
def init_db():
    old_init_db()
    init_drivers_vehicles_tables() 