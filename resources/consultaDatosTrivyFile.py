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
image =  sys.argv[7]
tag =  sys.argv[8]

f = open(report)

trivy = json.load(f)

#numtarget=len(trivy["Results"])


vuln = { "vulnerabilities":[]}

execution = 0


def add_vulnerability(vuln_item):
    vuln["vulnerabilities"].append(vuln_item)




def fill_vulnerability():
    #Se calcula el numero total de nodos analizados
    for k in range(0, 1):
        #Se calcula el numero de vulnerabilidades que tiene el nodo actual
            try:

                numvuln=len(trivy["Results"][k]["Misconfigurations"])
                print(numvuln)
                for i in range(0, numvuln):
                    vuln_item = {}
                    try:
                        vuln_item["Target"]=trivy["Results"][k]["Target"]
                    except KeyError:
                        vuln_item["Target"]=None
                    try:
                        vuln_item["Class"]=trivy["Results"][k]["Class"]
                    except KeyError:
                        vuln_item["Class"]=None
                    try:
                        vuln_item["Successes"]=trivy["Results"][k]["MisconfSummary"]["Successes"]
                    except KeyError:
                        vuln_item["Successes"]=None
                    try:
                        vuln_item["Failures"]=trivy["Results"][k]["MisconfSummary"]["Failures"]
                    except KeyError:
                        vuln_item["Failures"]=None
                    try:
                        vuln_item["Exceptions"]=trivy["Results"][k]["MisconfSummary"]["Exceptions"]
                    except KeyError:
                        vuln_item["Exceptions"]=None
                    try:
                        vuln_item["Type"]=trivy["Results"][k]["Misconfigurations"][i]["Type"]
                    except KeyError:
                        vuln_item["Type"]=None
                    try:
                        vuln_item["ID"]=trivy["Results"][k]["Misconfigurations"][i]["ID"]
                    except KeyError:
                        vuln_item["ID"]=None
                    try:
                        vuln_item["Title"]=trivy["Results"][k]["Misconfigurations"][i]["Title"]
                    except KeyError:
                        vuln_item["Title"]=None
                    try:
                        vuln_item["Description"]=trivy["Results"][k]["Misconfigurations"][i]["Description"]
                    except KeyError:
                        vuln_item["Description"]=None
                    try:
                        vuln_item["Message"]=trivy["Results"][k]["Misconfigurations"][i]["Message"]
                    except KeyError:
                        vuln_item["Message"]=None
                        
                    try:
                        vuln_item["Resolution"]=trivy["Results"][k]["Misconfigurations"][i]["Resolution"]
                    except KeyError:
                        vuln_item["Resolution"]=None
                    try:
                        vuln_item["Severity"]=trivy["Results"][k]["Misconfigurations"][i]["Severity"]
                    except KeyError:
                        vuln_item["Severity"]=None
                    try:
                        vuln_item["PrimaryURL"]=trivy["Results"][k]["Misconfigurations"][i]["PrimaryURL"]
                    except KeyError:
                        vuln_item["PrimaryURL"]=None
                    #print("Se va a añadir "+vuln_item["Target"])
                    add_vulnerability(vuln_item)
            except KeyError:
                print("No existen vulnerabilidades para este nodo")
    

fill_vulnerability()

#Create DB connection

try:
    connection = psycopg2.connect(user= user_par,password= password_par,host= host_par,port= port_par, database= database_par)
    cursor = connection.cursor()
    totalvuln=len(vuln["vulnerabilities"])
    get_ejecucion = """SELECT MAX(execution) FROM trivy_file WHERE image = %s AND tag = %s"""
    cursor.execute(get_ejecucion,(image,tag,))
    execution = [row[0] for row in cursor][0]
    if execution is None:
        execution = 1
    else:
        execution += 1

    for i in range(0, totalvuln):
        dt = datetime.now()
        dt = dt.replace(tzinfo=timezone.utc)
        postgres_insert_query = """ INSERT INTO trivy_file (image, tag, target, class, succes, failures, exceptions, type, id_vul, title, description, message, resolution, severity, url, execution, insertiondate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """
        record_to_insert = (image, tag, vuln["vulnerabilities"][i]["Target"],vuln["vulnerabilities"][i]["Class"],vuln["vulnerabilities"][i]["Successes"],vuln["vulnerabilities"][i]["Failures"],vuln["vulnerabilities"][i]["Exceptions"],vuln["vulnerabilities"][i]["Type"],vuln["vulnerabilities"][i]["ID"],vuln["vulnerabilities"][i]["Title"],vuln["vulnerabilities"][i]["Description"],vuln["vulnerabilities"][i]["Message"], vuln["vulnerabilities"][i]["Resolution"], vuln["vulnerabilities"][i]["Severity"], vuln["vulnerabilities"][i]["PrimaryURL"],execution,dt)
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