from __future__ import absolute_import

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tests.models import Base


def pytest_addoption(parser):
    parser.addoption(
        "--neo4j_uri", action="store",
        default="temp://",
        help=("URI for establishing a connection to neo4j."
        "See the docs for valid URIs"))

    parser.addoption(
        "--db_connection", action="store",
        default="mysql://localhost/test_taal",
        help="Sqlalchemy connection string"
    )


@pytest.fixture
def storage(request):
    from kaiso.persistence import Storage

    neo4j_uri = request.config.getoption('neo4j_uri')
    storage = Storage(neo4j_uri)
    storage.delete_all_data()
    storage.initialize()
    return storage


@pytest.fixture
def session(request):
    connection_string = request.config.getoption('db_connection')

    def drop_and_recreate_db():
        server, db_name = connection_string.rsplit('/', 1)
        engine = create_engine(server)
        query = 'DROP DATABASE {0}; CREATE DATABASE {0}'.format(db_name)
        engine.execute(query)


    engine = create_engine(connection_string)
    session_cls = sessionmaker(bind=engine)
    drop_and_recreate_db()
    Base.metadata.create_all(engine)
    session = session_cls()

    def teardown():
        session.close()

    request.addfinalizer(teardown)
    return session
