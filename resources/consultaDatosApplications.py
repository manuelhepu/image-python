import regex as re
import os
import requests
import json
import time
import psycopg2
import sys
import pytz
from requests.auth import HTTPBasicAuth


env = sys.argv[1]
tegnology = sys.argv[2]
application = sys.argv[3]
user_par = sys.argv[4]
password_par = sys.argv[5]
host_par = sys.argv[6]
port_par = sys.argv[7]
database_par = sys.argv[8]


#Create DB connection

try:
    connection = psycopg2.connect(user= user_par,password= password_par,host= host_par,port= port_par, database= database_par)
    cursor = connection.cursor()

    get_ejecucion = """SELECT env FROM applications WHERE env = %s AND tegnology = %s AND application_name = %s"""
    cursor.execute(get_ejecucion,(env,tegnology,application,))
    execution = [row[0] for row in cursor][0]
    if execution is None:
        postgres_insert_query = """ INSERT INTO applications (env, tegnology, application_name) VALUES (%s, %s,%s) """
        record_to_insert = (env,tegnology,application)
        cursor.execute(postgres_insert_query, record_to_insert)
    else:
        print("Ya existe el registro.")
except (Exception, psycopg2.Error) as error:
    print("Failed to insert record into mobile table", error)

finally:
    # closing database connection.
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")