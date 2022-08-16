import regex as re
import os
import requests
import json
import time
import psycopg2
import sys
import pytz
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone

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

    get_ejecucion = """SELECT env FROM applications WHERE env = %s"""
    
    
    
    cursor.execute(get_ejecucion,(env,))
    execution = [row[0] for row in cursor][0]
    if execution is None:
        execution = 1
    else:
        execution += 1

    for i in range(0, totalvuln):
        dt = datetime.now()
        dt = dt.replace(tzinfo=timezone.utc)
        postgres_insert_query = """ INSERT INTO trivi_image (image, target, type, vid, package, installed, fixed, severity, url, execution, insertiondate) VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """
        record_to_insert = (image, vuln["vulnerabilities"][i]["Target"],vuln["vulnerabilities"][i]["Type"],vuln["vulnerabilities"][i]["ID"],vuln["vulnerabilities"][i]["PkgName"],vuln["vulnerabilities"][i]["InstalledVersion"],vuln["vulnerabilities"][i]["FixedVersion"],vuln["vulnerabilities"][i]["Severity"],vuln["vulnerabilities"][i]["PrimaryURL"],execution,dt)
        cursor.execute(postgres_insert_query, record_to_insert)
        try:
            connection.commit()
        except (Exception, psycopg2.Error) as error:
            print("Ha fallado el insert")
    print("Todo ha ido bien")
except (Exception, psycopg2.Error) as error:
    print("Failed to insert record into mobile table", error)

finally:
    # closing database connection.
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")