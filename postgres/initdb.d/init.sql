CREATE TABLE IF NOT EXISTS public.recent_trades (
    id BIGINT PRIMARY KEY, -- The unique trade ID from Binance
    symbol VARCHAR(20) NOT NULL,
    price NUMERIC NOT NULL,
    qty NUMERIC NOT NULL,
    quote_qty NUMERIC NOT NULL,
    time TIMESTAMPTZ NOT NULL, -- The time of the trade
    is_buyer_maker BOOLEAN NOT NULL,
    is_best_match BOOLEAN NOT NULL
);

CREATE TABLE public.latest_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    price NUMERIC(20, 8) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.order_book (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    last_update_id BIGINT NOT NULL,
    side VARCHAR(4) NOT NULL, -- Stores 'bid' or 'ask'
    price NUMERIC NOT NULL,
    quantity NUMERIC NOT NULL,
    -- It's good practice to record when the row was inserted into our database
    ingested_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS public.ticker_stats (
    symbol VARCHAR(20) PRIMARY KEY,
    price_change NUMERIC,
    price_change_percent NUMERIC,
    weighted_avg_price NUMERIC,
    prev_close_price NUMERIC,
    last_price NUMERIC,
    last_qty NUMERIC,
    bid_price NUMERIC,
    bid_qty NUMERIC,
    ask_price NUMERIC,
    ask_qty NUMERIC,
    open_price NUMERIC,
    high_price NUMERIC,
    low_price NUMERIC,
    volume NUMERIC,
    quote_volume NUMERIC,
    open_time TIMESTAMPTZ,
    close_time TIMESTAMPTZ,
    first_id BIGINT,
    last_id BIGINT,
    trade_count BIGINT, -- Renamed from 'count' to avoid SQL keyword conflicts
    -- Add a timestamp to know when the stats were last updated in our system
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table 5: klines
-- Stores the k-line (candlestick) data.
-- A composite primary key on symbol and open_time ensures each candle is unique
-- and allows for efficient upserting (INSERT ... ON CONFLICT).

CREATE TABLE IF NOT EXISTS public.klines (
    symbol VARCHAR(20) NOT NULL,
    open_time TIMESTAMPTZ NOT NULL,
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    volume NUMERIC NOT NULL,
    close_time TIMESTAMPTZ NOT NULL,
    quote_asset_volume NUMERIC NOT NULL,
    num_trades BIGINT NOT NULL,
    taker_buy_base_volume NUMERIC NOT NULL,
    taker_buy_quote_volume NUMERIC NOT NULL,
    ingested_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (symbol, open_time)
);

-- An index to speed up queries fetching klines by their close time.
CREATE INDEX IF NOT EXISTS idx_klines_symbol_close_time ON public.klines (symbol, close_time DESC);


ALTER TABLE public.recent_trades REPLICA IDENTITY FULL; -- Recommended for Debezium to provide the "before" state of a row on UPDATE and DELETE events.