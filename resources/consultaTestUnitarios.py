import regex as re
import os
import requests
import json
import time
import psycopg2
import sys
import pytz
import xml.etree
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone

#report = sys.argv[1]

rootdir = "./target/surefire-reports/"

reports = []

regexp = re.compile('.*Test.*.xml')
for root, dirs, files in os.walk(rootdir):
    for file in files:
        if regexp.match(file):
            print(file)
            reports.append(file)

name = ""
unit_tests = 0
f_unit_tests = 0
e_unit_tests = 0
s_unit_tests = 0
execution = 0
ns = 'http://maven.apache.org/POM/4.0.0'

pom = ET.parse("./pom.xml")
name = pom.getroot().find("{%s}name" % ns).text


for i in reports:
    tree = ET.parse("target/surefire-reports/"+ i)
    root = tree.getroot()
    for child in root:
        for child_two in child:
            if child_two.tag == "failure":
                f_unit_tests += 1
            elif child_two.tag == "error":
                e_unit_tests += 1
            elif child_two.tag == "skipped":
                s_unit_tests += 1
    unit_tests += len(tree.findall('testcase'))

print("Hay "+ repr(unit_tests) +" tests unitarios")
print("Hay "+ repr(f_unit_tests) +" test fallidos")

#Create DB connection

try:
    connection = psycopg2.connect(user="admin",password="admin",host="192.168.1.50",port=5432, database="grafana")
    cursor = connection.cursor()
    get_ejecucion = """SELECT MAX(execution) FROM test_unit WHERE project = %s"""
    cursor.execute(get_ejecucion,(name,))
    execution = [row[0] for row in cursor][0]
    if execution is None:
        execution = 1
    else:
        execution += 1
        
    dt = datetime.now()
    dt = dt.replace(tzinfo=timezone.utc)
    postgres_insert_query = """ INSERT INTO test_unit (project, unit_tests, f_unit_tests, e_unit_tests, s_unit_tests, execution, insertiondate) VALUES (%s,%s,%s,%s,%s,%s,%s) """
    record_to_insert = (name,unit_tests, f_unit_tests, e_unit_tests, s_unit_tests, execution, dt)
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