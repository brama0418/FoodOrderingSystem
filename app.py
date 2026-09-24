from flask import Flask, render_template, redirect, request, session
import sqlite3

app = Flask(__name__)

app.secret_key = "food_secret_key"


# Database connection
def get_db_connection():
    conn = sqlite3.connect("food.db")
    return conn


# Login check
def is_logged_in():
    return "username" in session


# Create database
def create_database():

    conn = get_db_connection()
    cursor = conn.cursor()

    # Foods table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL
        )
    """)

    # Cart table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_id INTEGER,
            food_name TEXT,
            price REAL,
            quantity INTEGER
        )
    """)

    # Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_name TEXT,
            quantity INTEGER,
            total REAL
        )
    """)

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Food items
    foods = [

        # Non-Veg Starters
        ("Chicken Tikka", "Juicy grilled chicken pieces", 220, "Non-Veg Starters"),
        ("Chicken 65", "Crispy spicy chicken", 200, "Non-Veg Starters"),
        ("Chicken Lollipop", "Crispy chicken lollipop", 240, "Non-Veg Starters"),
        ("Chicken Wings", "Spicy crispy chicken wings", 230, "Non-Veg Starters"),
        ("Chicken Kebab", "Grilled chicken kebab", 250, "Non-Veg Starters"),

        # Veg Starters
        ("Paneer Tikka", "Grilled paneer with spices", 180, "Veg Starters"),
        ("Gobi Manchurian", "Crispy cauliflower Manchurian", 160, "Veg Starters"),
        ("Veg Manchurian", "Vegetable balls in spicy sauce", 150, "Veg Starters"),

        # Non-Veg Biryanis
        ("Chicken Biryani", "Hyderabadi style chicken biryani", 250, "Non-Veg Biryanis"),
        ("Mutton Biryani", "Delicious mutton biryani", 320, "Non-Veg Biryanis"),
        ("Egg Biryani", "Flavourful egg biryani", 180, "Non-Veg Biryanis"),

        # Veg Biryanis
        ("Veg Biryani", "Mixed vegetable biryani", 160, "Veg Biryanis"),
        ("Paneer Biryani", "Paneer and rice biryani", 190, "Veg Biryanis"),

        # Fast Food
        ("Pizza", "Cheesy vegetable pizza", 250, "Fast Food"),
        ("Burger", "Loaded cheese burger", 150, "Fast Food"),
        ("Pasta", "Creamy white sauce pasta", 180, "Fast Food"),
        ("Noodles", "Spicy vegetable noodles", 140, "Fast Food"),
        ("Chicken Roll", "Spicy chicken roll", 160, "Fast Food"),
        ("Chicken Shawarma", "Loaded chicken shawarma", 180, "Fast Food"),

        # Veg Main Course
        ("Paneer Butter Masala", "Paneer in creamy tomato gravy", 200, "Veg Main Course"),
        ("Masala Dosa", "Crispy dosa with potato masala", 100, "Veg Main Course"),

        # Soft Drinks
        ("Coke", "Chilled Coca Cola", 50, "Soft Drinks"),
        ("Pepsi", "Chilled Pepsi", 50, "Soft Drinks"),
        ("Sprite", "Refreshing lemon drink", 50, "Soft Drinks"),
        ("Fanta", "Refreshing orange drink", 50, "Soft Drinks"),
        ("Fresh Lime Soda", "Fresh lime refreshing drink", 70, "Soft Drinks"),

        # Juices & Milkshakes
        ("Mango Juice", "Fresh mango juice", 90, "Juices & Milkshakes"),
        ("Orange Juice", "Fresh orange juice", 80, "Juices & Milkshakes"),
        ("Chocolate Milkshake", "Creamy chocolate milkshake", 120, "Juices & Milkshakes"),
        ("Vanilla Milkshake", "Creamy vanilla milkshake", 110, "Juices & Milkshakes"),

        # Desserts
        ("Ice Cream", "Creamy vanilla ice cream", 80, "Desserts"),
        ("Gulab Jamun", "Soft sweet gulab jamun", 70, "Desserts"),
        ("Brownie", "Chocolate brownie", 100, "Desserts"),
        ("Chocolate Cake", "Soft chocolate cake", 120, "Desserts")
    ]

    # Insert food items only if table is empty
    cursor.execute("SELECT COUNT(*) FROM foods")
    food_count = cursor.fetchone()[0]

    if food_count == 0:

        cursor.executemany("""
            INSERT INTO foods
            (name, description, price, category)
            VALUES (?, ?, ?, ?)
        """, foods)

    conn.commit()
    conn.close()


# Home
@app.route("/")
def home():

    if not is_logged_in():
        return redirect("/login")

    return render_template("home.html")


# Menu
@app.route("/menu")
def menu():

    if not is_logged_in():
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM foods
        ORDER BY category, name
    """)

    foods = cursor.fetchall()

    conn.close()

    return render_template("menu.html", foods=foods)


