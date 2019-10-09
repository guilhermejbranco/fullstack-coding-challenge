from sqlalchemy import create_engine, MetaData,Table, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
import config

# Change the values associated with the database connection in the config.py file.
engine = create_engine(config.GetConfig.DB_TYPE +
                       '://' + config.GetConfig.DB_USERNAME +
                       ':' + config.GetConfig.DB_PW +
                       '@' + config.GetConfig.DB_URL +
                       '/' + config.GetConfig.DB_NAME, convert_unicode=True)


metadata = MetaData(engine)

if not engine.dialect.has_table(engine, config.GetConfig.DB_TRANSLATIONS_TABLE_NAME):  # If table don't exist, Create.
    # Create a table with the appropriate Columns
    Table(config.GetConfig.DB_TRANSLATIONS_TABLE_NAME, metadata,
          Column('id', Integer, primary_key=True),
          Column('original_string', String(500), unique=False),
          Column('translated_string', String(500), unique=False),
          Column('status', String(50), unique=False),
          Column('source_language', String(50), unique=False),
          Column('target_language', String(50), unique=False),
          Column('uid', String(50), unique=True)
          )
    # Implement the creation
    metadata.create_all()

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


def init_db():
    metadata.create_all(bind=engine)