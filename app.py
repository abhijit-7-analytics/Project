from flask import Flask, jsonify, request, send_from_directory, session, make_response
from flask_cors import CORS
from datetime import timedelta, datetime
import psycopg2, psycopg2.extras, os, functools, io

app = Flask(__name__, static_folder=".")
CORS(app, supports_credentials=True)

app.secret_key = os.getenv("SECRET_KEY", "salesdb-secret-2024")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")

COMPANY = {
    "name": "SalesDB Pvt. Ltd.",
    "address": "Kendrapara, Odisha",
    "pin": "754289",
    "phone": "+91 7205109609",
    "email": "sales@salesdb.com",
    "gst": "21XXXXX1234X1ZX",
}
TAX_RATE = 0.18

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "sales_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "Abhi@4321"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "connect_timeout": 5,
}

def get_conn():
    try: return psycopg2.connect(**DB_CONFIG)
    except psycopg2.OperationalError as e: raise RuntimeError(f"DB Error: {e}") from e

def dc(conn): return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

def login_required(f):
    @functools.wraps(f)
    def w(*a, **k):
        if not session.get("admin"): return jsonify({"error": "Auth required"}), 401
        return f(*a, **k)
    return w

@app.errorhandler(404)
def e404(e): return jsonify({"error": "Not found"}), 404
@app.errorhandler(500)
def e500(e): return jsonify({"error": str(e)}), 500

@app.route("/")
def index(): return send_from_directory(".", "index.html")
@app.route("/styles.css")
def css(): return send_from_directory(".", "styles.css")
@app.route("/script.js")
def js(): return send_from_directory(".", "script.js")

# ═══ AUTH ═══
@app.route("/api/auth/check")
def auth_check(): return jsonify({"authenticated": bool(session.get("admin"))})

@app.route("/api/login", methods=["POST"])
def do_login():
    d = request.get_json(force=True)
    if d.get("username","").strip() == ADMIN_USER and d.get("password","") == ADMIN_PASS:
        session.permanent = True; session["admin"] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route("/api/logout", methods=["POST"])
def do_logout(): session.clear(); return jsonify({"success": True})

@app.route("/api/health")
def health():
    try: c=get_conn(); c.close(); return jsonify({"status":"ok"})
    except: return jsonify({"status":"error"}), 503

# ═══ ANALYTICS ═══
@app.route("/api/analytics/revenue-by-category")
def rev_cat():
    try:
        conn=get_conn()
        with dc(conn) as cur:
            cur.execute("SELECT pd.category,SUM(sf.sale_amount)::float AS total_revenue FROM sales_fact sf JOIN product_dim pd ON sf.product_id=pd.product_id GROUP BY pd.category ORDER BY total_revenue DESC;")
            rows=cur.fetchall()
        conn.close(); return jsonify([dict(r) for r in rows])
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/analytics/kpis")
def kpis():
    try:
        conn=get_conn()
        with dc(conn) as cur:
            cur.execute("SELECT COUNT(*)::int AS total_sales,COALESCE(SUM(sale_amount),0)::float AS total_revenue,COALESCE(AVG(sale_amount),0)::float AS avg_order_value,(SELECT COUNT(*) FROM customer_dim)::int AS total_customers,(SELECT COUNT(*) FROM product_dim)::int AS total_products FROM sales_fact;")
            row=dict(cur.fetchone())
            cur.execute("SELECT COUNT(*)::int AS cnt FROM product_dim WHERE COALESCE(stock_qty,0)>0 AND COALESCE(stock_qty,0)<=10;")
            row["low_stock_count"]=cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*)::int AS cnt FROM product_dim WHERE COALESCE(stock_qty,0)<=0;")
            row["out_stock_count"]=cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*)::int AS cnt FROM invoice_fact WHERE status='Pending';")
            row["pending_invoices"]=cur.fetchone()["cnt"]
        conn.close(); return jsonify(row)
    except Exception as e: return jsonify({"error":str(e)}),500

# ═══ CUSTOMERS ═══
@app.route("/api/customers",methods=["GET"])
def get_cust():
    try:
        conn=get_conn()
        with dc(conn) as cur: cur.execute("SELECT * FROM customer_dim ORDER BY customer_id;"); rows=cur.fetchall()
        conn.close(); return jsonify([dict(r) for r in rows])
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/customers",methods=["POST"])
@login_required
def add_cust():
    try:
        d=request.get_json(force=True)
        if not d.get("first_name") or not d.get("last_name"): return jsonify({"error":"Name required"}),400
        conn=get_conn()
        with dc(conn) as cur:
            cur.execute("INSERT INTO customer_dim(first_name,last_name,city,mobile_no,email,region,member_type) VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING *;",
                (d["first_name"],d["last_name"],d.get("city"),d.get("mobile_no"),d.get("email"),d.get("region"),d.get("member_type","Regular")))
            row=cur.fetchone()
        conn.commit(); conn.close(); return jsonify(dict(row)),201
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/customers/<int:cid>",methods=["PUT"])
@login_required
def upd_cust(cid):
    try:
        d=request.get_json(force=True); conn=get_conn()
        with dc(conn) as cur:
            cur.execute("UPDATE customer_dim SET first_name=%s,last_name=%s,city=%s,mobile_no=%s,email=%s,region=%s,member_type=%s WHERE customer_id=%s RETURNING *;",
                (d["first_name"],d["last_name"],d.get("city"),d.get("mobile_no"),d.get("email"),d.get("region"),d.get("member_type","Regular"),cid))
            row=cur.fetchone()
        conn.commit(); conn.close()
        if not row: return jsonify({"error":"Not found"}),404
        return jsonify(dict(row))
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/customers/<int:cid>",methods=["DELETE"])
@login_required
def del_cust(cid):
    try:
        conn=get_conn()
        with conn.cursor() as cur: cur.execute("DELETE FROM customer_dim WHERE customer_id=%s;",(cid,))
        conn.commit(); conn.close(); return jsonify({"deleted":cid})
    except Exception as e: return jsonify({"error":str(e)}),500

