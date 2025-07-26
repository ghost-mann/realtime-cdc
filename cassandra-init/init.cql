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

