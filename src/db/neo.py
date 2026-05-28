from neo4j import GraphDatabase
from src.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

_driver = None


def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return _driver


def run(query, **params):
    with get_driver().session() as session:
        return list(session.run(query, **params))


def close():
    global _driver
    if _driver:
        _driver.close()
        _driver = None
