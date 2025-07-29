# realtime-cdc-poc

# Spin up containers

    docker compose up --build

# kafka-connector

## postgres source 

### Register

    curl -X POST http://localhost:8083/connectors \
    -H "Content-Type: application/json" \
    --data @connectors/postgres-source.json | jq

### Deregister

    curl -X DELETE http://localhost:8083/connectors/postgres-source

## cassandra sink

### Register

    curl -X POST http://localhost:8083/connectors \
    -H "Content-Type: application/json" \
    --data @connectors/cassandra-sink.json | jq

### Deregister

    curl -X DELETE http://localhost:8083/connectors/cassandra-sink | jq

# kafka

## Watch kafka topic

    docker-compose exec kafka kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic trades.public.recent_trades \
    --from-beginning \
    --property print.key=true \
    --property key.separator=" | "

# postgres

    docker-compose exec postgres psql -U postgres -d trades

## Ingest create event

    INSERT INTO public.recent_trades (symbol, price, quote_qty, qty, is_buyer_maker, is_best_match) VALUES ('AAPL', 150.25, 100, 1, true, true);

## Ingest update event

    UPDATE public.recent_trades SET price = 151.00 WHERE id = 1;

## Delete event

    DELETE FROM public.recent_trades WHERE id = 1;

# cassandra

    docker compose exec --interactive cassandra cqlsh

    DESCRIBE KEYSPACES;

    USE trades_keyspace;

    SELECT * FROM trades_keyspace.recent_trades;

# Troubleshooting

## List connectors

    curl -s http://localhost:8083/connectors | jq  

## List plugins

    curl http://localhost:8083/connector-plugins | jq
