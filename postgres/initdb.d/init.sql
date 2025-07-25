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



ALTER TABLE public.recent_trades REPLICA IDENTITY FULL; -- Recommended for Debezium to provide the "before" state of a row on UPDATE and DELETE events.