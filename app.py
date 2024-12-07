from flask import Flask, jsonify, render_template
import pymysql

app = Flask(__name__)

# Global database connection
db = None

def get_db_connection():
    global db
    if db is None or not db.open:
        db = pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="Test123$",
            database="IMSProject",
            cursorclass=pymysql.cursors.DictCursor
        )
    return db

def execute_query(query):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            return results
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        return []

@app.route('/')
def home():
    return render_template('index.html')

# API Endpoints for Table Queries
@app.route('/api/sales/november2024', methods=['GET'])
def sales_november_2024():
    query = """
        SELECT s.sale_id, c.name as customer_name, s.date, s.total_amount
        FROM Sales s
        JOIN Customers c ON s.customer_id = c.customer_id
        WHERE MONTH(s.date) = 11 AND YEAR(s.date) = 2024
    """
    data = execute_query(query)
    return jsonify({"columns": ["sale_id", "customer_name", "date", "total_amount"], "data": data})

@app.route('/api/sales/comparison', methods=['GET'])
def sales_comparison():
    query = """
        SELECT YEAR(s.date) AS year, MONTH(s.date) AS month, SUM(s.total_amount) AS total_sales
        FROM Sales s
        WHERE MONTH(s.date) = 11
        GROUP BY YEAR(s.date), MONTH(s.date)
    """
    data = execute_query(query)
    return jsonify({"columns": ["year", "month", "total_sales"], "data": data})

@app.route('/api/sales/best-seller', methods=['GET'])
def best_seller():
    query = """
        SELECT p.product_id, p.name AS product_name, SUM(sd.quantity) AS total_quantity
        FROM SalesDetails sd
        JOIN Products p ON sd.product_id = p.product_id
        GROUP BY p.product_id
        ORDER BY total_quantity DESC
        LIMIT 1
    """
    data = execute_query(query)
    return jsonify({"columns": ["product_id", "product_name", "total_quantity"], "data": data})

@app.route('/api/sales/worst-seller', methods=['GET'])
def worst_seller():
    query = """
        SELECT p.product_id, p.name AS product_name, SUM(sd.quantity) AS total_quantity
        FROM SalesDetails sd
        JOIN Products p ON sd.product_id = p.product_id
        GROUP BY p.product_id
        ORDER BY total_quantity ASC
        LIMIT 1
    """
    data = execute_query(query)
    return jsonify({"columns": ["product_id", "product_name", "total_quantity"], "data": data})

@app.route('/api/vendors/profitable', methods=['GET'])
def most_profitable_vendor():
    query = """
        SELECT v.name AS vendor_name, SUM(sd.quantity * (p.selling_price - p.cost_price)) AS profit
        FROM SalesDetails sd
        JOIN Products p ON sd.product_id = p.product_id
        JOIN Vendors v ON p.vendor_id = v.vendor_id
        GROUP BY v.vendor_id
        ORDER BY profit DESC
        LIMIT 1
    """
    data = execute_query(query)
    return jsonify({"columns": ["vendor_name", "profit"], "data": data})

@app.route('/api/products/reorder', methods=['GET'])
def products_reorder():
    query = """
        SELECT product_id, name, quantity_in_stock, reorder_threshold
        FROM Products
        WHERE quantity_in_stock <= reorder_threshold
    """
    data = execute_query(query)
    return jsonify({"columns": ["product_id", "name", "quantity_in_stock", "reorder_threshold"], "data": data})

@app.route('/api/products/unsold', methods=['GET'])
def unsold_products():
    query = """
        SELECT p.product_id, p.name, p.quantity_in_stock
        FROM Products p
        LEFT JOIN SalesDetails sd ON p.product_id = sd.product_id
        LEFT JOIN Sales s ON sd.sale_id = s.sale_id
        WHERE s.date IS NULL OR s.date < CURDATE() - INTERVAL 3 MONTH
    """
    data = execute_query(query)
    return jsonify({"columns": ["product_id", "name", "quantity_in_stock"], "data": data})

@app.route('/api/sales/monthly-breakdown', methods=['GET'])
def monthly_sales():
    query = """
        SELECT YEAR(s.date) AS year, MONTH(s.date) AS month, SUM(s.total_amount) AS total_sales
        FROM Sales s
        GROUP BY YEAR(s.date), MONTH(s.date)
    """
    data = execute_query(query)
    return jsonify({"columns": ["year", "month", "total_sales"], "data": data})

@app.route('/api/customers/top-spenders', methods=['GET'])
def top_spenders():
    query = """
        SELECT c.customer_id, c.name, SUM(s.total_amount) AS total_spent
        FROM Customers c
        JOIN Sales s ON c.customer_id = s.customer_id
        GROUP BY c.customer_id
        ORDER BY total_spent DESC
        LIMIT 5
    """
    data = execute_query(query)
    return jsonify({"columns": ["customer_id", "name", "total_spent"], "data": data})

@app.route('/api/vendors/orders-analysis', methods=['GET'])
def vendor_orders_analysis():
    query = """
        SELECT v.name AS vendor_name, COUNT(vo.order_id) AS total_orders, vo.status
        FROM VendorOrders vo
        JOIN Vendors v ON vo.vendor_id = v.vendor_id
        GROUP BY v.vendor_id, vo.status
    """
    data = execute_query(query)
    return jsonify({"columns": ["vendor_name", "total_orders", "status"], "data": data})

# Chart Data Endpoints
@app.route('/api/charts/vendor-order-status', methods=['GET'])
def vendor_order_status():
    query = """
        SELECT vo.status AS "Order Status", COUNT(vo.order_id) AS "Order Count"
        FROM VendorOrders vo
        GROUP BY vo.status
    """
    data = execute_query(query)
    return jsonify({"data": data})

@app.route('/api/charts/monthly-revenue-trend', methods=['GET'])
def monthly_revenue_trend():
    query = """
        SELECT YEAR(s.date) AS Year, MONTH(s.date) AS Month, SUM(s.total_amount) AS Revenue
        FROM Sales s
        GROUP BY YEAR(s.date), MONTH(s.date)
        ORDER BY Year, Month
    """
    data = execute_query(query)
    return jsonify({"data": data})

@app.route('/api/charts/revenue-by-vendor', methods=['GET'])
def revenue_by_vendor():
    query = """
        SELECT v.name AS Vendor, SUM(sd.quantity * p.selling_price) AS Revenue
        FROM SalesDetails sd
        JOIN Products p ON sd.product_id = p.product_id
        JOIN Vendors v ON p.vendor_id = v.vendor_id
        GROUP BY v.name
    """
    data = execute_query(query)
    return jsonify({"data": data})

if __name__ == '__main__':
    app.run(debug=True)
