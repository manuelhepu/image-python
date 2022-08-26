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
env = sys.argv[9]
tegnology = sys.argv[10]
application_name = sys.argv[11]


f = open(report)

trivy = json.load(f)

numtarget=len(trivy["Results"])

#image_nueva=trivy["ArtifactName"].split(sep='/')

#image = image_nueva[3]




vuln = { "vulnerabilities":[]}

execution = 0



def add_vulnerability(vuln_item):
    vuln["vulnerabilities"].append(vuln_item)




def fill_vulnerability():
    #Se calcula el numero total de nodos analizados
    for k in range(0, 1):
        #Se calcula el numero de vulnerabilidades que tiene el nodo actual
            try:
                numvuln=len(trivy["Results"][k]["Vulnerabilities"])
                for i in range(0, numvuln):
                    vuln_item = {}
                    try:
                        vuln_item["Target"]=trivy["Results"][k]["Target"]
                    except KeyError:
                        vuln_item["Target"]=None
                    try:
                        vuln_item["Type"]=trivy["Results"][k]["Type"]
                    except KeyError:
                        vuln_item["Type"]=None
                    try:
                        vuln_item["ID"]=trivy["Results"][k]["Vulnerabilities"][i]["VulnerabilityID"]
                    except KeyError:
                        vuln_item["ID"]=None
                    try:
                        vuln_item["PkgName"]=trivy["Results"][k]["Vulnerabilities"][i]["PkgName"]
                    except KeyError:
                        vuln_item["PkgName"]=None
                    try:
                        vuln_item["InstalledVersion"]=trivy["Results"][k]["Vulnerabilities"][i]["InstalledVersion"]
                    except KeyError:
                        vuln_item["InstalledVersion"]=None
                    try:
                        vuln_item["FixedVersion"]=trivy["Results"][k]["Vulnerabilities"][i]["FixedVersion"]
                    except KeyError:
                        vuln_item["FixedVersion"]=None
                    try:
                        vuln_item["Severity"]=trivy["Results"][k]["Vulnerabilities"][i]["Severity"]
                    except KeyError:
                        vuln_item["Severity"]=None
                    try:
                        vuln_item["PrimaryURL"]=trivy["Results"][k]["Vulnerabilities"][i]["PrimaryURL"]
                    except KeyError:
                        vuln_item["PrimaryURL"]=None
                    add_vulnerability(vuln_item)
            except KeyError:
                print("No existen vulnerabilidades para este nodo")
    

fill_vulnerability()

#Create DB connection

try:
    connection = psycopg2.connect(user= user_par,password= password_par,host= host_par,port= port_par, database= database_par)
    cursor = connection.cursor()
    totalvuln=len(vuln["vulnerabilities"])
    get_ejecucion = """SELECT id_application FROM applications WHERE env = %s AND tegnology = %s AND application_name = %s"""
    cursor.execute(get_ejecucion,(env,tegnology,application_name))
    execution = [row[0] for row in cursor][0]
    if execution is None:
        print("No existe la app.")
    else:
        id_application = execution
    
    
    
    
    get_ejecucion = """SELECT MAX(execution) FROM trivy_image WHERE id_application = %s"""
    cursor.execute(get_ejecucion,(id_application,))
    execution = [row[0] for row in cursor][0]
    if execution is None:
        execution = 1
    else:
        execution += 1

    for i in range(0, totalvuln):
        dt = datetime.now()
        dt = dt.replace(tzinfo=timezone.utc)
        postgres_insert_query = """ INSERT INTO trivy_image (id_application, image, tag, target, type, vid, package, installed, fixed, severity, url, execution, insertiondate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """
        record_to_insert = (id_application, image, tag, vuln["vulnerabilities"][i]["Target"],vuln["vulnerabilities"][i]["Type"],vuln["vulnerabilities"][i]["ID"],vuln["vulnerabilities"][i]["PkgName"],vuln["vulnerabilities"][i]["InstalledVersion"],vuln["vulnerabilities"][i]["FixedVersion"],vuln["vulnerabilities"][i]["Severity"],vuln["vulnerabilities"][i]["PrimaryURL"],execution,dt)
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