from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError, ArgumentError
from sqlalchemy.orm import sessionmaker
from utils.logging import logger


'''
This utililty allows us to establish one database connection via
sql alchemy and manage sessions (REMEMBER TO CLOSE SESSIONS WHEN OPENING THEM).

We also instantiated our declaritive base that we'll utilize in our models
when creating and replicating tables in our database.
'''
class DatabaseConfig:
    """
    Configuration class for the database. Allows connection setup and session management.
    """
    def __init__(self, db_url, debug):
        logger.info("Starting SQL Alchemy configuration...: ")
        self._session = None
        try:
            self._engine = create_engine(db_url, echo=debug)
            self._Session = sessionmaker(autoflush=False, bind=self._engine)
            # connection check
            connection = self._engine.connect()
            connection.close()
        except ArgumentError as err:
            logger.error(f"Invalid or missing database connection parameters: {err}")
            raise
        except OperationalError as err:
            logger.error(f"Database connection error: {err}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while configuring database: {e}")
            raise
        self._session_wrapper = self._SessionWrapper(self)
        logger.info(f"Completed SQL Alchemy configuration: {self._engine}")


    @property
    def session(self):
        """
        Return the session wrapper for session management.
        """
        return self._session_wrapper
    
    class _SessionWrapper:
        """
        Internal session wrapper for managing the database sessions.
        """
        def __init__(self, db):
            self._db = db
        
        def open(self):
            """
            Open a new database session or return the existing one.
            """
            if not self._db._session:
                self._db._session = self._db._Session()
            else: # if opening an already open session
                logger.warning(f"A session for {self._db._engine.url} is already open.")
            return self._db._session
        
        def close(self):
            """
            Close the current database session if it exists.
            """
            if self._db._session:
                self._db._session.close()
                self._db._session = None
            else: # if no session
                logger.warning("No session to close.")

def config_db(config):
    """
    Initialize and return the database configuration.
    Args:
        config (object): Configuration object with DB_URL and DEBUG properties.
    Returns:
        DatabaseConfig: Initialized database configuration.
    """
    return DatabaseConfig(config.DB_URL, config.DEBUG)