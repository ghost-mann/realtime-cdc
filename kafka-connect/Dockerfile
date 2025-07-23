# Start with Confluent's official Kafka Connect image, which includes 'confluent-hub'.
FROM confluentinc/cp-kafka-connect:7.5.0

# --- Part 1: Manually download and install the DataStax Apache Cassandra Sink Connector ---
# This sink connector is also downloaded from Maven Central.
ENV CASSANDRA_SINK_VERSION=1.7.3
RUN mkdir -p /usr/share/java/kafka-connect-cassandra-sink && \
    # Download the connector archive \
    wget -O /tmp/cassandra-sink.tar.gz https://github.com/datastax/kafka-sink/releases/download/${CASSANDRA_SINK_VERSION}/kafka-connect-cassandra-sink-${CASSANDRA_SINK_VERSION}.tar.gz && \
    # Extract the archive into our target directory, stripping the top-level folder
    tar -xvf /tmp/cassandra-sink.tar.gz -C /usr/share/java/kafka-connect-cassandra-sink --strip-components=1 && \
    # Clean up the downloaded file
    rm /tmp/cassandra-sink.tar.gz

# --- Part 2: Manually download and install the Debezium Connector ---
# Debezium connectors are downloaded from Maven Central.
# We set the version as an environment variable for easy updates.
ENV DEBEZIUM_VERSION=2.5.0.Final

# The plugin path is where Kafka Connect looks for connector JARs.
# In the Confluent images, this is /usr/share/java.
# We create a new subdirectory for our connector.
RUN mkdir -p /usr/share/java/debezium-connector-postgres && \
    # Download the connector archive
    wget -O /tmp/debezium.tar.gz https://repo1.maven.org/maven2/io/debezium/debezium-connector-postgres/${DEBEZIUM_VERSION}/debezium-connector-postgres-${DEBEZIUM_VERSION}-plugin.tar.gz && \
    # Extract the archive into our target directory
    tar -xvf /tmp/debezium.tar.gz -C /usr/share/java/debezium-connector-postgres && \
    # Clean up the downloaded file
    rm /tmp/debezium.tar.gz