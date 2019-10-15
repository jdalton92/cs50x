import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    portfolio = db.execute("SELECT symbol, number, price_per_share FROM portfolio WHERE user_id=:user_id",
                           user_id=session["user_id"])
    assets_db = db.execute("SELECT SUM(number) FROM portfolio WHERE user_id=:user_id GROUP by symbol", user_id=session["user_id"])
    cash_db = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])

    # Create a list of lookup dictionary outputs for shares_owned
    shares_owned = {}
    assets = 0
    if portfolio:
        for share in portfolio:
            if share["symbol"] in shares_owned:
                shares_owned[share["symbol"]]["number"] += share["number"]
                shares_owned[share["symbol"]]["total"] = usd(
                    shares_owned[share["symbol"]]["number"] * lookup(share["symbol"])["price"])
                assets += float(shares_owned[share["symbol"]]["number"] * lookup(share["symbol"])["price"])
            else:
                shares_owned[share["symbol"]] = lookup(share["symbol"])
                shares_owned[share["symbol"]]["number"] = share["number"]
                shares_owned[share["symbol"]]["total"] = usd(share["number"] * lookup(share["symbol"])["price"])
                assets += float(shares_owned[share["symbol"]]["number"] * lookup(share["symbol"])["price"])

        cash = cash_db[0]["cash"]
        total = cash + assets

        return render_template("portfolio.html", shares_owned=shares_owned, cash=usd(cash), total=usd(total))

    return render_template("portfolio.html", shares_owned=shares_owned, cash=usd(0))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # If request method is post, buy shares
    if request.method == "POST":

        share_info = lookup(request.form.get("symbol"))

        # Check symbol exists
        if not share_info:
            return apology("Symbol not found", 400)

        # Validate amount to be bought
        try:
            number = int(request.form.get("shares"))
        except:
            return apology("You must buy more than 1 share", 400)

        if number <= 0:
            return apology("You must buy more than 1 share", 400)

        # Check user has sufficienct cash
        rows = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
        cash_required = share_info["price"] * number
        cash = rows[0]["cash"]

        if cash < cash_required:
            return apology("Not enough cash")

        # Record transaction in transaction table
        db.execute("INSERT INTO portfolio (user_id, symbol, number, price_per_share) VALUES (:user_id, :symbol, :number, :price_per_share)",
                   user_id=session["user_id"], symbol=share_info["symbol"], number=number, price_per_share=share_info["price"])

        # Update cash in user table
        db.execute("UPDATE users SET cash = cash - :cash_required WHERE id = :user_id",
                   cash_required=cash_required, user_id=session["user_id"])

        return redirect("/")

    if request.method == "GET":
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    username = request.args.get("username")

    db_username = db.execute("SELECT username FROM users WHERE username=:username", username=username)

    if len(username) > 0 and db_username:
        return jsonify(False)
    elif len(username) > 0 and not db_username:
        return jsonify(True)
    else:
        return jsonify(False)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    history = db.execute(
        "SELECT symbol, number, price_per_share, trans_time FROM portfolio WHERE user_id=:user_id", user_id=session["user_id"])

    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # If method is post, lookup symbol
    if request.method == "POST":

        quote = lookup(request.form.get("symbol"))

        if not quote:
            return apology("Symbol not found", 400)

        price = usd(quote["price"])

        return render_template("stock_quote.html", quote=quote, price=price)

    # If method is get, show quote template
    elif request.method == "GET":

        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    # If submitting a new user details, validate data
    if request.method == "POST":

        # Validate form inputs
        if not username:
            return apology("Missing Username!", 400)
        elif not password:
            return apology("Missing Password!", 400)
        elif not confirmation:
            return apology("Missing Confirmation!", 400)
        elif password != confirmation:
            return apology("Passwords don't match!", 400)

        # Hash password
        hash = generate_password_hash(password)

        # Add user to database
        new_user_id = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                                 username=username, hash=hash)

        # Return apology if username is taken
        if not new_user_id:
            return apology("Username taken", 400)

        # Store user user ID to login automatically
        session["user_id"] = new_user_id

        return redirect("/")

    # If redirecting to page, show register.html
    elif request.method == "GET":
        return render_template("register.html")


@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    """Deposit extra cash"""

    # If POST, validate data
    if request.method == "POST":

        # Validate form inputs
        deposit = int(request.form.get("deposit"))
        if deposit <= 0:
            return apology("You must deposit more than 1", 400)

        # Deposit cash
        db.execute("UPDATE users SET cash = cash + :deposit WHERE id = :user_id",
                   deposit=deposit, user_id=session["user_id"])

        return redirect("/")

    # If redirecting to page, show register.html
    elif request.method == "GET":
        return render_template("deposit.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # If POST then sell shares
    if request.method == "POST":

        quote = lookup(request.form.get("symbol"))
        symbol = request.form.get("symbol")

        if not quote:
            return apology("Symbol not found", 400)

        shares = int(request.form.get("shares"))

        if shares < 1:
            return apology("Number must be positive integer", 400)

        # Check if there is enough shares in portfolio to sell
        portfolio = db.execute("SELECT SUM(number) FROM portfolio WHERE symbol=:symbol AND user_id=:user_id",
                               symbol=symbol, user_id=session["user_id"])

        if portfolio[0]["SUM(number)"] < shares:
            return apology("You don't have enough shares to sell", 400)

        total_sale = quote["price"] * shares

        # Update cash in users
        db.execute("UPDATE users SET cash = (cash + :total) WHERE id=:user_id", total=total_sale, user_id=session["user_id"])

        # Update transaction in portfolio database
        db.execute("INSERT INTO portfolio (user_id, symbol, number, price_per_share) VALUES (:user_id, :symbol, :number, :price_per_share)",
                   user_id=session["user_id"], symbol=symbol, number=-shares, price_per_share=quote["price"])

        return redirect("/")

    # If GET then redirect to sell page
    elif request.method == "GET":
        return render_template("sell.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)