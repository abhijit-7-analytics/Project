from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__, static_folder=".")
CORS(app)

# ── Configuration ──────────────────────────────────────────────────────────
DB_CONFIG = {
    "dbname":   os.getenv("DB_NAME",     "sales_db"),
    "user":     os.getenv("DB_USER",     "postgres"),
    "password": os.getenv("DB_PASSWORD", "Abhi@4321"),
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     os.getenv("DB_PORT",     "5432"),
    "connect_timeout": 5,
}


def get_conn():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.OperationalError as e:
        raise RuntimeError(
            f"Cannot connect to PostgreSQL: {e}. "
            "Check DB_HOST / DB_USER / DB_PASSWORD / DB_NAME."
        ) from e


def dict_cursor(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


# ── Error handlers ─────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal(e):
    return jsonify({"error": str(e)}), 500


# ── Serve frontend files ──────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/styles.css")
def serve_css():
    return send_from_directory(".", "styles.css")

@app.route("/script.js")
def serve_js():
    return send_from_directory(".", "script.js")


# ── Health ─────────────────────────────────────────────────────────────────

@app.route("/api/health")
def health():
    try:
        conn = get_conn()
        conn.close()
        db_ok = True
        db_msg = "connected"
    except RuntimeError as e:
        db_ok = False
        db_msg = str(e)

    return jsonify({
        "status": "ok",
        "db_status": "ok" if db_ok else "error",
        "db_msg": db_msg,
    }), 200 if db_ok else 503


# ── Analytics ──────────────────────────────────────────────────────────────

@app.route("/api/analytics/revenue-by-category")
def revenue_by_category():
    try:
        conn = get_conn()
        with dict_cursor(conn) as cur:
            cur.execute("""
                SELECT pd.category,
                       SUM(sf.sale_amount)::float AS total_revenue
                FROM   sales_fact sf
                JOIN   product_dim pd ON sf.product_id = pd.product_id
                GROUP  BY pd.category
                ORDER  BY total_revenue DESC;
            """)
            rows = cur.fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/revenue-over-time")
def revenue_over_time():
    try:
        conn = get_conn()
        with dict_cursor(conn) as cur:
            cur.execute("""
                SELECT sale_date::text         AS sale_date,
                       SUM(sale_amount)::float AS daily_revenue
                FROM   sales_fact
                GROUP  BY sale_date
                ORDER  BY sale_date;
            """)
            rows = cur.fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/kpis")
def kpis():
    try:
        conn = get_conn()
        with dict_cursor(conn) as cur:
            cur.execute("""
                SELECT
                    COUNT(*)::int                            AS total_sales,
                    COALESCE(SUM(sale_amount),  0)::float   AS total_revenue,
                    COALESCE(AVG(sale_amount),  0)::float   AS avg_order_value,
                    (SELECT COUNT(*) FROM customer_dim)::int AS total_customers,
                    (SELECT COUNT(*) FROM product_dim)::int  AS total_products
                FROM sales_fact;
            """)
            row = cur.fetchone()
        conn.close()
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Customers ──────────────────────────────────────────────────────────────

@app.route("/api/customers", methods=["GET"])
def get_customers():
    try:
        conn = get_conn()
        with dict_cursor(conn) as cur:
            cur.execute("SELECT * FROM customer_dim ORDER BY customer_id;")
            rows = cur.fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/customers", methods=["POST"])
def add_customer():
    try:
        data = request.get_json(force=True)
        if not data.get("first_name") or not data.get("last_name"):
            return jsonify({"error": "first_name and last_name are required"}), 400
        conn = get_conn()
        with dict_cursor(conn) as cur:
            cur.execute(
                """INSERT INTO customer_dim
                       (first_name, last_name, city, mobile_no, email, region, member_type)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *;""",
                (
                    data["first_name"],
                    data["last_name"],
                    data.get("city"),
                    data.get("mobile_no"),
                    data.get("email"),
                    data.get("region"),
                    data.get("member_type", "Regular"),
                ),
            )
            row = cur.fetchone()
        conn.commit()
        conn.close()
        return jsonify(dict(row)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/customers/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    try:
        data = request.get_json(force=True)
        if not data.get("first_name") or not data.get("last_name"):
            return jsonify({"error": "first_name and last_name are required"}), 400
        conn = get_conn()
        with dict_cursor(conn) as cur:
            cur.execute(
                """UPDATE customer_dim
                   SET first_name  = %s,
                       last_name   = %s,
                       city        = %s,
                       mobile_no   = %s,
                       email       = %s,
                       region      = %s,
                       member_type = %s
                   WHERE customer_id = %s
                   RETURNING *;""",
                (
                    data["first_name"],
                    data["last_name"],
                    data.get("city"),
                    data.get("mobile_no"),
                    data.get("email"),
                    data.get("region"),
                    data.get("member_type", "Regular"),
                    customer_id,
                ),
            )
            row = cur.fetchone()
        conn.commit()
        conn.close()
        if row is None:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/customers/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM customer_dim WHERE customer_id = %s;", (customer_id,))
        conn.commit()
        conn.close()
        return jsonify({"deleted": customer_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Products ───────────────────────────────────────────────────────────────

@app.route("/api/products", methods=["GET"])
def get_products():
    try:
        conn = get_conn()
        with dict_cursor(conn) as cur:
            cur.execute("SELECT * FROM product_dim ORDER BY product_id;")
            rows = cur.fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/products", methods=["POST"])
def add_product():
    try:
        data = request.get_json(force=True)
        if not data.get("product_name"):
            return jsonify({"error": "product_name is required"}), 400
        conn = get_conn()
        with dict_cursor(conn) as cur:
            cur.execute(
                "INSERT INTO product_dim (product_name, category) VALUES (%s, %s) RETURNING *;",
                (data["product_name"], data.get("category")),
            )
            row = cur.fetchone()
        conn.commit()
        conn.close()
        return jsonify(dict(row)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    try:
        data = request.get_json(force=True)
        if not data.get("product_name"):
            return jsonify({"error": "product_name is required"}), 400
        conn = get_conn()
        with dict_cursor(conn) as cur:
            cur.execute(
                """UPDATE product_dim
                   SET product_name = %s,
                       category     = %s
                   WHERE product_id = %s
                   RETURNING *;""",
                (data["product_name"], data.get("category"), product_id),
            )
            row = cur.fetchone()
        conn.commit()
        conn.close()
        if row is None:
            return jsonify({"error": "Product not found"}), 404
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM product_dim WHERE product_id = %s;", (product_id,))
        conn.commit()
        conn.close()
        return jsonify({"deleted": product_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Sales ──────────────────────────────────────────────────────────────────

@app.route("/api/sales", methods=["GET"])
def get_sales():
    try:
        conn = get_conn()
        with dict_cursor(conn) as cur:
            cur.execute("""
                SELECT sf.sale_id,
                       c.first_name || ' ' || c.last_name AS customer_name,
                       pd.product_name,
                       pd.category,
                       sf.sale_date::text,
                       sf.quantity,
                       sf.sale_amount::float
                FROM   sales_fact sf
                JOIN   customer_dim c  ON sf.customer_id = c.customer_id
                JOIN   product_dim  pd ON sf.product_id  = pd.product_id
                ORDER  BY sf.sale_date DESC, sf.sale_id DESC;
            """)
            rows = cur.fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sales", methods=["POST"])
def add_sale():
    try:
        data = request.get_json(force=True)
        required = ["customer_id", "product_id", "sale_date", "quantity", "sale_amount"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {missing}"}), 400
        conn = get_conn()
        with dict_cursor(conn) as cur:
            cur.execute(
                """INSERT INTO sales_fact
                       (customer_id, product_id, sale_date, quantity, sale_amount)
                   VALUES (%s, %s, %s, %s, %s) RETURNING sale_id;""",
                (data["customer_id"], data["product_id"],
                 data["sale_date"], data["quantity"], data["sale_amount"]),
            )
            row = cur.fetchone()
        conn.commit()
        conn.close()
        return jsonify(dict(row)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sales/<int:sale_id>", methods=["DELETE"])
def delete_sale(sale_id):
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sales_fact WHERE sale_id = %s;", (sale_id,))
        conn.commit()
        conn.close()
        return jsonify({"deleted": sale_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Schema setup ───────────────────────────────────────────────────────────

@app.route("/api/setup", methods=["POST"])
def setup():
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS customer_dim (
                    customer_id  SERIAL PRIMARY KEY,
                    first_name   VARCHAR(50)  NOT NULL,
                    last_name    VARCHAR(50)  NOT NULL,
                    city         VARCHAR(50),
                    mobile_no    VARCHAR(20),
                    email        VARCHAR(100),
                    region       VARCHAR(20),
                    member_type  VARCHAR(20) DEFAULT 'Regular'
                );

                CREATE TABLE IF NOT EXISTS product_dim (
                    product_id   SERIAL PRIMARY KEY,
                    product_name VARCHAR(100) NOT NULL,
                    category     VARCHAR(50)
                );

                CREATE TABLE IF NOT EXISTS sales_fact (
                    sale_id     SERIAL PRIMARY KEY,
                    customer_id INTEGER REFERENCES customer_dim(customer_id) ON DELETE CASCADE,
                    product_id  INTEGER REFERENCES product_dim(product_id)  ON DELETE CASCADE,
                    sale_date   DATE           NOT NULL,
                    quantity    INTEGER        NOT NULL,
                    sale_amount NUMERIC(10, 2) NOT NULL
                );

                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='customer_dim' AND column_name='mobile_no'
                    ) THEN
                        ALTER TABLE customer_dim ADD COLUMN mobile_no VARCHAR(20);
                    END IF;

                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='customer_dim' AND column_name='email'
                    ) THEN
                        ALTER TABLE customer_dim ADD COLUMN email VARCHAR(100);
                    END IF;

                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='customer_dim' AND column_name='region'
                    ) THEN
                        ALTER TABLE customer_dim ADD COLUMN region VARCHAR(20);
                    END IF;

                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='customer_dim' AND column_name='member_type'
                    ) THEN
                        ALTER TABLE customer_dim ADD COLUMN member_type VARCHAR(20) DEFAULT 'Regular';
                    END IF;
                END
                $$;
            """)
        conn.commit()
        conn.close()
        return jsonify({"status": "schema ready"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  SalesDB API starting...")
    print("  Dashboard  →  http://localhost:5000")
    print("  Health     →  http://localhost:5000/api/health")
    print("  Setup DB   →  POST http://localhost:5000/api/setup\n")
    app.run(debug=True, port=5000, host="0.0.0.0")