# ═══ PRODUCTS ═══
@app.route("/api/products",methods=["GET"])
def get_prod():
    try:
        conn=get_conn()
        with dc(conn) as cur: cur.execute("SELECT * FROM product_dim ORDER BY product_id;"); rows=cur.fetchall()
        conn.close()
        return jsonify([{**dict(r),"unit_price":float(r.get("unit_price") or 0),"stock_qty":int(r.get("stock_qty") or 0)} for r in rows])
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/products",methods=["POST"])
@login_required
def add_prod():
    try:
        d=request.get_json(force=True)
        if not d.get("product_name"): return jsonify({"error":"Name required"}),400
        conn=get_conn()
        with dc(conn) as cur:
            cur.execute("INSERT INTO product_dim(product_name,category,unit_price,stock_qty) VALUES(%s,%s,%s,%s) RETURNING *;",
                (d["product_name"],d.get("category"),d.get("unit_price",0),d.get("stock_qty",0)))
            row=cur.fetchone()
        conn.commit(); conn.close()
        r=dict(row); r["unit_price"]=float(r.get("unit_price") or 0); r["stock_qty"]=int(r.get("stock_qty") or 0)
        return jsonify(r),201
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/products/<int:pid>",methods=["PUT"])
@login_required
def upd_prod(pid):
    try:
        d=request.get_json(force=True); conn=get_conn()
        with dc(conn) as cur:
            cur.execute("UPDATE product_dim SET product_name=%s,category=%s,unit_price=%s,stock_qty=%s WHERE product_id=%s RETURNING *;",
                (d["product_name"],d.get("category"),d.get("unit_price",0),d.get("stock_qty",0),pid))
            row=cur.fetchone()
        conn.commit(); conn.close()
        if not row: return jsonify({"error":"Not found"}),404
        r=dict(row); r["unit_price"]=float(r.get("unit_price") or 0); r["stock_qty"]=int(r.get("stock_qty") or 0)
        return jsonify(r)
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/products/<int:pid>",methods=["DELETE"])
@login_required
def del_prod(pid):
    try:
        conn=get_conn()
        with conn.cursor() as cur: cur.execute("DELETE FROM product_dim WHERE product_id=%s;",(pid,))
        conn.commit(); conn.close(); return jsonify({"deleted":pid})
    except Exception as e: return jsonify({"error":str(e)}),500

# ═══ STOCKS ═══
@app.route("/api/stocks/restock",methods=["POST"])
@login_required
def restock():
    try:
        d=request.get_json(force=True)
        pid=d.get("product_id"); qty=d.get("quantity",0)
        if not pid or qty<=0: return jsonify({"error":"Valid product and qty required"}),400
        conn=get_conn()
        with dc(conn) as cur:
            cur.execute("UPDATE product_dim SET stock_qty=COALESCE(stock_qty,0)+%s WHERE product_id=%s RETURNING product_name,stock_qty;",(qty,pid))
            row=cur.fetchone()
            if not row: conn.close(); return jsonify({"error":"Product not found"}),404
            # Log stock change
            cur.execute("INSERT INTO stock_history(product_id,change_type,qty_change,new_stock) VALUES(%s,%s,%s,%s);",
                (pid,'RESTOCK',qty,row["stock_qty"]))
        conn.commit(); conn.close()
        return jsonify({"product":row["product_name"],"new_stock":int(row["stock_qty"])})
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/stocks/history")
@login_required
def stock_history():
    try:
        conn=get_conn()
        with dc(conn) as cur:
            cur.execute("""SELECT sh.*, pd.product_name, sh.created_at::text
                FROM stock_history sh JOIN product_dim pd ON sh.product_id=pd.product_id
                ORDER BY sh.history_id DESC LIMIT 50;""")
            rows=cur.fetchall()
        conn.close(); return jsonify([dict(r) for r in rows])
    except Exception as e: return jsonify([])  # Table may not exist yet

