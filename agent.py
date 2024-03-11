import logging
import os

import oracledb
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from sqlalchemy import create_engine


def get_schema(_):
  return db.get_table_info()


def run_query(query):
  return db.run(query)


def create_oracle_engine():
  ORACLE_USER = os.getenv('ORACLE_USER')
  ORACLE_PASSWORD = os.getenv('ORACLE_PASSWORD')
  ORACLE_HOST_AND_PORT = os.getenv('ORACLE_HOST_AND_PORT')
  ORACLE_SERVICE_NAME = os.getenv('ORACLE_SERVICE_NAME')
  db_uri = "oracle+oracledb://{}:{}@{}?service_name={}".format(ORACLE_USER,
                                                               ORACLE_PASSWORD,
                                                               ORACLE_HOST_AND_PORT,
                                                               ORACLE_SERVICE_NAME)
  logging.info(f"Creating Oracle Engine for {db_uri}")
  # Enabling THICK mode in order to work with legacy encodings
  #oracledb.init_oracle_client(lib_dir="/Users/ou83mp/Developer/tools/instant_client")
  engine = create_engine(db_uri)
  return engine


logging.basicConfig(
  format='%(asctime)s %(levelname)-8s %(message)s',
  level=logging.INFO,
  datefmt='%Y-%m-%d %H:%M:%S')

load_dotenv()

ORACLE_SCHEMA = os.getenv('ORACLE_SCHEMA')

engine = create_oracle_engine()
logging.info("Created Engine ")
db = SQLDatabase(engine, schema=ORACLE_SCHEMA)
logging.info("Loaded DB")
schema = get_schema('empty')
logging.info("Loaded Schema")
with open('ingfos_schema.txt', 'w') as file:
  file.write(schema)

logging.info("Saved Schema on file")


llm = Ollama(model="llama2")

logging.info("Created llm")
agent_executor = create_sql_agent(llm, db=db, agent_type="zero-shot-react-description", verbose=True)

logging.info("Created agent")
agent_executor.invoke("How many requests do a customer execute on exit?")
