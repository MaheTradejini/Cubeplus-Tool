from functools import wraps
from flask import Flask, flash, redirect, render_template, url_for, session, request, jsonify
from flask_socketio import SocketIO
from forms import LoginForm
from admin_forms import CreateUserForm, EditUserForm, GlobalTOTPForm
from models import db, User, Transaction, UserCredential
from flask_bcrypt import Bcrypt
from tradejini_client import TradejiniClient
from live_price_stream import LivePriceStreamer
from config import TRADEJINI_CONFIG

def get_current_totp():
    """Get current TOTP from database or environment"""
    try:
        # First try database (admin updated TOTP)
        admin_user = User.query.filter_by(is_admin=True).first()
        if admin_user:
            credential = UserCredential.query.filter_by(
                user_id=admin_user.id,
                credential_name='GLOBAL_TOTP'
            ).first()
            if credential:
                return credential.credential_value
    except:
        pass
    
    # Fallback to environment variable (initial setup)
    import os
    return os.environ.get('TRADEJINI_TWO_FA', '')
from sqlalchemy import func


def create_app():
  app = Flask(__name__)
  from config import SECRET_KEY, DATABASE_URL
  import os
  
  # Use SQLite for production (PostgreSQL has Python 3.13 compatibility issues)
  database_url = 'sqlite:///app.db'
  app.logger.info('Using SQLite database for production')
  
  # Update TRADEJINI_CONFIG with current TOTP
  def update_tradejini_config():
      current_totp = get_current_totp()
      if current_totp:
          TRADEJINI_CONFIG['two_fa'] = current_totp
  
  # Update config on app start and periodically
  update_tradejini_config()
  
  # Add route to refresh TOTP config
  @app.route('/refresh-totp', methods=['POST'])
  def refresh_totp():
      """Internal endpoint to refresh TOTP config"""
      update_tradejini_config()
      return {'status': 'updated'}
  
  # Test TradJini authentication
  @app.route('/test-tradejini')
  def test_tradejini():
      """Test TradJini API authentication"""
      try:
          client = TradejiniClient()
          if client.access_token:
              return {'status': 'success', 'message': 'TradJini authenticated successfully'}
          else:
              return {'status': 'failed', 'message': 'TradJini authentication failed'}
      except Exception as e:
          return {'status': 'error', 'message': str(e)}
  
  # Check streaming status
  @app.route('/streaming-status')
  def streaming_status():
      """Check live price streaming status"""
      try:
          status = price_streamer.get_connection_status()
          return {
              'status': 'success',
              'streaming': status,
              'live_prices_count': len(price_streamer.live_prices) if hasattr(price_streamer, 'live_prices') else 0
          }
      except Exception as e:
          return {'status': 'error', 'message': str(e)}
  app.config['SECRET_KEY'] = SECRET_KEY
  app.config['SQLALCHEMY_DATABASE_URI'] = database_url
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
      'pool_pre_ping': True,
      'pool_recycle': 300,
  }
  bcrypt = Bcrypt()
  socketio = SocketIO(app, cors_allowed_origins="*")

  db.init_app(app)
  bcrypt.init_app(app)
  
  # Initialize live price streamer
  price_streamer = LivePriceStreamer(socketio)
  
  # Start live stream
  try:
      if not price_streamer.start_live_stream():
          app.logger.warning("Failed to start live stream - check SDK installation")
  except Exception as e:
      app.logger.error(f"Live stream initialization error: {e}")
      # Continue without live stream for deployment

  with app.app_context():
    db.create_all()
    # Create admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@cubeplus.com',
            is_admin=True,
            balance=0
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()


  def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

  def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_login'))
        user = User.query.get(session['admin_id'])
        if not user or not user.is_admin:
            flash('Admin access required', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

  @app.route("/")
  def home():
    return render_template("home.html")


  @app.route("/login", methods=['GET', 'POST'])
  def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.is_active and user.check_password(form.password.data):
            if user.is_admin:
                flash('Admin users must login through /admin', 'warning')
                return render_template("login.html", form=form)
            session['user_id'] = user.id
            session['username'] = user.username
            flash('You have been logged in!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check credentials or account status.', 'danger')
    return render_template("login.html", form=form)




  @app.route("/dashboard")
  @login_required
  def dashboard():
    user = User.query.get(session['user_id'])
    if not user or not user.is_active:
        session.clear()
        flash('Account not found or inactive.', 'danger')
        return redirect(url_for('login'))
    
    if user.is_admin:
        flash('Admin users cannot access client dashboard', 'danger')
        return redirect(url_for('admin_login'))
    
    # Get stock data from TradJini API or fallback to mock data
    try:
        client = TradejiniClient()
        stocks = client.get_stock_list()
    except Exception as e:
        app.logger.warning(f"TradJini API failed: {e}, using mock data")
        # Fallback to mock stock data with live-like prices
        from config import STOCK_TOKENS
        import random
        import time
        
        stocks = []
        base_time = int(time.time())
        for i, (symbol, token) in enumerate(STOCK_TOKENS.items()):
            # Generate realistic fluctuating prices
            base_price = 500 + (i * 100)  # Different base prices
            fluctuation = random.uniform(-0.05, 0.05)  # ±5% fluctuation
            current_price = base_price * (1 + fluctuation)
            
            stocks.append({
                'symbol': symbol,
                'name': symbol.replace('_', ' ').title(),
                'price': round(current_price, 2),
                'change': round(fluctuation * 100, 2)
            })
    
    return render_template("dashboard.html", stocks=stocks, balance=user.balance)

  @app.route("/buy", methods=['POST'])
  @login_required
  def buy_stock():
    symbol = request.form.get('symbol')
    # Get current live price or fallback to form price
    try:
        price = price_streamer.get_current_price(symbol)
        if price == 0.0:
            price = float(request.form.get('price'))
    except:
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
        pass
    else:
        pass
    
    return redirect(url_for('dashboard'))

  @app.route("/sell", methods=['POST'])
  @login_required
  def sell_stock():
    symbol = request.form.get('symbol')
    # Get current live price or fallback to form price
    try:
        price = price_streamer.get_current_price(symbol)
        if price == 0.0:
            price = float(request.form.get('price'))
    except:
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
        pass
    else:
        pass
    
    return redirect(url_for('dashboard'))

  @app.route("/portfolio")
  @login_required
  def portfolio():
    user_id = session['user_id']
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.timestamp.desc()).all()
    
    # Calculate holdings with P&L
    holdings = {}
    for t in Transaction.query.filter_by(user_id=user_id).all():
        if t.symbol not in holdings:
            holdings[t.symbol] = {'buy_qty': 0, 'sell_qty': 0, 'buy_value': 0, 'sell_value': 0}
        if t.type == 'BUY':
            holdings[t.symbol]['buy_qty'] += t.quantity
            holdings[t.symbol]['buy_value'] += t.quantity * t.price
        else:
            holdings[t.symbol]['sell_qty'] += t.quantity
            holdings[t.symbol]['sell_value'] += t.quantity * t.price
    
    current_holdings = {}
    total_invested = 0
    total_current_value = 0
    
    for symbol, data in holdings.items():
        net_qty = data['buy_qty'] - data['sell_qty']
        if net_qty > 0:
            avg_buy_price = data['buy_value'] / data['buy_qty'] if data['buy_qty'] > 0 else 0
            invested_amount = net_qty * avg_buy_price
            
            # Get current live price or use average price
            try:
                current_price = price_streamer.get_current_price(symbol)
                if current_price == 0.0:
                    current_price = avg_buy_price
            except:
                current_price = avg_buy_price
            current_value = net_qty * current_price
            pnl = current_value - invested_amount
            pnl_percent = (pnl / invested_amount * 100) if invested_amount > 0 else 0
            
            current_holdings[symbol] = {
                'quantity': net_qty,
                'avg_price': avg_buy_price,
                'current_price': current_price,
                'invested': invested_amount,
                'current_value': current_value,
                'pnl': pnl,
                'pnl_percent': pnl_percent
            }
            
            total_invested += invested_amount
            total_current_value += current_value
    
    total_pnl = total_current_value - total_invested
    total_pnl_percent = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    
    portfolio_summary = {
        'total_invested': total_invested,
        'current_value': total_current_value,
        'total_pnl': total_pnl,
        'total_pnl_percent': total_pnl_percent
    }
    
    from datetime import timedelta
    return render_template("portfolio.html", transactions=transactions, holdings=current_holdings, summary=portfolio_summary, current_user=User.query.get(user_id), timedelta=timedelta)

  # Admin Login Route
  @app.route("/admin", methods=['GET', 'POST'])
  def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.is_active and user.check_password(form.password.data):
            if not user.is_admin:
                flash('Admin access required', 'danger')
                return render_template("admin_login.html", form=form)
            session['admin_id'] = user.id
            session['admin_username'] = user.username
            flash('Admin logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
    return render_template("admin_login.html", form=form)

  # Admin Dashboard
  @app.route("/admin/dashboard")
  @admin_required
  def admin_dashboard():
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_transactions = Transaction.query.count()
    total_volume = db.session.query(func.sum(Transaction.price * Transaction.quantity)).scalar() or 0
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    return render_template("admin_dashboard.html", 
                         total_users=total_users,
                         active_users=active_users, 
                         total_transactions=total_transactions,
                         total_volume=f"{total_volume:,.0f}",
                         recent_users=recent_users)

  @app.route("/admin/logout")
  @admin_required
  def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('Admin logged out successfully!', 'success')
    return redirect(url_for('admin_login'))

  @app.route("/admin/users")
  @admin_required
  def admin_users():
    users = User.query.all()
    return render_template("admin_users.html", users=users)

  @app.route("/admin/create-user", methods=['GET', 'POST'])
  @admin_required
  def admin_create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        if User.query.count() >= 30:
            flash('Maximum 30 users allowed', 'danger')
            return redirect(url_for('admin_users'))
        
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data)
        ).first()
        
        if existing_user:
            flash('Username or email already exists', 'danger')
        else:
            user = User(
                username=form.username.data,
                email=form.email.data,
                balance=float(form.balance.data or 100000),
                is_admin=form.is_admin.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash(f'User {user.username} created successfully', 'success')
            return redirect(url_for('admin_users'))
    
    return render_template("admin_create_user.html", form=form)

  @app.route("/admin/edit-user/<int:user_id>", methods=['GET', 'POST'])
  @admin_required
  def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm()
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.balance = float(form.balance.data)
        user.is_active = form.is_active.data
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash(f'User {user.username} updated successfully', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template("admin_edit_user.html", form=form, user=user)

  @app.route("/admin/global-totp", methods=['GET', 'POST'])
  @admin_required
  def admin_global_totp():
    form = GlobalTOTPForm()
    
    if form.validate_on_submit():
        # Store TOTP in database for production persistence
        import os
        from models import db
        
        # Update current session
        os.environ['TRADEJINI_TWO_FA'] = form.totp_secret.data
        
        # Store in database for persistence across restarts
        admin_user = User.query.filter_by(is_admin=True).first()
        if admin_user:
            # Store TOTP in admin user record or create system config
            credential = UserCredential.query.filter_by(
                user_id=admin_user.id, 
                credential_name='GLOBAL_TOTP'
            ).first()
            
            if credential:
                credential.credential_value = form.totp_secret.data
            else:
                credential = UserCredential(
                    user_id=admin_user.id,
                    credential_name='GLOBAL_TOTP',
                    credential_value=form.totp_secret.data
                )
                db.session.add(credential)
            
            db.session.commit()
        
        # Test TradJini authentication with new TOTP
        try:
            client = TradejiniClient()
            if client.access_token:
                # Store access token in database for 24 hours
                token_credential = UserCredential.query.filter_by(
                    user_id=admin_user.id,
                    credential_name='ACCESS_TOKEN'
                ).first()
                
                if token_credential:
                    token_credential.credential_value = client.access_token
                else:
                    token_credential = UserCredential(
                        user_id=admin_user.id,
                        credential_name='ACCESS_TOKEN',
                        credential_value=client.access_token
                    )
                    db.session.add(token_credential)
                
                db.session.commit()
                flash('TOTP verified and access token stored! Live prices active for 24 hours.', 'success')
            else:
                # For now, create a mock token to enable live-like prices
                import time
                mock_token = f"MOCK_TOKEN_{int(time.time())}"
                token_credential = UserCredential.query.filter_by(
                    user_id=admin_user.id,
                    credential_name='ACCESS_TOKEN'
                ).first()
                
                if token_credential:
                    token_credential.credential_value = mock_token
                else:
                    token_credential = UserCredential(
                        user_id=admin_user.id,
                        credential_name='ACCESS_TOKEN',
                        credential_value=mock_token
                    )
                    db.session.add(token_credential)
                
                db.session.commit()
                flash('TOTP saved! Using simulated live prices (TradJini API credentials need verification).', 'warning')
        except Exception as e:
            flash(f'TOTP verification failed: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    return render_template("admin_global_totp.html", form=form)

  @app.route("/admin/toggle-user/<int:user_id>")
  @admin_required
  def admin_toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        user.is_active = not user.is_active
        db.session.commit()
        status = 'activated' if user.is_active else 'deactivated'
        flash(f'User {user.username} {status}', 'success')
    return redirect(url_for('admin_users'))

  @app.route("/logout")
  def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out!', 'success')
    return redirect(url_for('home'))

  return app, socketio


if __name__ == '__main__':
    import os
    app, socketio = create_app()
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, debug=False, host='0.0.0.0', port=port)