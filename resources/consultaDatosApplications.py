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
technology = sys.argv[2]
application = sys.argv[3]
user_par = sys.argv[4]
password_par = sys.argv[5]
host_par = sys.argv[6]
port_par = sys.argv[7]
database_par = sys.argv[8]



try:
    connection = psycopg2.connect(user= user_par,password= password_par,host= host_par,port= port_par, database= database_par)
    cursor = connection.cursor()

    get_ejecucion = """SELECT * FROM applications WHERE env = %s AND technology = %s AND application_name = %s"""
    cursor.execute(get_ejecucion,(env,technology,application))
    exist= False
    for row in cursor:
        exist = True


    
    if exist == False:
        postgres_insert_query = """INSERT INTO applications (env, technology, application_name) VALUES (%s, %s, %s) """
        record_to_insert = (env,technology,application)
        cursor.execute(postgres_insert_query, record_to_insert)
        try:
            connection.commit()
        except (Exception, psycopg2.Error) as error:
            print("Ha fallado el insert")
        print("Insert realizado.")
    else:
        print("Ya existe la app.")
except (Exception, psycopg2.Error) as error:
    print("Failed to insert record into applications table", error)

finally:
    # closing database connection.
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
