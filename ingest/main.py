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


if __name__ == "__main__":
    for symbol in top_pairs:
        get_recent_trades(symbol)