# ═══ SALES ═══
@app.route("/api/sales",methods=["GET"])
def get_sales():
    try:
        conn=get_conn()
        with dc(conn) as cur:
            cur.execute("""SELECT sf.sale_id,c.first_name||' '||c.last_name AS customer_name,
                pd.product_name,pd.category,COALESCE(pd.unit_price,0)::float AS unit_price,
                sf.sale_date::text,sf.quantity,sf.sale_amount::float,inv.invoice_no
                FROM sales_fact sf JOIN customer_dim c ON sf.customer_id=c.customer_id
                JOIN product_dim pd ON sf.product_id=pd.product_id
                LEFT JOIN invoice_fact inv ON sf.sale_id=inv.sale_id
                ORDER BY sf.sale_date DESC,sf.sale_id DESC;""")
            rows=cur.fetchall()
        conn.close(); return jsonify([dict(r) for r in rows])
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/sales",methods=["POST"])
@login_required
def add_sale():
    try:
        d=request.get_json(force=True)
        required=["customer_id","product_id","sale_date","quantity","sale_amount"]
        missing=[f for f in required if f not in d]
        if missing: return jsonify({"error":f"Missing: {missing}"}),400
        conn=get_conn()
        with dc(conn) as cur:
            cur.execute("SELECT stock_qty,product_name FROM product_dim WHERE product_id=%s;",(d["product_id"],))
            prod=cur.fetchone()
            if not prod: return jsonify({"error":"Product not found"}),404
            if (prod["stock_qty"] or 0)<d["quantity"]:
                return jsonify({"error":f"Insufficient stock for {prod['product_name']}. Available: {prod['stock_qty'] or 0}"}),400
            cur.execute("INSERT INTO sales_fact(customer_id,product_id,sale_date,quantity,sale_amount) VALUES(%s,%s,%s,%s,%s) RETURNING sale_id;",
                (d["customer_id"],d["product_id"],d["sale_date"],d["quantity"],d["sale_amount"]))
            sale_id=cur.fetchone()["sale_id"]
            # Deduct stock
            cur.execute("UPDATE product_dim SET stock_qty=stock_qty-%s WHERE product_id=%s RETURNING stock_qty;",(d["quantity"],d["product_id"]))
            new_stock=cur.fetchone()["stock_qty"]
            # Log stock change
            cur.execute("INSERT INTO stock_history(product_id,change_type,qty_change,new_stock) VALUES(%s,%s,%s,%s);",
                (d["product_id"],'SALE',-d["quantity"],new_stock))
            # Invoice
            sub=float(d["sale_amount"]); tax=round(sub*TAX_RATE,2); grand=round(sub+tax,2)
            inv_no=f"INV-{datetime.now().strftime('%Y')}-{sale_id:05d}"
            cur.execute("INSERT INTO invoice_fact(sale_id,invoice_no,subtotal,tax_rate,tax_amount,grand_total,status) VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING invoice_id;",
                (sale_id,inv_no,sub,TAX_RATE*100,tax,grand,'Pending'))
            inv_id=cur.fetchone()["invoice_id"]
        conn.commit(); conn.close()
        return jsonify({"sale_id":sale_id,"invoice_no":inv_no,"invoice_id":inv_id}),201
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/sales/<int:sid>",methods=["DELETE"])
@login_required
def del_sale(sid):
    try:
        conn=get_conn()
        with dc(conn) as cur:
            cur.execute("SELECT product_id,quantity FROM sales_fact WHERE sale_id=%s;",(sid,))
            sale=cur.fetchone()
            if sale:
                cur.execute("UPDATE product_dim SET stock_qty=stock_qty+%s WHERE product_id=%s RETURNING stock_qty;",(sale["quantity"],sale["product_id"]))
                new_stock=cur.fetchone()["stock_qty"]
                cur.execute("INSERT INTO stock_history(product_id,change_type,qty_change,new_stock) VALUES(%s,%s,%s,%s);",
                    (sale["product_id"],'RETURN',sale["quantity"],new_stock))
            cur.execute("DELETE FROM sales_fact WHERE sale_id=%s;",(sid,))
        conn.commit(); conn.close(); return jsonify({"deleted":sid})
    except Exception as e: return jsonify({"error":str(e)}),500

# ═══ CUSTOMER SALES (for invoice builder auto-fill) ═══
@app.route("/api/customers/<int:cid>/sales", methods=["GET"])
@login_required
def cust_sales(cid):
    """Return all sales for a customer so the invoice builder can pre-fill line items."""
    try:
        conn = get_conn()
        with dc(conn) as cur:
            cur.execute("""
                SELECT sf.sale_id, pd.product_name AS description,
                       COALESCE(pd.unit_price,0)::float AS unit_price,
                       sf.quantity AS qty,
                       sf.sale_amount::float AS amount,
                       sf.sale_date::text,
                       pd.category,
                       inv.invoice_no
                FROM sales_fact sf
                JOIN product_dim pd ON sf.product_id = pd.product_id
                LEFT JOIN invoice_fact inv ON sf.sale_id = inv.sale_id
                WHERE sf.customer_id = %s
                ORDER BY sf.sale_date DESC, sf.sale_id DESC;
            """, (cid,))
            rows = cur.fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══ INVOICE PDF BUILDER (shared helper) ═══
