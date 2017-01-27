# add.py

from celery_config import app
import time

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

@app.task(name='ins00.add')
def add(x, y):
    time.sleep(5) # sleep for a while before the gigantic addition task!
    return x + y

@celery.task(name='ins00.read_db_data')
def read_db_data(lname_wanted='Aarick'):
    CONN_STRING = 'postgresql://test_user:med@luckystardb:5432/etl'
    Base = automap_base()

    # engine, assume it has a table 'ins00' set up
    engine = create_engine(CONN_STRING)

    # reflect the tables
    Base.prepare(engine, reflect=True)

    # mapped classes are now created with names by default
    # matching that of the table name.
    Insurance = Base.classes.ins00
    session = Session(engine)

    from sqlalchemy import text
    stmt = text("SELECT data->>'lname', data->>'fname'"
                "FROM ins00 where data->>'lname'=:lname")
    stmt = stmt.columns(Insurance.lname, Insurance.fname)

    #LNAME_WANTED = 'Aarick'
    #LNAME_WANTED = 'Aaron'
    #LNAME_WANTED = 'Abad'

    LNAME_WANTED = lname_wanted

    insurances = session.query(Insurance).\
                 from_statement(stmt).params(lname=LNAME_WANTED).all():
    
    results = []
    for ins in insurances:    
        results.append('{} {}\n'.format(ins.fname, ins.lname))
    return ','.join(results)