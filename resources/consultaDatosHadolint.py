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

report = sys.argv[1]
user_par = sys.argv[2]
password_par = sys.argv[3]
host_par = sys.argv[4]
port_par = sys.argv[5]
database_par = sys.argv[6]
image = sys.argv[7]
tag = sys.argv[8]


f = open(report)

hadolint = json.load(f)



numtarget=len(hadolint)



vuln = { "vulnerabilities":[]}

execution = 0

def add_vulnerability(vuln_item):
    #print(vuln["vulnerabilities"])
    vuln["vulnerabilities"].append(vuln_item)
    
    
def fill_vulnerability():
    #Se calcula el numero total de nodos analizados
    for k in range(0, numtarget):
        #Se calcula el numero de vulnerabilidades que tiene el nodo actual
        try:
            vuln_item = {}
            try:
                vuln_item["line"]=hadolint[k]["line"]  
            except KeyError:
                vuln_item["line"]=None
            try:
                vuln_item["code"]=hadolint[k]["code"]
            except KeyError:
                vuln_item["code"]=None
            try:
                vuln_item["message"]=hadolint[k]["message"]
            except KeyError:
                vuln_item["message"]=None
            try:
                vuln_item["column"]=hadolint[k]["column"]
            except KeyError:
                vuln_item["column"]=None
            try:
                vuln_item["file"]=hadolint[k]["file"]
            except KeyError:
                vuln_item["file"]=None
            try:
                vuln_item["level"]=hadolint[k]["level"]
            except KeyError:
                vuln_item["level"]=None
                
            add_vulnerability(vuln_item)
        except KeyError:
            print("No existen vulnerabilidades para este nodo")
    

fill_vulnerability()



#Create DB connection

try:
    connection = psycopg2.connect(user= user_par,password= password_par,host= host_par,port= port_par, database= database_par)
    cursor = connection.cursor()
    totalvuln=len(vuln["vulnerabilities"])
    get_ejecucion = """SELECT MAX(execution) FROM hadolint WHERE image = %s AND tag = %s"""
    cursor.execute(get_ejecucion,(image,tag,))
    execution = [row[0] for row in cursor][0]
    if execution is None:
        execution = 1
    else:
        execution += 1

    for i in range(0, totalvuln):
        dt = datetime.now()
        dt = dt.replace(tzinfo=timezone.utc)
        postgres_insert_query = """ INSERT INTO hadolint (image, tag, line, code, message, columna, file, level, execution, insertiondate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """
        record_to_insert = (image,tag,vuln["vulnerabilities"][i]["line"],vuln["vulnerabilities"][i]["code"],vuln["vulnerabilities"][i]["message"],vuln["vulnerabilities"][i]["column"],vuln["vulnerabilities"][i]["file"],vuln["vulnerabilities"][i]["level"],execution,dt)
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