# Add to cart
@app.route("/add-to-cart/<int:food_id>")
def add_to_cart(food_id):

    if not is_logged_in():
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM foods
        WHERE id = ?
    """, (food_id,))

    food = cursor.fetchone()

    if food:

        cursor.execute("""
            SELECT *
            FROM cart
            WHERE food_id = ?
        """, (food_id,))

        existing_item = cursor.fetchone()

        if existing_item:

            cursor.execute("""
                UPDATE cart
                SET quantity = quantity + 1
                WHERE food_id = ?
            """, (food_id,))

        else:

            cursor.execute("""
                INSERT INTO cart
                (food_id, food_name, price, quantity)
                VALUES (?, ?, ?, ?)
            """, (food[0], food[1], food[3], 1))

    conn.commit()
    conn.close()

    return redirect("/cart")


# Cart
@app.route("/cart")
def cart():

    if not is_logged_in():
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM cart
    """)

    cart_items = cursor.fetchall()

    total = 0

    for item in cart_items:
        total += item[3] * item[4]

    conn.close()

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total
    )


# Increase quantity
@app.route("/increase/<int:cart_id>")
def increase(cart_id):

    if not is_logged_in():
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE cart
        SET quantity = quantity + 1
        WHERE id = ?
    """, (cart_id,))

    conn.commit()
    conn.close()

    return redirect("/cart")


# Decrease quantity
@app.route("/decrease/<int:cart_id>")
def decrease(cart_id):

    if not is_logged_in():
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE cart
        SET quantity = quantity - 1
        WHERE id = ? AND quantity > 1
    """, (cart_id,))

    conn.commit()
    conn.close()

    return redirect("/cart")


# Remove from cart
@app.route("/remove/<int:cart_id>")
def remove(cart_id):

    if not is_logged_in():
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM cart
        WHERE id = ?
    """, (cart_id,))

    conn.commit()
    conn.close()

    return redirect("/cart")


# Place order
@app.route("/place-order")
def place_order():

    if not is_logged_in():
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM cart
    """)

    cart_items = cursor.fetchall()

    if cart_items:

        for item in cart_items:

            item_total = item[3] * item[4]

            cursor.execute("""
                INSERT INTO orders
                (food_name, quantity, total)
                VALUES (?, ?, ?)
            """, (
                item[2],
                item[4],
                item_total
            ))

        cursor.execute("DELETE FROM cart")

        conn.commit()

    conn.close()

    return render_template("order_success.html")


# Orders
@app.route("/orders")
def orders():

    if not is_logged_in():
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM orders
        ORDER BY id DESC
    """)

    orders = cursor.fetchall()

    conn.close()

    return render_template(
        "orders.html",
        orders=orders
    )


# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM users
            WHERE username = ? AND password = ?
        """, (username, password))

        user = cursor.fetchone()

        conn.close()

        if user:

            session["username"] = username

            return redirect("/")

        else:

            return "Invalid username or password"

    return render_template("login.html")


# Register
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute("""
                INSERT INTO users
                (fullname, username, password)
                VALUES (?, ?, ?)
            """, (fullname, username, password))

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:

            conn.close()

            return "Username already exists. Please use another username."

    return render_template("register.html")


# Logout
@app.route("/logout")
def logout():

    session.pop("username", None)

    return redirect("/login")


# Run application
if __name__ == "__main__":

    create_database()

    app.run(debug=True)