"""Orquesta la carga completa e idempotente de MongoDB y Neo4j."""
from src.etl.load_mongo import load_all as load_mongo
from src.etl.load_neo4j import load_all as load_neo4j


def seed():
    print("── Cargando MongoDB ──────────────────────────────")
    load_mongo()
    print("\n── Cargando Neo4j ────────────────────────────────")
    load_neo4j()
    print("\n✓ Seed completo")


if __name__ == "__main__":
    seed()
