import logging
import requests
from sqlalchemy import create_engine
import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os

load_dotenv()
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_UNAME')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

base_url = 'https://api.binance.com'
top_pairs = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]

try:
    engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
    with engine.connect() as conn:
        logger.debug("Database connection successful.")
except SQLAlchemyError as e:
    logger.error("Failed to connect to the database.", exc_info=e)
    exit()


def get_latest_prices(symbol):
   
    response = requests.get(f"{base_url}/api/v3/ticker/price", params={"symbol": symbol})
    latest_price_data = response.json()
    logger.debug(latest_price_data)
        
    with engine.connect() as conn:
        conn.execute(
            sa.text("""
        INSERT INTO latest_prices (symbol, price)
        VALUES (:symbol, :price)
    """
            ),
            # Pass dictionary directly to the insert statement
            latest_price_data,
        )
        conn.commit()

def get_recent_trades(symbol, limit=20):
    response = requests.get(f"{base_url}/api/v3/trades", params={"symbol": symbol, "limit": limit})
    recent_trades = response.json()
    
    for recent_trade in recent_trades:
        recent_trade.update({"symbol": symbol})
        logger.debug(recent_trade)

    with engine.connect() as conn:
        conn.execute(
            sa.text(
                "INSERT INTO public.recent_trades (price, quote_qty, qty, is_buyer_maker, is_best_match, symbol) VALUES (:price, :quoteQty,  :qty, :isBuyerMaker, :isBestMatch, :symbol)"
            ),
            recent_trades,
        )
        conn.commit()

def get_orderbook(symbol, limit=20):
    
    url = f'{base_url}/api/v3/depth'
    try:
        response = requests.get(url, params={'symbol': symbol, 'limit': limit})
       
        response.raise_for_status()
        order_data = response.json()
        
        last_update_id = order_data['lastUpdateId']
        orders_to_insert = []

        
        for price, quantity in order_data['bids']:
            orders_to_insert.append({
                'symbol': symbol,
                'last_update_id': last_update_id,
                'side': 'bid',
                'price': price,
                'quantity': quantity
            })

        
        for price, quantity in order_data['asks']:
            orders_to_insert.append({
                'symbol': symbol,
                'last_update_id': last_update_id,
                'side': 'ask',
                'price': price,
                'quantity': quantity
            })

        if not orders_to_insert:
            logger.warning(f"No order book data found for {symbol}")
            return
            
        logger.debug(f"Inserting {len(orders_to_insert)} order book entries for {symbol}")
        with engine.connect() as conn:

            conn.execute(
                sa.text("""
                    INSERT INTO order_book (symbol, last_update_id, side, price, quantity)
                    VALUES (:symbol, :last_update_id, :side, :price, :quantity)
                """),
                orders_to_insert,
            )
            conn.commit()

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch order book for {symbol}", exc_info=e)
    except SQLAlchemyError as e:
        logger.error(f"Database error inserting order book for {symbol}", exc_info=e)
    

def get_ticker_stats_data(symbol, limit=20):
    

if __name__ == "__main__":
    for symbol in top_pairs:
        get_recent_trades(symbol)
        get_latest_prices(symbol)
        get_orderbook(symbol)