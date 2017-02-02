# tasks.py

from celery_config import app
import time
import logging
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('tasks.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

CONN_STRING = 'postgresql://test_user:med@10.20.20.12:5432/etl'
ALLOWED_QUERY_KEYS = {'cust_id', 'lname', 'fname', 'state', 'gender'}

@app.task(name='ins00.add')
def add(x, y):
    time.sleep(5) # sleep for a while before the gigantic addition task!
    return x + y

@app.task(name='ins00.read_db_data')
def read_db_data(lname_wanted='Aarick'):
    #CONN_STRING = 'postgresql://test_user:med@10.20.20.12:5432/etl'
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
    stmt = text("SELECT id, data "
                "FROM ins00 WHERE LOWER(data->>'lname')=LOWER(:lname)")
    stmt = stmt.columns(Insurance.id, Insurance.data)

    #LNAME_WANTED = 'Aarick'
    #LNAME_WANTED = 'Aaron'
    #LNAME_WANTED = 'Abad'

    LNAME_WANTED = lname_wanted
    logger.info('looking up by last name: {}'.format(LNAME_WANTED))

    insurances = session.query(Insurance).\
                 from_statement(stmt).params(lname=LNAME_WANTED).all()
    results = []
    for ins in insurances:    
        results.append('{} {} {}<br>\n'.format(ins.data['fname'], ins.data['lname'], ins.data['ssn']))
    return ''.join(results)

def generate_query_text(kwargs):
    results = []
    results.append("SELECT id, data FROM ins00 WHERE ")
    for key, value in kwargs.items():
        if key in ALLOWED_QUERY_KEYS:
            results.append("LOWER(data->>'{}')=LOWER('{}') ".format(key, value))
            results.append("AND ")
    return ''.join(results[:-1])

@app.task(name='ins00.flex_find_data')
def flex_find_data(**kwargs):
    #CONN_STRING = 'postgresql://test_user:med@10.20.20.12:5432/etl'
    Base = automap_base()

    # engine, assume it has a table 'ins00' set up
    engine = create_engine(CONN_STRING)

    # reflect the tables
    Base.prepare(engine, reflect=True)

    # mapped classes are now created with names by default
    # matching that of the table name.
    Insurance = Base.classes.ins00
    session = Session(engine)

    my_sql = generate_query_text(kwargs)
    logger.info('..db looking up with query: {}'.format(my_sql))
    from sqlalchemy import text
    stmt = text(my_sql)
    stmt = stmt.columns(Insurance.id, Insurance.data)
    insurances = session.query(Insurance).from_statement(stmt).all()
    results = []
    results.append('The following keys are allowed in search: {}'.format(','.join(ALLOWED_QUERY_KEYS)))
    for ins in insurances:
        results.append('{} {} {}<br>\n'.format(ins.data['fname'], ins.data['lname'], ins.data['ssn']))

    return ''.join(results)