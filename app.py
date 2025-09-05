from functools import wraps
from flask import Flask, flash, redirect, render_template, url_for, session, request, jsonify
from flask_socketio import SocketIO
from forms import LoginForm
from admin_forms import CreateUserForm, EditUserForm, DirectTokenForm
from models import db, User, Transaction, UserCredential, ShortPosition, ClosedPosition
from flask_bcrypt import Bcrypt
from tradejini_client import TradejiniClient
from live_price_stream import LivePriceStreamer
from config import TRADEJINI_CONFIG

def get_current_access_token():
    """Get current access token from database if valid (24hrs)"""
    try:
        from datetime import datetime, timedelta
        admin_user = User.query.filter_by(is_admin=True).first()
        if admin_user:
            credential = UserCredential.query.filter_by(
                user_id=admin_user.id,
                credential_name='ACCESS_TOKEN'
            ).first()
            if credential:
                # Check if token is still valid (24 hours)
                if credential.updated_at and credential.updated_at > datetime.utcnow() - timedelta(hours=24):
                    return credential.credential_value
                else:
                    print("Access token expired, need new TOTP")
    except Exception as e:
        print(f"Error getting access token: {e}")
    return None
from sqlalchemy import func


def create_app():
  app = Flask(__name__)
  from config import SECRET_KEY, DATABASE_URL
  import os
  
  # Local SQLite database
  database_url = DATABASE_URL
  
  # Check for valid access token on app start
  def check_access_token():
      token = get_current_access_token()
      if token:
          print(f"Valid access token found: {token[:10]}****")
      else:
          print("No valid access token found, need TOTP to generate new one")
  
  # Will check token after db init
  
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
  # Configure SQLAlchemy engine options based on database type
  if 'postgresql' in database_url:
      from sqlalchemy.pool import NullPool
      app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
          'poolclass': NullPool
      }
  else:
      # SQLite configuration
      app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
          'pool_pre_ping': True,
          'pool_recycle': 300,
          'connect_args': {'check_same_thread': False}
      }
  bcrypt = Bcrypt()
  socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False, ping_timeout=60, ping_interval=25)

  db.init_app(app)
  bcrypt.init_app(app)
  
  # Initialize live price streamer
  price_streamer = LivePriceStreamer(socketio)
  
  # Add route to manually start streaming (try all methods)
  @app.route('/start-streaming', methods=['POST'])
  def start_streaming():
      try:
          # Try all available methods for live prices
          if price_streamer.start_live_stream():
              return {'status': 'success', 'message': 'Live streaming started'}
          else:
              return {'status': 'failed', 'message': 'Failed to start streaming'}
      except Exception as e:
          return {'status': 'error', 'message': str(e)}

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
    
    # Check for valid access token after db is ready
    check_access_token()


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
    
    # Get stock data with live prices from streaming
    from config import STOCK_TOKENS
    import random
    
    stocks = []
    for i, (symbol, token) in enumerate(STOCK_TOKENS.items()):
        # Try to get live price from streamer first
        try:
            live_price = price_streamer.get_current_price(symbol)
            if live_price > 0:
                # Use live price
                current_price = live_price
                # Calculate change from base price (for demo)
                base_price = 500 + (i * 100)
                change_percent = ((current_price - base_price) / base_price) * 100
            else:
                # Fallback to realistic mock prices
                base_price = 500 + (i * 100)
                fluctuation = random.uniform(-0.02, 0.02)  # ±2% fluctuation
                current_price = base_price * (1 + fluctuation)
                change_percent = fluctuation * 100
        except:
            # Fallback to mock prices
            base_price = 500 + (i * 100)
            fluctuation = random.uniform(-0.02, 0.02)
            current_price = base_price * (1 + fluctuation)
            change_percent = fluctuation * 100
        
        stocks.append({
            'symbol': symbol,
            'name': symbol.replace('_', ' ').title(),
            'price': round(current_price, 2),
            'change': round(change_percent, 2)
        })
    
    return render_template("dashboard.html", stocks=stocks, balance=user.balance)

  @app.route("/buy", methods=['POST'])
  @login_required
  def buy_stock():
    symbol = request.form.get('symbol')
    try:
        price = price_streamer.get_current_price(symbol)
        if price == 0.0:
            price = float(request.form.get('price'))
    except:
        price = float(request.form.get('price'))
    quantity = int(request.form.get('quantity', 1))
    
    user = User.query.get(session['user_id'])
    
    # Check if covering short position
    short_position = ShortPosition.query.filter_by(user_id=user.id, symbol=symbol).first()
    
    if short_position and short_position.quantity > 0:
        # Covering short position
        cover_qty = min(quantity, short_position.quantity)
        profit_loss = (short_position.avg_sell_price - price) * cover_qty
        
        user.balance += profit_loss
        
        # Record closed short position
        closed_position = ClosedPosition(
            user_id=user.id,
            symbol=symbol,
            position_type='SHORT',
            quantity=cover_qty,
            buy_price=price,
            sell_price=short_position.avg_sell_price,
            pnl=profit_loss
        )
        db.session.add(closed_position)
        
        short_position.quantity -= cover_qty
        if short_position.quantity == 0:
            db.session.delete(short_position)
        
        transaction = Transaction(
            user_id=user.id,
            symbol=symbol,
            type='COVER',
            quantity=cover_qty,
            price=price
        )
        db.session.add(transaction)
        
        # If still quantity left after covering, buy normally
        remaining_qty = quantity - cover_qty
        if remaining_qty > 0:
            total_cost = price * remaining_qty
            if user.balance >= total_cost:
                user.balance -= total_cost
                buy_transaction = Transaction(
                    user_id=user.id,
                    symbol=symbol,
                    type='BUY',
                    quantity=remaining_qty,
                    price=price
                )
                db.session.add(buy_transaction)
    else:
        # Normal buy
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
    return redirect(url_for('dashboard'))

  @app.route("/sell", methods=['POST'])
  @login_required
  def sell_stock():
    symbol = request.form.get('symbol')
    try:
        price = price_streamer.get_current_price(symbol)
        if price == 0.0:
            price = float(request.form.get('price'))
    except:
        price = float(request.form.get('price'))
    quantity = int(request.form.get('quantity', 1))
    
    user = User.query.get(session['user_id'])
    
    # Calculate available shares
    buy_qty = db.session.query(db.func.sum(Transaction.quantity)).filter_by(
        user_id=user.id, symbol=symbol, type='BUY').scalar() or 0
    sell_qty = db.session.query(db.func.sum(Transaction.quantity)).filter_by(
        user_id=user.id, symbol=symbol, type='SELL').scalar() or 0
    cover_qty = db.session.query(db.func.sum(Transaction.quantity)).filter_by(
        user_id=user.id, symbol=symbol, type='COVER').scalar() or 0
    
    available = buy_qty + cover_qty - sell_qty
    
    if available >= quantity:
        # Normal sell
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
    else:
        # Short sell (selling more than owned)
        sell_available = min(quantity, available) if available > 0 else 0
        short_qty = quantity - sell_available
        
        # Normal sell for available shares
        if sell_available > 0:
            user.balance += price * sell_available
            sell_transaction = Transaction(
                user_id=user.id,
                symbol=symbol,
                type='SELL',
                quantity=sell_available,
                price=price
            )
            db.session.add(sell_transaction)
        
        # Short sell for remaining quantity
        if short_qty > 0:
            collateral = price * short_qty
            if user.balance >= collateral:
                user.balance -= collateral  # Reserve collateral
                
                # Create or update short position
                short_position = ShortPosition.query.filter_by(
                    user_id=user.id, symbol=symbol).first()
                
                if short_position:
                    # Update existing short position with weighted average
                    total_qty = short_position.quantity + short_qty
                    total_value = (short_position.avg_sell_price * short_position.quantity) + (price * short_qty)
                    short_position.avg_sell_price = total_value / total_qty
                    short_position.quantity = total_qty
                else:
                    # Create new short position
                    short_position = ShortPosition(
                        user_id=user.id,
                        symbol=symbol,
                        quantity=short_qty,
                        avg_sell_price=price
                    )
                    db.session.add(short_position)
                
                short_transaction = Transaction(
                    user_id=user.id,
                    symbol=symbol,
                    type='SHORT_SELL',
                    quantity=short_qty,
                    price=price
                )
                db.session.add(short_transaction)
    
    db.session.commit()
    return redirect(url_for('dashboard'))

  @app.route("/portfolio")
  @login_required
  def portfolio():
    user_id = session['user_id']
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.timestamp.desc()).all()
    
    # Calculate holdings with P&L (including new transaction types)
    holdings = {}
    for t in Transaction.query.filter_by(user_id=user_id).all():
        if t.symbol not in holdings:
            holdings[t.symbol] = {'buy_qty': 0, 'sell_qty': 0, 'buy_value': 0, 'sell_value': 0}
        
        if t.type in ['BUY', 'COVER']:  # Both BUY and COVER add to holdings
            holdings[t.symbol]['buy_qty'] += t.quantity
            holdings[t.symbol]['buy_value'] += t.quantity * t.price
        elif t.type in ['SELL', 'SHORT_SELL']:  # Both SELL and SHORT_SELL reduce holdings
            holdings[t.symbol]['sell_qty'] += t.quantity
            holdings[t.symbol]['sell_value'] += t.quantity * t.price
    
    current_holdings = {}
    total_invested = 0
    total_current_value = 0
    
    for symbol, data in holdings.items():
        net_qty = data['buy_qty'] - data['sell_qty']
        if net_qty > 0:
            # Get current live price
            try:
                current_price = price_streamer.get_current_price(symbol)
                if current_price == 0.0:
                    current_price = data['buy_value'] / data['buy_qty'] if data['buy_qty'] > 0 else 0
            except:
                current_price = data['buy_value'] / data['buy_qty'] if data['buy_qty'] > 0 else 0
            
            # Use current price for both invested and current value
            invested_amount = net_qty * current_price
            current_value = net_qty * current_price
            pnl = 0  # No P&L since both use current price
            pnl_percent = 0
            
            current_holdings[symbol] = {
                'quantity': net_qty,
                'avg_price': current_price,  # Show current price as avg price
                'current_price': current_price,
                'invested': invested_amount,
                'current_value': current_value,
                'pnl': pnl,
                'pnl_percent': pnl_percent
            }
            
            total_invested += invested_amount
            total_current_value += current_value
    
    # Get short positions first
    short_positions = {}
    for short in ShortPosition.query.filter_by(user_id=user_id).all():
        try:
            current_price = price_streamer.get_current_price(short.symbol)
            if current_price == 0.0:
                current_price = short.avg_sell_price
        except:
            current_price = short.avg_sell_price
        
        unrealized_pnl = (short.avg_sell_price - current_price) * short.quantity
        short_positions[short.symbol] = {
            'quantity': short.quantity,
            'avg_sell_price': short.avg_sell_price,
            'current_price': current_price,
            'unrealized_pnl': unrealized_pnl
        }
    
    # Calculate short position values
    total_short_collateral = 0
    total_short_pnl = 0
    
    for symbol, data in short_positions.items():
        collateral = data['avg_sell_price'] * data['quantity']  # Collateral reserved
        total_short_collateral += collateral
        total_short_pnl += data['unrealized_pnl']
    
    # Combined portfolio totals
    combined_invested = total_invested + total_short_collateral
    combined_current_value = total_current_value + total_short_collateral + total_short_pnl
    combined_pnl = total_current_value - total_invested + total_short_pnl
    combined_pnl_percent = (combined_pnl / combined_invested * 100) if combined_invested > 0 else 0
    
    # Get closed positions P&L
    closed_positions = ClosedPosition.query.filter_by(user_id=user_id).order_by(ClosedPosition.closed_at.desc()).limit(10).all()
    total_closed_pnl = db.session.query(func.sum(ClosedPosition.pnl)).filter_by(user_id=user_id).scalar() or 0
    
    portfolio_summary = {
        'total_invested': combined_invested,
        'current_value': combined_current_value,
        'total_pnl': combined_pnl,
        'total_pnl_percent': combined_pnl_percent,
        'total_closed_pnl': total_closed_pnl
    }
    
    from datetime import timedelta
    return render_template("portfolio.html", transactions=transactions, holdings=current_holdings, short_positions=short_positions, summary=portfolio_summary, closed_positions=closed_positions, current_user=User.query.get(user_id), timedelta=timedelta)

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



  @app.route("/admin/direct-token", methods=['GET', 'POST'])
  @admin_required
  def admin_direct_token():
    form = DirectTokenForm()
    
    if form.validate_on_submit():
        # Store access token directly
        admin_user = User.query.filter_by(is_admin=True).first()
        access_token = form.access_token.data.strip()
        
        if admin_user:
            from datetime import datetime, timedelta
            
            # Store access token with timestamp for 24hr validity
            token_credential = UserCredential.query.filter_by(
                user_id=admin_user.id,
                credential_name='ACCESS_TOKEN'
            ).first()
            
            if token_credential:
                token_credential.credential_value = access_token
                token_credential.updated_at = datetime.utcnow()
            else:
                token_credential = UserCredential(
                    user_id=admin_user.id,
                    credential_name='ACCESS_TOKEN',
                    credential_value=access_token
                )
                db.session.add(token_credential)
            
            db.session.commit()
            flash(f'Access token saved successfully! Token: {access_token[:10]}****', 'success')
            print(f'Direct access token stored: {access_token[:10]}****')
        
        # Update TRADEJINI_CONFIG with the new token for immediate use
        TRADEJINI_CONFIG['access_token'] = access_token
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template("admin_direct_token.html", form=form)

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


# Entry point for both local and production
if __name__ == '__main__':
    import os
    app, socketio = create_app()
    port = int(os.getenv('PORT', 8000))
    socketio.run(app, debug=False, host='0.0.0.0', port=port)