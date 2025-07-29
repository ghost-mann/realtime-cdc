-- This script will be executed by our temporary init container.

-- Create the keyspace for our application data.
-- The replication strategy is simple because we have a single-node cluster.
CREATE KEYSPACE IF NOT EXISTS trades_keyspace
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

-- Create the target table. The structure should match the data
-- we expect to receive from the Kafka topic.
CREATE TABLE IF NOT EXISTS trades_keyspace.recent_trades (
    id INT PRIMARY KEY,
    price TEXT,
    qty TEXT,
    quote_qty TEXT,
    time INT,
    is_buyer_maker BOOLEAN,
    is_best_match BOOLEAN,
    symbol TEXT,
    created_at TIMESTAMP,
    modified_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trades_keyspace.latest_prices (
    symbol TEXT PRIMARY KEY,
    price TEXT,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trades_keyspace.order_book (
    id BIGINT PRIMARY KEY,
    symbol TEXT,
    last_update_id BIGINT,
    side TEXT, -- 'bid' or 'ask'
    price DECIMAL,
    quantity DECIMAL
);

CREATE TABLE IF NOT EXISTS ticker_stats (
    symbol TEXT PRIMARY KEY,
    price_change DECIMAL,
    price_change_percent DECIMAL,
    weighted_avg_price DECIMAL,
    prev_close_price DECIMAL,
    last_price DECIMAL,
    last_qty DECIMAL,
    bid_price DECIMAL,
    bid_qty DECIMAL,
    ask_price DECIMAL,
    ask_qty DECIMAL,
    open_price DECIMAL,
    high_price DECIMAL,
    low_price DECIMAL,
    volume DECIMAL,
    quote_volume DECIMAL,
    open_time TIMESTAMP,
    close_time TIMESTAMP,
    first_id BIGINT,
    last_id BIGINT,
    trade_count BIGINT,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS klines (
    symbol TEXT,
    open_time TIMESTAMP,
    open DECIMAL,
    high DECIMAL,
    low DECIMAL,
    close DECIMAL,
    volume DECIMAL,
    close_time TIMESTAMP,
    quote_asset_volume DECIMAL,
    num_trades BIGINT,
    taker_buy_base_volume DECIMAL,
    taker_buy_quote_volume DECIMAL,
    ingested_at TIMESTAMP,
    PRIMARY KEY (symbol, open_time)
) WITH CLUSTERING ORDER BY (open_time DESC);

