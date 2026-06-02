"""
scripts/setup_kafka_topics.py

Provisions the 8 core Kafka topics required by Phase 0 on a Redpanda Cloud
Serverless cluster. Credentials are read exclusively from environment variables
(never hard-coded).

Usage:
    python -m scripts.setup_kafka_topics

Required env vars (set via Doppler or .env):
    KAFKA_BOOTSTRAP_SERVERS  e.g. <cluster>.prd.cloud.redpanda.com:9092
    KAFKA_SASL_USERNAME      Redpanda service-account username
    KAFKA_SASL_PASSWORD      Redpanda service-account password
"""

import os
import sys
from dotenv import load_dotenv
from confluent_kafka.admin import AdminClient, NewTopic, KafkaException

load_dotenv()

BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "")
SASL_USERNAME = os.getenv("KAFKA_SASL_USERNAME", "")
SASL_PASSWORD = os.getenv("KAFKA_SASL_PASSWORD", "")


def _build_admin_client() -> AdminClient:
    """Build an AdminClient with SASL/SCRAM-256 auth when credentials exist."""
    config: dict[str, str] = {"bootstrap.servers": BOOTSTRAP_SERVERS}

    if SASL_USERNAME and SASL_PASSWORD:
        config.update(
            {
                "security.protocol": "SASL_SSL",
                "sasl.mechanisms": "SCRAM-SHA-256",
                "sasl.username": SASL_USERNAME,
                "sasl.password": SASL_PASSWORD,
            }
        )
        print("[auth] Using SASL/SCRAM-256 authentication.")
    else:
        print(
            "[warn] KAFKA_SASL_USERNAME / KAFKA_SASL_PASSWORD not set. "
            "Connecting without authentication (works only for local dev)."
        )

    return AdminClient(config)


# Topic definitions — partitions and retention match Phase 0 spec exactly.
TOPICS: list[dict] = [
    {"name": "task.assigned",               "partitions": 6, "retention_days": 7},
    {"name": "deliverable.ready",           "partitions": 6, "retention_days": 7},
    {"name": "deliverable.approved",        "partitions": 6, "retention_days": 7},
    {"name": "client.health.alert",         "partitions": 3, "retention_days": 30},
    {"name": "regulatory.update.healthcare","partitions": 3, "retention_days": 90},
    {"name": "regulatory.update.logistics", "partitions": 3, "retention_days": 90},
    {"name": "regulatory.update.legal",     "partitions": 3, "retention_days": 90},
    {"name": "regulatory.update.edtech",    "partitions": 3, "retention_days": 90},
    {"name": "mas.health.report",           "partitions": 1, "retention_days": 365},
]


def main() -> None:
    if not BOOTSTRAP_SERVERS:
        print("ERROR: KAFKA_BOOTSTRAP_SERVERS is not set. Aborting.")
        sys.exit(1)

    admin = _build_admin_client()

    new_topics = [
        NewTopic(
            t["name"],
            num_partitions=t["partitions"],
            replication_factor=3,
            config={"retention.ms": str(t["retention_days"] * 24 * 60 * 60 * 1_000)},
        )
        for t in TOPICS
    ]

    print(f"Provisioning {len(new_topics)} topics on {BOOTSTRAP_SERVERS} …")
    print(f"Provisioning {len(new_topics)} topics on {BOOTSTRAP_SERVERS} ...")
    futures = admin.create_topics(new_topics, request_timeout=30)

    success = True
    for topic_name, future in futures.items():
        try:
            future.result()
            print(f"  [OK] {topic_name}")
        except KafkaException as exc:
            err_str = str(exc).lower()
            if "already exists" in err_str:
                print(f"  [SKIP] {topic_name} - already exists")
            elif "authorization" in err_str or "auth" in err_str:
                print(
                    f"  [FAIL] {topic_name} - Authorization failed.\n"
                    f"         Ensure the Redpanda user '{SASL_USERNAME}' has CREATE/DESCRIBE\n"
                    f"         ACLs on topic '{topic_name}'. In Redpanda Cloud Console go to:\n"
                    f"         Security -> ACLs -> Add ACL (Principal: {SASL_USERNAME}, \n"
                    f"         Resource: topic:{topic_name}, Ops: All).\n"
                    f"         Or grant a wildcard ACL on all topics for this service account."
                )
                success = False
            else:
                print(f"  [FAIL] {topic_name} - {exc}")
                success = False

    if not success:
        print("\nOne or more topics failed to create. Check credentials and try again.")
        sys.exit(1)

    print("\nKafka topic provisioning complete. [OK]")


if __name__ == "__main__":
    main()
