from functools import wraps
from flask import Flask, flash, redirect, render_template, url_for, session, request, jsonify
from flask_socketio import SocketIO
from forms import RegisterForm, LoginForm
from models import db, User, Transaction
from flask_bcrypt import Bcrypt
from tradejini_client import TradejiniClient
from real_price_stream import RealPriceStreamer
from config import TRADEJINI_CONFIG


def create_app():
  app = Flask(__name__)
  from config import SECRET_KEY, DATABASE_URL
  app.config['SECRET_KEY'] = SECRET_KEY
  app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
  bcrypt = Bcrypt()
  socketio = SocketIO(app, cors_allowed_origins="*")

  db.init_app(app)
  bcrypt.init_app(app)
  
  # Initialize real price streamer
  price_streamer = RealPriceStreamer(socketio)
  
  # Start real stream with your credentials
  price_streamer.start_real_stream(
      TRADEJINI_CONFIG['apikey'],
      TRADEJINI_CONFIG['password'],
      TRADEJINI_CONFIG['two_fa'],
      TRADEJINI_CONFIG['two_fa_type']
  )

  with app.app_context():
    db.create_all()


  def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

  @app.route("/")
  def home():
    return render_template("home.html")


  @app.route("/login", methods=['GET', 'POST'])
  def login():
    if 'user_id' in session:
        return redirect(url_for("dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('You have been logged in!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    else:
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'danger')
    return render_template("login.html", form=form)


  @app.route("/register", methods = ['GET', 'POST'])
  def register():
    if 'user_id' in session:
        return redirect(url_for("dashboard"))
    form = RegisterForm()
    if form.validate_on_submit():
        hased_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hased_password,
        )
        db.session.add(user)
        db.session.commit()
        flash('Your Account has been created!!!', 'success')
        return redirect(url_for("login"))

    return render_template("register.html", form=form)

  @app.route("/dashboard")
  @login_required
  def dashboard():
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        flash('User not found. Please login again.', 'danger')
        return redirect(url_for('login'))
    
    if user.balance is None:
        user.balance = 100000.0
        db.session.commit()
    
    # Get stock data from TradJini API
    client = TradejiniClient()
    stocks = client.get_stock_list()
    
    return render_template("dashboard.html", stocks=stocks, balance=user.balance)

  @app.route("/buy", methods=['POST'])
  @login_required
  def buy_stock():
    symbol = request.form.get('symbol')
    # Get current live price instead of form price
    price = price_streamer.get_current_price(symbol)
    if price == 0.0:  # Fallback to form price if live price not available
        price = float(request.form.get('price'))
    quantity = int(request.form.get('quantity', 1))
    
    user = User.query.get(session['user_id'])
    total_cost = price * quantity
    
    if user.balance >= total_cost:
        user.balance -= total_cost
        
        transaction = Transaction(
            user_id=user.id,
            symbol=symbol,
            type='BUY',
            quantity=quantity,
            price=price
        )
        
        db.session.add(transaction)
        db.session.commit()
        flash(f'Bought {quantity} shares of {symbol} at ₹{price}', 'success')
    else:
        flash('Insufficient balance', 'danger')
    
    return redirect(url_for('dashboard'))

  @app.route("/sell", methods=['POST'])
  @login_required
  def sell_stock():
    symbol = request.form.get('symbol')
    # Get current live price instead of form price
    price = price_streamer.get_current_price(symbol)
    if price == 0.0:  # Fallback to form price if live price not available
        price = float(request.form.get('price'))
    quantity = int(request.form.get('quantity', 1))
    
    user = User.query.get(session['user_id'])
    
    # Check available shares
    buy_qty = db.session.query(db.func.sum(Transaction.quantity)).filter_by(
        user_id=user.id, symbol=symbol, type='BUY').scalar() or 0
    sell_qty = db.session.query(db.func.sum(Transaction.quantity)).filter_by(
        user_id=user.id, symbol=symbol, type='SELL').scalar() or 0
    available = buy_qty - sell_qty
    
    if available >= quantity:
        total_value = price * quantity
        user.balance += total_value
        
        transaction = Transaction(
            user_id=user.id,
            symbol=symbol,
            type='SELL',
            quantity=quantity,
            price=price
        )
        
        db.session.add(transaction)
        db.session.commit()
        flash(f'Sold {quantity} shares of {symbol} at ₹{price}', 'success')
    else:
        flash(f'Insufficient shares. Available: {available}', 'danger')
    
    return redirect(url_for('dashboard'))

  @app.route("/portfolio")
  @login_required
  def portfolio():
    user_id = session['user_id']
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.timestamp.desc()).all()
    
    # Calculate holdings
    holdings = {}
    for t in Transaction.query.filter_by(user_id=user_id).all():
        if t.symbol not in holdings:
            holdings[t.symbol] = {'buy': 0, 'sell': 0}
        if t.type == 'BUY':
            holdings[t.symbol]['buy'] += t.quantity
        else:
            holdings[t.symbol]['sell'] += t.quantity
    
    current_holdings = {}
    for symbol, data in holdings.items():
        net_qty = data['buy'] - data['sell']
        if net_qty > 0:
            current_holdings[symbol] = net_qty
    
    return render_template("portfolio.html", transactions=transactions, holdings=current_holdings)

  @app.route("/logout")
  def logout():
    session.pop('user_id')
    session.pop('username')
    flash('You have been logged out !', 'success')
    return redirect(url_for('home'))

  return app, socketio


if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, debug=True, port=5000)