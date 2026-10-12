import sqlite3
from app.core.database import engine, Base
import app.models  # load all models including IndustryLab, IndustryLabTask, IndustryLabAttempt


def create_retail_sandbox_tables(conn: sqlite3.Connection):
    cur = conn.cursor()

    # 1. Retail Customers
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lab_retail_customers (
        id INTEGER PRIMARY KEY,
        customer_name TEXT NOT NULL,
        segment TEXT NOT NULL,
        city TEXT NOT NULL,
        signup_date TEXT NOT NULL,
        active_status TEXT NOT NULL
    )
    """)

    # 2. Retail Products
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lab_retail_products (
        id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        cost_price REAL NOT NULL,
        list_price REAL NOT NULL
    )
    """)

    # 3. Retail Orders (note: some are CANCELLED/PENDING, some have edge cases)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lab_retail_orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date TEXT NOT NULL,
        total_amount REAL NOT NULL,
        payment_status TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES lab_retail_customers(id)
    )
    """)

    # 4. Retail Order Items
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lab_retail_order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        discount REAL DEFAULT 0.0,
        FOREIGN KEY (order_id) REFERENCES lab_retail_orders(id),
        FOREIGN KEY (product_id) REFERENCES lab_retail_products(id)
    )
    """)

    # 5. Retail Returns (only some orders have returns; requires LEFT JOIN)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lab_retail_returns (
        id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        return_date TEXT NOT NULL,
        return_reason TEXT NOT NULL,
        refund_amount REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES lab_retail_orders(id)
    )
    """)

    # Seed Retail Data if empty
    cur.execute("SELECT COUNT(*) FROM lab_retail_customers")
    if cur.fetchone()[0] == 0:
        customers = [
            (1, "Acro Corp", "Enterprise", "New York", "2024-01-15", "ACTIVE"),
            (2, "Apex Logistics", "Enterprise", "Chicago", "2024-02-10", "ACTIVE"),
            (3, "BrightPath Tech", "Mid-Market", "Austin", "2024-03-05", "ACTIVE"),
            (4, "Crestview Media", "Mid-Market", "Seattle", "2024-03-22", "ACTIVE"),
            (5, "Delta Dynamics", "SMB", "Denver", "2024-04-01", "ACTIVE"),
            (6, "Echo Ventures", "SMB", "San Francisco", "2024-04-18", "ACTIVE"),
            (7, "Flux Studios", "SMB", "Boston", "2024-05-12", "ACTIVE"),
            (8, "GreenLeaf Retail", "Mid-Market", "Atlanta", "2024-06-01", "INACTIVE"),
            (9, "Helix Biotech", "Enterprise", "San Diego", "2024-06-15", "ACTIVE"),
            (10, "Innova Labs", "SMB", "Miami", "2024-07-01", "ACTIVE"),
        ]
        cur.executemany("INSERT INTO lab_retail_customers VALUES (?, ?, ?, ?, ?, ?)", customers)

        products = [
            (101, "Data Analytics Suite Pro", "Software", 120.0, 499.0),
            (102, "Cloud Data Pipeline Hub", "Software", 250.0, 899.0),
            (103, "Enterprise BI Dashboard Connector", "Software", 80.0, 299.0),
            (104, "Server Edge Node 16GB", "Hardware", 400.0, 750.0),
            (105, "Secure Hardware Key Yubi", "Hardware", 15.0, 55.0),
            (106, "Priority Technical Support SLA", "Services", 50.0, 200.0),
        ]
        cur.executemany("INSERT INTO lab_retail_products VALUES (?, ?, ?, ?, ?)", products)

        # Orders: some CANCELLED, some COMPLETED
        orders = [
            (1001, 1, "2024-07-10", 1797.0, "COMPLETED"),
            (1002, 1, "2024-08-01", 899.0, "COMPLETED"),
            (1003, 2, "2024-07-12", 2250.0, "COMPLETED"),
            (1004, 2, "2024-08-15", 499.0, "COMPLETED"),
            (1005, 3, "2024-07-15", 1498.0, "COMPLETED"),
            (1006, 3, "2024-08-20", 598.0, "COMPLETED"),
            (1007, 4, "2024-07-18", 1249.0, "COMPLETED"),
            (1008, 4, "2024-08-22", 899.0, "CANCELLED"),  # Edge case: CANCELLED
            (1009, 5, "2024-07-25", 854.0, "COMPLETED"),
            (1010, 5, "2024-08-28", 299.0, "COMPLETED"),
            (1011, 6, "2024-08-02", 554.0, "COMPLETED"),
            (1012, 6, "2024-08-30", 499.0, "PENDING"),    # Edge case: PENDING
            (1013, 7, "2024-08-05", 255.0, "COMPLETED"),
            (1014, 9, "2024-08-10", 3596.0, "COMPLETED"),
            (1015, 10, "2024-08-14", 299.0, "COMPLETED"),
        ]
        cur.executemany("INSERT INTO lab_retail_orders VALUES (?, ?, ?, ?, ?)", orders)

        # Order Items
        order_items = [
            (1, 1001, 101, 2, 499.0, 0.0),
            (2, 1001, 104, 1, 750.0, 0.0),
            (3, 1002, 102, 1, 899.0, 0.0),
            (4, 1003, 104, 3, 750.0, 0.0),
            (5, 1004, 101, 1, 499.0, 0.0),
            (6, 1005, 104, 1, 750.0, 0.0),
            (7, 1005, 104, 1, 750.0, 0.0),
            (8, 1006, 103, 2, 299.0, 0.0),
            (9, 1007, 102, 1, 899.0, 0.0),
            (10, 1007, 105, 5, 55.0, 0.0),
            (11, 1009, 104, 1, 750.0, 0.0),
            (12, 1010, 103, 1, 299.0, 0.0),
            (13, 1011, 101, 1, 499.0, 0.0),
            (14, 1013, 105, 4, 55.0, 0.0),
            (15, 1014, 102, 4, 899.0, 0.0),
            (16, 1015, 103, 1, 299.0, 0.0),
        ]
        cur.executemany("INSERT INTO lab_retail_order_items VALUES (?, ?, ?, ?, ?, ?)", order_items)

        # Returns: only 3 orders have returns (requiring LEFT JOIN so orders without returns are kept)
        returns = [
            (1, 1002, "2024-08-05", "Defective configuration", 899.0),
            (2, 1006, "2024-08-25", "Customer dissatisfaction", 299.0),
            (3, 1011, "2024-08-10", "Billing dispute", 499.0),
        ]
        cur.executemany("INSERT INTO lab_retail_returns VALUES (?, ?, ?, ?, ?)", returns)

    conn.commit()


def migrate():
    # 1. Create ORM tables (industry_labs, industry_lab_tasks, industry_lab_attempts)
    Base.metadata.create_all(bind=engine)
    print("ORM tables created successfully.")

    # 2. Populate retail sandbox dataset tables
    con = sqlite3.connect("skillpath.db")
    create_retail_sandbox_tables(con)
    print("Retail sandbox tables and datasets seeded.")

    tables = [t[0] for t in con.cursor().execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print("Current tables:", tables)
    con.close()


if __name__ == "__main__":
    migrate()
