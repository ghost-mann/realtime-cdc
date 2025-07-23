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

ALTER TABLE public.recent_trades REPLICA IDENTITY FULL; -- Recommended for Debezium to provide the "before" state of a row on UPDATE and DELETE events.