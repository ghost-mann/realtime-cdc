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
    

def get_ticker_stats_data(symbol):
    
    url = f'{base_url}/api/v3/ticker/24hr'
    try:
        response = requests.get(url, params={'symbol':symbol})
        response.raise_for_status()
        stats_data = response.json()
    
        logger.debug(f"24hr Stats for {symbol}")
        with engine.connect() as conn:
            conn.execute(sa.text("""
                INSERT INTO public.ticker_stats (
                    symbol, price_change, price_change_percent, weighted_avg_price, prev_close_price, 
                    last_price, last_qty, bid_price, bid_qty, ask_price, ask_qty, open_price, high_price, 
                    low_price, volume, quote_volume, open_time, close_time, first_id, last_id, trade_count, updated_at
                ) VALUES (
                    :symbol, :priceChange, :priceChangePercent, :weightedAvgPrice, :prevClosePrice, 
                    :lastPrice, :lastQty, :bidPrice, :bidQty, :askPrice, :askQty, :openPrice, :highPrice, 
                    :lowPrice, :volume, :quoteVolume, to_timestamp(:openTime / 1000.0), 
                    to_timestamp(:closeTime / 1000.0), :firstId, :lastId, :count, NOW()
                )
                ON CONFLICT (symbol) DO UPDATE SET
                    price_change = EXCLUDED.price_change,
                    price_change_percent = EXCLUDED.price_change_percent,
                    weighted_avg_price = EXCLUDED.weighted_avg_price,
                    prev_close_price = EXCLUDED.prev_close_price,
                    last_price = EXCLUDED.last_price,
                    last_qty = EXCLUDED.last_qty,
                    bid_price = EXCLUDED.bid_price,
                    bid_qty = EXCLUDED.bid_qty,
                    ask_price = EXCLUDED.ask_price,
                    ask_qty = EXCLUDED.ask_qty,
                    open_price = EXCLUDED.open_price,
                    high_price = EXCLUDED.high_price,
                    low_price = EXCLUDED.low_price,
                    volume = EXCLUDED.volume,
                    quote_volume = EXCLUDED.quote_volume,
                    open_time = EXCLUDED.open_time,
                    close_time = EXCLUDED.close_time,
                    first_id = EXCLUDED.first_id,
                    last_id = EXCLUDED.last_id,
                    trade_count = EXCLUDED.trade_count,
                    updated_at = NOW();
                """),
                stats_data
            )
            conn.commit()

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch ticker stats for {symbol}", exc_info=e)
    except SQLAlchemyError as e:
        logger.error(f"Database error inserting ticker stats for {symbol}", exc_info=e)
    
def get_klines(symbol, interval='15m'):
    """
    Fetches k-line/candlestick data and upserts it into the database without using pandas.
    """
    url = f'{base_url}/api/v3/klines'
    
    # Define the column names in the order they appear in the Binance API response
    kline_columns = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ]

    try:
        response = requests.get(url, params={'symbol': symbol, 'interval': interval})
        response.raise_for_status()
        kline_data_from_api = response.json()

        klines_to_insert = []
        # Each 'kline' in the response is a list of values
        for kline_record in kline_data_from_api:
            # Use zip to efficiently create a dictionary from the column names and the list of values
            kline_dict = dict(zip(kline_columns, kline_record))
            # Add the symbol to the dictionary, as it's not in the API's inner list
            kline_dict['symbol'] = symbol
            klines_to_insert.append(kline_dict)

        if not klines_to_insert:
            logger.warning(f"No k-line data found for {symbol} with interval {interval}")
            return

        logger.debug(f"Upserting {len(klines_to_insert)} k-lines for {symbol}")
        with engine.connect() as conn:
            conn.execute(
                sa.text("""
                    INSERT INTO public.klines (
                        symbol, open_time, open, high, low, close, volume,
                        close_time, quote_asset_volume, num_trades,
                        taker_buy_base_volume, taker_buy_quote_volume
                    ) VALUES (
                        :symbol, to_timestamp(:open_time / 1000.0), :open, :high, :low, :close, :volume,
                        to_timestamp(:close_time / 1000.0), :quote_asset_volume, :num_trades,
                        :taker_buy_base_volume, :taker_buy_quote_volume
                    )
                    ON CONFLICT (symbol, open_time) DO UPDATE SET
                        open = EXCLUDED.open,
                        high = EXCLUDED.high,
                        low = EXCLUDED.low,
                        close = EXCLUDED.close,
                        volume = EXCLUDED.volume,
                        close_time = EXCLUDED.close_time,
                        quote_asset_volume = EXCLUDED.quote_asset_volume,
                        num_trades = EXCLUDED.num_trades,
                        taker_buy_base_volume = EXCLUDED.taker_buy_base_volume,
                        taker_buy_quote_volume = EXCLUDED.taker_buy_quote_volume,
                        ingested_at = NOW();
                """),
                klines_to_insert  # Pass the entire list of dictionaries for a bulk operation
            )
            conn.commit()

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch k-lines for {symbol}", exc_info=e)
    except SQLAlchemyError as e:
        logger.error(f"Database error inserting k-lines for {symbol}", exc_info=e)

if __name__ == "__main__":
    for symbol in top_pairs:
        get_recent_trades(symbol)
        get_latest_prices(symbol)
        get_orderbook(symbol)
        get_ticker_stats_data(symbol)
        get_klines(symbol, interval='15m')