CREATE TABLE public.recent_trades (
      id SERIAL PRIMARY KEY,
      price VARCHAR(255) NOT NULL,
      qty VARCHAR(255) NOT NULL,
      quote_qty VARCHAR(255) NOT NULL,
      is_buyer_maker BOOLEAN NOT NULL,
      is_best_match BOOLEAN NOT NULL,
      symbol VARCHAR(255) NOT NULL,
      created_at TIMESTAMPTZ DEFAULT NOW(),
      modified_at TIMESTAMPTZ DEFAULT NOW()
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


ALTER TABLE public.recent_trades REPLICA IDENTITY FULL; -- Recommended for Debezium to provide the "before" state of a row on UPDATE and DELETE events.