def _build_invoice_pdf(buf, inv_no, customer, items, subtotal, tax_rate, tax_amount, grand_total, notes=""):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor, white
    from reportlab.pdfgen import canvas as pdf_canvas

    c = pdf_canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    purple  = HexColor('#7c3aed')
    lp      = HexColor('#f3f0ff')
    dk      = HexColor('#1e293b')
    mt      = HexColor('#64748b')
    gn      = HexColor('#059669')
    lineClr = HexColor('#e2e8f0')

    # Header band
    c.setFillColor(lp); c.rect(0, h-125, w, 125, fill=True, stroke=False)
    c.setFillColor(dk); c.setFont("Helvetica-Bold", 15); c.drawString(40, h-42, COMPANY["name"])
    c.setFont("Helvetica", 8.5); c.setFillColor(mt)
    c.drawString(40, h-56,  f"Address : Kendrapara, Odisha, PIN {COMPANY['pin']}")
    c.drawString(40, h-69,  f"Phone   : {COMPANY['phone']}")
    c.drawString(40, h-82,  f"Email   : {COMPANY['email']}")
    c.drawString(40, h-95,  f"GSTIN   : {COMPANY['gst']}")

    # Logo box — sidebar style (pink→purple gradient, white text, Syne-equivalent bold)
    from reportlab.lib.colors import linearlyInterpolatedColor
    pink   = HexColor('#be185d')
    grad_r = HexColor('#7c3aed')
    # Draw gradient by stacking thin horizontal slices
    box_x, box_y, box_w, box_h = w-172, h-112, 132, 62
    steps = 30
    for i in range(steps):
        t   = i / steps
        r   = int(pink.red*255   + (grad_r.red*255   - pink.red*255)   * t)
        g_c = int(pink.green*255 + (grad_r.green*255 - pink.green*255) * t)
        b   = int(pink.blue*255  + (grad_r.blue*255  - pink.blue*255)  * t)
        slice_color = HexColor('#{:02x}{:02x}{:02x}'.format(
            max(0,min(255,r)), max(0,min(255,g_c)), max(0,min(255,b))))
        slice_y = box_y + (box_h / steps) * i
        slice_h = box_h / steps + 1
        c.setFillColor(slice_color); c.setStrokeColor(slice_color)
        c.rect(box_x, slice_y, box_w, slice_h, fill=True, stroke=False)
    # Rounded border overlay
    c.setStrokeColor(HexColor('#9333ea')); c.setLineWidth(0); c.setFillColor(HexColor('#9333ea00'))
    c.roundRect(box_x, box_y, box_w, box_h, 8, fill=False, stroke=False)
    # Text: "SalesDB" bold white
    c.setFillColor(white); c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(box_x + box_w/2, box_y + box_h - 24, "SalesDB")
    # Subtext: "Analytics"
    c.setFont("Helvetica", 8); c.setFillColor(HexColor('#fce7f3'))
    c.drawCentredString(box_x + box_w/2, box_y + 10, "Analytics")

    # Title
    c.setFillColor(purple); c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(w/2, h-155, "INVOICE")

    # Bill To
    y = h-198
    c.setFillColor(purple); c.setFont("Helvetica-Bold", 10); c.drawString(40, y, "Bill To")
    c.setFont("Helvetica-Bold", 10); c.setFillColor(dk)
    c.drawString(40, y-18, f"{customer.get('first_name','')} {customer.get('last_name','')}")
    c.setFont("Helvetica", 9); c.setFillColor(mt)
    c.drawString(40, y-32, f"City   : {customer.get('city','—')}")
    c.drawString(40, y-45, f"Mobile : {customer.get('mobile_no','—')}")
    c.drawString(40, y-58, f"Email  : {customer.get('email','—')}")
    c.drawString(40, y-71, f"Region : {customer.get('region','—')}")

    # Invoice meta
    rx = 330
    today = datetime.now(); due = today + timedelta(days=14)
    meta_labels = ["Invoice #", "Invoice Date", "Due Date", "Status"]
    meta_values = [inv_no, today.strftime("%d-%m-%Y"), due.strftime("%d-%m-%Y"), "Pending"]
    c.setFillColor(purple); c.setFont("Helvetica-Bold", 9)
    for i, lbl in enumerate(meta_labels): c.drawString(rx, y - i*18, lbl)
    c.setFont("Helvetica", 9)
    for i, v in enumerate(meta_values[:-1]):
        c.setFillColor(dk); c.drawString(rx+115, y - i*18, v)
    c.setFillColor(gn); c.drawString(rx+115, y-54, meta_values[-1])

    # Items table
    th = y-110
    c.setFillColor(purple); c.rect(35, th-2, w-70, 22, fill=True, stroke=False)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 9)
    cols = [45, 105, 310, 400, 470]
    hdrs = ["#", "Description", "Unit Price", "Qty", "Amount"]
    for cx, hdr in zip(cols, hdrs): c.drawString(cx, th+4, hdr)

    row_y = th - 22
    c.setFont("Helvetica", 9)
    for idx, item in enumerate(items):
        bg = HexColor('#faf5ff') if idx % 2 == 0 else white
        c.setFillColor(bg); c.rect(35, row_y-4, w-70, 18, fill=True, stroke=False)
        c.setFillColor(dk)
        c.drawString(cols[0], row_y, str(idx+1))
        desc = str(item.get('description',''))[:40]
        c.drawString(cols[1], row_y, desc)
        c.drawString(cols[2], row_y, f"${float(item.get('unit_price',0)):.2f}")
        c.drawString(cols[3], row_y, str(item.get('qty',1)))
        c.drawString(cols[4], row_y, f"${float(item.get('amount',0)):.2f}")
        c.setStrokeColor(lineClr); c.setLineWidth(0.4)
        c.line(35, row_y-5, w-35, row_y-5)
        row_y -= 20

    # Totals
    ty = row_y - 22
    c.setFont("Helvetica", 10); c.setFillColor(mt)
    c.drawRightString(460, ty, "Subtotal")
    c.drawRightString(460, ty-20, f"GST ({tax_rate:.0f}%)")
    c.setFillColor(dk)
    c.drawRightString(w-40, ty, f"${subtotal:.2f}")
    c.drawRightString(w-40, ty-20, f"${tax_amount:.2f}")
    c.setStrokeColor(purple); c.setLineWidth(1.5); c.line(300, ty-35, w-35, ty-35)
    c.setFont("Helvetica-Bold", 12); c.setFillColor(purple)
    c.drawRightString(460, ty-55, "Total (USD)")
    c.setFillColor(dk); c.setFont("Helvetica-Bold", 15)
    c.drawRightString(w-40, ty-55, f"${grand_total:.2f}")

    # Notes
    if notes:
        ny = ty - 88
        c.setFont("Helvetica-Bold", 9); c.setFillColor(purple); c.drawString(40, ny, "Notes")
        c.setFont("Helvetica", 8.5); c.setFillColor(mt); c.drawString(40, ny-14, str(notes)[:100])

    # Terms
    tmy = 130
    c.setStrokeColor(lineClr); c.setLineWidth(0.5); c.line(40, tmy+22, w-40, tmy+22)
    c.setFillColor(purple); c.setFont("Helvetica-Bold", 10); c.drawString(40, tmy, "Terms and Conditions")
    c.setFont("Helvetica", 8); c.setFillColor(mt)
    c.drawString(40, tmy-16, "Payment is due within 14 days of invoice date.")
    c.drawString(40, tmy-30, f"Please make checks payable to: {COMPANY['name']}")
    c.drawString(40, tmy-44, f"Contact: {COMPANY['phone']}  |  {COMPANY['email']}")

    # Footer
    c.setFillColor(lp); c.rect(0, 0, w, 42, fill=True, stroke=False)
    c.setFillColor(mt); c.setFont("Helvetica", 7)
    c.drawCentredString(w/2, 16, f"Generated by SalesDB  |  {COMPANY['name']}  |  Kendrapara, Odisha  |  PIN {COMPANY['pin']}")
    c.save()


