

# CREATE DATABASE EOVSA_flare_list_wiki_db;

# USE EOVSA_flare_list_wiki_db;

# # Let's say we create a database like this:
# CREATE TABLE `EOVSA_flare_list_wiki_tb` (
#   `Id` int(11) NOT NULL AUTO_INCREMENT,
#   `Flare_ID` BIGINT NOT NULL,
#   `Flare_class` varchar(5) NULL,
#   `EO_tstart` double NOT NULL,
#   `EO_tpeak` double NOT NULL,
#   `EO_tend` double NOT NULL,
#   `EO_xcen` float NULL,
#   `EO_ycen` float NULL,
#   `depec_file` varchar(30) NULL,
#   PRIMARY KEY (`Id`)
# );


# show columns from EOVSA_flare_list_wiki_tb;

# SELECT * FROM EOVSA_flare_list_wiki_tb;

# drop table EOVSA_flare_list_wiki_tb;





#####==================================================get flare_id_exist from mySQL
import mysql.connector
import os

connection = mysql.connector.connect(
    host = os.getenv('FLARE_DB_HOST'),
    database = os.getenv('FLARE_DB_DATABASE'),
    user = os.getenv('FLARE_DB_USER'),
    password = os.getenv('FLARE_DB_PASSWORD')
)

cursor = connection.cursor()

cursor.execute("SELECT Flare_ID FROM EOVSA_flare_list_wiki_tb")
flare_id_exist = cursor.fetchall()

cursor.close()
connection.close()




#####==================================================
import mysql.connector
from astropy.time import Time
import numpy as np
import sys
from datetime import datetime
import pandas as pd

# Connect to the database and get a cursor to access it:
cnxn = mysql.connector.connect(user='root', passwd='C@l1b4Me', host='localhost', database='EOVSA_flare_list_wiki_db')
# cnxn = mysql.connector.connect(user='Python3', passwd='Py+h0nUser', host='localhost', database='flare_test')

cursor = cnxn.cursor()
table = 'EOVSA_flare_list_wiki_tb'

# Write to the database (add records)
# Assume a database that mirrors the .csv file (first two lines below):
#    Flare_ID,Date,Time,flare_class,EO_tstart,EO_tpeak,EO_tend,EO_xcen,EO_ycen
#    20190415193100,2019-04-15,19:31:00,B3.3,2019-04-15 19:30:04,2019-04-15 19:32:21,2019-04-15 19:33:10,519.1,152.3
# The Flare_ID is automatic (just incremented from 1), so is not explicitly written.  Also, separating Date and Time doesn't make sense, so combine into a single Date:

columns = ['Flare_ID', 'Flare_class', 'EO_tstart', 'EO_tpeak', 'EO_tend', 'EO_xcen', 'EO_ycen', 'depec_file']
columns = ['Flare_ID', 'Flare_class', 'EO_tstart', 'EO_tpeak', 'EO_tend', 'depec_file']

values = []



#####==================================================
file_path = '/data1/xychen/flaskenv/EOVSA_flare_list_from_wiki_sub.csv'#/data1/xychen/flaskenv/EOVSA_flare_list_from_wiki.csv
df = pd.read_csv(file_path)

flare_id = df['Flare_ID']
dates = df['Date']
times = df['Time (UT)']
EO_tstart = df['EO_tstart']
EO_tpeak = df['EO_tpeak']
EO_tend = df['EO_tend']
GOES_class = df['flare_class']
# EO_xcen = np.nan_to_num(df['EO_xcen'], nan=0.0)
# EO_ycen = np.nan_to_num(df['EO_ycen'], nan=0.0)

# EO_xcen = df['EO_xcen']
# EO_ycen = df['EO_ycen']

depec_file = df['depec_file']


##=========================
for i in range(len(flare_id)):
  if not any(int(flare_id[i]) == existing_flare_id[0] for existing_flare_id in flare_id_exist):
    date = Time(dates[i]+' '+times[i]).jd
    # newlist = [int(flare_id[i]), GOES_class[i], Time(EO_tstart[i]).jd, Time(EO_tpeak[i]).jd, Time(EO_tend[i]).jd, EO_xcen[i], EO_ycen[i], depec_file[i]]
    newlist = [int(flare_id[i]), GOES_class[i], Time(EO_tstart[i]).jd, Time(EO_tpeak[i]).jd, Time(EO_tend[i]).jd, depec_file[i]]

    values.append(newlist)
    print("Update for ", int(flare_id[i]))



values = [[None if pd.isna(val) else val for val in sublist] for sublist in values]


# You can also create a list of lists of values, i.e. values.append([newlist]) for use with executemany()
# Create a "put_query" string from the column headings
put_query = 'insert ignore into '+table+' ('+','.join(columns)+') values ('+('%s,'*len(columns))[:-1]+')'


# The put_query will look like this:
# 'insert ignore into flare_list (Date,flare_class,EO_tstart,EO_tpeak,EO_tend,EO_xcen,EO_ycen) values (%s,%s,%s,%s,%s,%s,%s)'
# Execute the query (will write the record to the database)
# cursor.execute(put_query, values)    # There is also cursor.executemany(put_query, values_list)

cursor.executemany(put_query, values)
cnxn.commit()    # Important!  The record will be deleted if you do not "commit" after a transaction



# #####==================================================
# ts=1
# te=10
# # Read records from the database
# query = 'select * from '+table+' where date between '+str(ts)+' and '+str(te)
# cursor.execute(query)
# data = np.transpose(np.array(cursor.fetchall(),'object'))
# nrecs = len(data[0])
# # Get names from description
# names = np.array(cursor.description)[:,0]
# # Reshape data array for zipping into dictionary.  Each dictionary entry will be
# # an array of size nrecs.
# data.shape = (len(names),nrecs)
# # Create the dictionary 
# outdict = dict(list(zip(names,data)))
# cxnx.close()