@app.route("/api/invoices/save", methods=["POST"])
@login_required
def save_invoice():
    """Save a standalone invoice to invoice_fact and link to sales_fact rows."""
    try:
        import random, string
        d = request.get_json(force=True)
        cid   = d.get("customer_id")
        items = d.get("items", [])   # each item has sale_id (optional), description, unit_price, qty, amount
        notes = d.get("notes", "")

        if not cid or not items:
            return jsonify({"error": "customer_id and items required"}), 400

        subtotal    = round(sum(float(i.get("amount", 0)) for i in items), 2)
        tax_amount  = round(subtotal * TAX_RATE, 2)
        grand_total = round(subtotal + tax_amount, 2)
        rand_suffix = ''.join(random.choices(string.digits, k=5))
        inv_no      = f"INV-{datetime.now().strftime('%Y%m')}-{rand_suffix}"

        conn = get_conn()
        with dc(conn) as cur:
            # Get customer for response
            cur.execute("SELECT * FROM customer_dim WHERE customer_id=%s;", (cid,))
            customer = dict(cur.fetchone() or {})

            # For each item that has a real sale_id, insert an invoice_fact row
            # For items without sale_id (manual rows), create a dummy sales row first
            inserted_inv_ids = []
            for item in items:
                sale_id = item.get("sale_id")
                if not sale_id:
                    # Create a placeholder sale row for this manual item
                    cur.execute("""
                        INSERT INTO sales_fact(customer_id, product_id, sale_date, quantity, sale_amount)
                        SELECT %s, product_id, CURRENT_DATE, %s, %s
                        FROM product_dim LIMIT 1
                        RETURNING sale_id;
                    """, (cid, int(item.get("qty", 1)), float(item.get("amount", 0))))
                    row = cur.fetchone()
                    sale_id = row["sale_id"] if row else None

                if sale_id:
                    # Check if invoice already exists for this sale
                    cur.execute("SELECT invoice_id FROM invoice_fact WHERE sale_id=%s;", (sale_id,))
                    existing = cur.fetchone()
                    if not existing:
                        item_sub   = float(item.get("amount", 0))
                        item_tax   = round(item_sub * TAX_RATE, 2)
                        item_grand = round(item_sub + item_tax, 2)
                        cur.execute("""
                            INSERT INTO invoice_fact(sale_id,invoice_no,subtotal,tax_rate,tax_amount,grand_total,status)
                            VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING invoice_id;
                        """, (sale_id, inv_no, item_sub, TAX_RATE*100, item_tax, item_grand, 'Pending'))
                        inserted_inv_ids.append(cur.fetchone()["invoice_id"])

        conn.commit(); conn.close()
        return jsonify({
            "success":     True,
            "invoice_no":  inv_no,
            "customer":    customer,
            "items":       items,
            "subtotal":    subtotal,
            "tax_rate":    TAX_RATE * 100,
            "tax_amount":  tax_amount,
            "grand_total": grand_total,
            "notes":       notes,
            "invoice_ids": inserted_inv_ids,
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/invoices/download-custom", methods=["POST"])
def download_custom_invoice():
    """Generate and download a PDF for a custom invoice payload."""
    try:
        d = request.get_json(force=True)
        buf = io.BytesIO()
        _build_invoice_pdf(
            buf,
            inv_no      = d["invoice_no"],
            customer    = d["customer"],
            items       = d["items"],
            subtotal    = float(d["subtotal"]),
            tax_rate    = float(d.get("tax_rate", 18)),
            tax_amount  = float(d["tax_amount"]),
            grand_total = float(d["grand_total"]),
            notes       = d.get("notes", ""),
        )
        buf.seek(0)
        resp = make_response(buf.getvalue())
        resp.headers['Content-Type']        = 'application/pdf'
        resp.headers['Content-Disposition'] = f'attachment; filename={d["invoice_no"]}.pdf'
        return resp
    except ImportError:
        return jsonify({"error": "pip install reportlab"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══ INVOICES ═══
@app.route("/api/invoices",methods=["GET"])
@login_required
def get_inv():
    try:
        conn=get_conn()
        with dc(conn) as cur:
            cur.execute("""SELECT inv.*,c.first_name||' '||c.last_name AS customer_name,
                c.city,c.mobile_no,c.email,c.region,pd.product_name,pd.category,
                sf.sale_date::text,sf.quantity,COALESCE(pd.unit_price,0)::float AS unit_price,sf.sale_amount::float
                FROM invoice_fact inv JOIN sales_fact sf ON inv.sale_id=sf.sale_id
                JOIN customer_dim c ON sf.customer_id=c.customer_id
                JOIN product_dim pd ON sf.product_id=pd.product_id ORDER BY inv.invoice_id DESC;""")
            rows=cur.fetchall()
        conn.close()
        result=[]
        for r in rows:
            d=dict(r)
            for k in ['subtotal','tax_amount','grand_total','unit_price','sale_amount']:
                if k in d: d[k]=float(d[k] or 0)
            result.append(d)
        return jsonify(result)
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/invoices/<int:iid>/status",methods=["PUT"])
@login_required
def upd_inv_status(iid):
    try:
        d=request.get_json(force=True); conn=get_conn()
        with dc(conn) as cur:
            cur.execute("UPDATE invoice_fact SET status=%s WHERE invoice_id=%s RETURNING *;",(d.get("status","Pending"),iid))
            row=cur.fetchone()
        conn.commit(); conn.close()
        if not row: return jsonify({"error":"Not found"}),404
        return jsonify(dict(row))
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/invoices/<int:iid>/download")
def dl_inv(iid):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.colors import HexColor, white
        from reportlab.pdfgen import canvas as pdf_canvas

        conn=get_conn()
        with dc(conn) as cur:
            cur.execute("""SELECT inv.*,c.first_name,c.last_name,c.city,c.mobile_no,c.email,c.region,
                pd.product_name,pd.category,COALESCE(pd.unit_price,0)::float AS unit_price,
                sf.sale_date::text,sf.quantity,sf.sale_amount::float
                FROM invoice_fact inv JOIN sales_fact sf ON inv.sale_id=sf.sale_id
                JOIN customer_dim c ON sf.customer_id=c.customer_id
                JOIN product_dim pd ON sf.product_id=pd.product_id WHERE inv.invoice_id=%s;""",(iid,))
            inv=cur.fetchone()
        conn.close()
        if not inv: return jsonify({"error":"Not found"}),404
        inv=dict(inv)
        for k in ['subtotal','tax_amount','grand_total','unit_price','sale_amount']:
            if k in inv: inv[k]=float(inv[k] or 0)

        buf=io.BytesIO(); c=pdf_canvas.Canvas(buf,pagesize=A4); w,h=A4
        purple=HexColor('#7c3aed'); lp=HexColor('#f3f0ff'); dk=HexColor('#1e293b'); mt=HexColor('#64748b'); gn=HexColor('#059669')

        c.setFillColor(lp); c.rect(0,h-120,w,120,fill=True,stroke=False)
        c.setFillColor(dk); c.setFont("Helvetica-Bold",16); c.drawString(40,h-45,COMPANY["name"])
        c.setFont("Helvetica",9); c.setFillColor(mt)
        c.drawString(40,h-60,f"{COMPANY['address']}, PIN: {COMPANY['pin']}")
        c.drawString(40,h-73,f"Phone: {COMPANY['phone']} | Email: {COMPANY['email']}")
        c.drawString(40,h-86,f"GSTIN: {COMPANY['gst']}")

        # Logo box — sidebar style (pink→purple gradient, white text)
        pink2   = HexColor('#be185d')
        grad_r2 = HexColor('#7c3aed')
        bx, by, bw, bh = w-170, h-108, 130, 60
        steps2 = 30
        for i in range(steps2):
            t2    = i / steps2
            r2    = int(pink2.red*255   + (grad_r2.red*255   - pink2.red*255)   * t2)
            g2    = int(pink2.green*255 + (grad_r2.green*255 - pink2.green*255) * t2)
            b2    = int(pink2.blue*255  + (grad_r2.blue*255  - pink2.blue*255)  * t2)
            sc2   = HexColor('#{:02x}{:02x}{:02x}'.format(
                max(0,min(255,r2)), max(0,min(255,g2)), max(0,min(255,b2))))
            sy2   = by + (bh / steps2) * i
            sh2   = bh / steps2 + 1
            c.setFillColor(sc2); c.rect(bx, sy2, bw, sh2, fill=True, stroke=False)
        c.setFillColor(white); c.setFont("Helvetica-Bold",20)
        c.drawCentredString(bx+bw/2, by+bh-24, "SalesDB")
        c.setFont("Helvetica",8); c.setFillColor(HexColor('#fce7f3'))
        c.drawCentredString(bx+bw/2, by+10, "Analytics")

        c.setFillColor(purple); c.setFont("Helvetica-Bold",28); c.drawCentredString(w/2,h-145,"INVOICE")

        y=h-185
        c.setFillColor(purple); c.setFont("Helvetica-Bold",10); c.drawString(40,y,"Bill To")
        c.setFillColor(dk); c.setFont("Helvetica",10); c.drawString(40,y-18,f"{inv['first_name']} {inv['last_name']}")
        c.setFont("Helvetica",9); c.setFillColor(mt)
        c.drawString(40,y-33,f"City: {inv.get('city','--')}")
        c.drawString(40,y-46,f"Mobile: {inv.get('mobile_no','--')}")
        c.drawString(40,y-59,f"Email: {inv.get('email','--')}")
        c.drawString(40,y-72,f"Region: {inv.get('region','--')}")

        rx=320
        c.setFillColor(purple); c.setFont("Helvetica-Bold",10)
        c.drawString(rx,y,"Invoice #"); c.drawString(rx,y-18,"Date"); c.drawString(rx,y-36,"Status")
        c.setFillColor(dk); c.setFont("Helvetica",10)
        c.drawString(rx+110,y,inv['invoice_no']); c.drawString(rx+110,y-18,inv['sale_date'])
        c.setFillColor(gn if inv.get('status')=='Paid' else HexColor('#d97706'))
        c.drawString(rx+110,y-36,inv.get('status','Pending'))

        tt=y-100; cx=[40,100,300,420]; cl=['Qty','Description','Unit Price','Amount']
        c.setFillColor(purple); c.rect(35,tt-2,w-70,22,fill=True,stroke=False)
        c.setFillColor(white); c.setFont("Helvetica-Bold",9)
        for i,l in enumerate(cl): c.drawString(cx[i],tt+4,l)
        ry=tt-25
        c.setStrokeColor(HexColor('#e2e8f0')); c.setLineWidth(0.5); c.line(35,ry-5,w-35,ry-5)
        c.setFillColor(dk); c.setFont("Helvetica",9)
        c.drawString(cx[0],ry,str(inv['quantity']))
        c.drawString(cx[1],ry,f"{inv['product_name']} ({inv.get('category','--')})")
        c.drawString(cx[2],ry,f"${inv['unit_price']:.2f}")
        c.drawString(cx[3],ry,f"${inv['sale_amount']:.2f}")
        c.line(35,ry-25,w-35,ry-25)

        ty=ry-50
        c.setFont("Helvetica",10); c.setFillColor(mt); c.drawRightString(420,ty,"Subtotal")
        c.setFillColor(dk); c.drawRightString(w-40,ty,f"${inv['subtotal']:.2f}")
        c.setFillColor(mt); c.drawRightString(420,ty-20,f"GST ({inv.get('tax_rate',18):.0f}%)")
        c.setFillColor(dk); c.drawRightString(w-40,ty-20,f"${inv['tax_amount']:.2f}")
        c.setStrokeColor(purple); c.setLineWidth(1.5); c.line(300,ty-35,w-35,ty-35)
        c.setFont("Helvetica-Bold",12); c.setFillColor(purple); c.drawRightString(420,ty-55,"Total (USD)")
        c.setFillColor(dk); c.setFont("Helvetica-Bold",14); c.drawRightString(w-40,ty-55,f"${inv['grand_total']:.2f}")

        tmy=140
        c.setStrokeColor(HexColor('#e2e8f0')); c.setLineWidth(0.5); c.line(40,tmy+20,w-40,tmy+20)
        c.setFillColor(purple); c.setFont("Helvetica-Bold",10); c.drawString(40,tmy,"Terms and Conditions")
        c.setFillColor(mt); c.setFont("Helvetica",8)
        c.drawString(40,tmy-16,"Payment is due within 14 days.")
        c.drawString(40,tmy-30,f"Pay to: {COMPANY['name']}")
        c.drawString(40,tmy-44,f"Contact: {COMPANY['phone']} | {COMPANY['email']}")

        c.setFillColor(lp); c.rect(0,0,w,40,fill=True,stroke=False)
        c.setFillColor(mt); c.setFont("Helvetica",7)
        c.drawCentredString(w/2,16,f"Generated by SalesDB | {COMPANY['name']} | {COMPANY['address']}, {COMPANY['pin']}")

        c.save(); buf.seek(0)
        response=make_response(buf.getvalue())
        response.headers['Content-Type']='application/pdf'
        response.headers['Content-Disposition']=f'attachment; filename={inv["invoice_no"]}.pdf'
        return response
    except ImportError: return jsonify({"error":"pip install reportlab"}),500
    except Exception as e: return jsonify({"error":str(e)}),500

# ═══ REPORTS ═══
@app.route("/api/reports/sales")
@login_required
def rpt_sales():
    try:
        f=request.args.get('from'); t=request.args.get('to')
        cat=request.args.get('category'); reg=request.args.get('region')
        conds=[]; params=[]
        if f: conds.append("sf.sale_date>=%s"); params.append(f)
        if t: conds.append("sf.sale_date<=%s"); params.append(t)
        if cat: conds.append("pd.category=%s"); params.append(cat)
        if reg: conds.append("c.region=%s"); params.append(reg)
        where="WHERE "+" AND ".join(conds) if conds else ""
        conn=get_conn()
        with dc(conn) as cur:
            cur.execute(f"""SELECT sf.sale_id,c.first_name||' '||c.last_name AS customer_name,
                pd.product_name,pd.category,COALESCE(pd.unit_price,0)::float AS unit_price,
                sf.sale_date::text,sf.quantity,sf.sale_amount::float,c.region
                FROM sales_fact sf JOIN customer_dim c ON sf.customer_id=c.customer_id
                JOIN product_dim pd ON sf.product_id=pd.product_id {where}
                ORDER BY sf.sale_date DESC;""",params)
            records=[dict(r) for r in cur.fetchall()]
        conn.close()
        tr=sum(r["sale_amount"] for r in records); tc=len(records); av=tr/tc if tc else 0
        return jsonify({"records":records,"total_revenue":tr,"total_count":tc,"avg_order":av})
    except Exception as e: return jsonify({"error":str(e)}),500

# ═══ SETUP ═══
@app.route("/api/setup",methods=["POST"])
def setup():
    try:
        conn=get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS customer_dim(
                    customer_id SERIAL PRIMARY KEY,first_name VARCHAR(50) NOT NULL,last_name VARCHAR(50) NOT NULL,
                    city VARCHAR(50),mobile_no VARCHAR(20),email VARCHAR(100),region VARCHAR(20),
                    member_type VARCHAR(20) DEFAULT 'Regular');
                CREATE TABLE IF NOT EXISTS product_dim(
                    product_id SERIAL PRIMARY KEY,product_name VARCHAR(100) NOT NULL,
                    category VARCHAR(50),unit_price NUMERIC(10,2) DEFAULT 0,stock_qty INTEGER DEFAULT 0);
                CREATE TABLE IF NOT EXISTS sales_fact(
                    sale_id SERIAL PRIMARY KEY,
                    customer_id INTEGER REFERENCES customer_dim(customer_id) ON DELETE CASCADE,
                    product_id INTEGER REFERENCES product_dim(product_id) ON DELETE CASCADE,
                    sale_date DATE NOT NULL,quantity INTEGER NOT NULL,sale_amount NUMERIC(10,2) NOT NULL);
                CREATE TABLE IF NOT EXISTS invoice_fact(
                    invoice_id SERIAL PRIMARY KEY,
                    sale_id INTEGER REFERENCES sales_fact(sale_id) ON DELETE CASCADE,
                    invoice_no VARCHAR(30) UNIQUE NOT NULL,subtotal NUMERIC(10,2) NOT NULL,
                    tax_rate NUMERIC(5,2) DEFAULT 18,tax_amount NUMERIC(10,2) NOT NULL,
                    grand_total NUMERIC(10,2) NOT NULL,status VARCHAR(20) DEFAULT 'Pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS stock_history(
                    history_id SERIAL PRIMARY KEY,
                    product_id INTEGER REFERENCES product_dim(product_id) ON DELETE CASCADE,
                    change_type VARCHAR(20) NOT NULL,
                    qty_change INTEGER NOT NULL,
                    new_stock INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
                DO $$ BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='customer_dim' AND column_name='mobile_no') THEN ALTER TABLE customer_dim ADD COLUMN mobile_no VARCHAR(20); END IF;
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='customer_dim' AND column_name='email') THEN ALTER TABLE customer_dim ADD COLUMN email VARCHAR(100); END IF;
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='customer_dim' AND column_name='region') THEN ALTER TABLE customer_dim ADD COLUMN region VARCHAR(20); END IF;
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='customer_dim' AND column_name='member_type') THEN ALTER TABLE customer_dim ADD COLUMN member_type VARCHAR(20) DEFAULT 'Regular'; END IF;
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='product_dim' AND column_name='unit_price') THEN ALTER TABLE product_dim ADD COLUMN unit_price NUMERIC(10,2) DEFAULT 0; END IF;
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='product_dim' AND column_name='stock_qty') THEN ALTER TABLE product_dim ADD COLUMN stock_qty INTEGER DEFAULT 0; END IF;
                END $$;
            """)
        conn.commit(); conn.close()
        return jsonify({"status":"schema ready (5 tables: customer_dim, product_dim, sales_fact, invoice_fact, stock_history)"})
    except Exception as e: return jsonify({"error":str(e)}),500

if __name__=="__main__":
    print(f"\n  SalesDB API (Full: Stocks + Invoices + Reports)")
    print(f"  Admin: {ADMIN_USER} / {ADMIN_PASS}")
    print(f"  Dashboard → http://localhost:5000")
    print(f"  Setup DB  → POST http://localhost:5000/api/setup\n")
    app.run(debug=True,port=5000,host="0.0.0.0")