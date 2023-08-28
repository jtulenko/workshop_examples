import pymysql
import pylab as pl
import numpy as np
import pandas
import db_info

# enter the following command into a terminal window
# it will create a temporary connection to the database
# and specify that ICE-D data will be sent from the database to local port 12345
# email Greg or Joe for ICE-D IP address and database name to fill out the command

#########################################################################################
#                                                                                       #
#     ssh -f 'database'@stoneage.ice-d.org -L 12345:'ICE-D IP address':3306 -N -v       #
#                                                                                       #
#########################################################################################

[myhost,myport,myuser,mypassword,mydatabase,mydatabase2] = db_info.credentials()



def reader_connect_to_db():
    dbc = pymysql.connect(host=myhost,port=myport,user=myuser,password=mypassword,database=mydatabase)

    return dbc

def created_at_query():
    dbc = reader_connect_to_db()
    dbcursor = dbc.cursor()

    query = """select left(iced.base_sample.created_at,4), substring(iced.base_sample.created_at,6,2),substring(iced.base_sample.created_at,9,2)
        from iced.base_sample
        where iced.base_sample.id > 21901"""
    dbcursor.execute(query)
    result = dbcursor.fetchall()

    dbc.close()

    return result

result = created_at_query()

def created_at_hist(result):
    df1 = pandas.DataFrame(list(result))

    date1 = df1[0]
    date1 = date1.astype('float64')

    date2 = df1[1]
    date2 = date2.astype('float64')
    date2_1 = date2 / 12

    date3 = df1[2]
    date3 = date3.astype('float64')
    date3_1 = date3 / 365

    date = date1 + date2_1 + date3_1

    pl.ion()
    pl.figure(1)
    pl.hist(date, bins=np.arange(np.min(date),np.max(date) + (5/365), (5/365)))
    pl.xlabel('Date entered (decimal date)')
    pl.ylabel('sample count')

    return date

plot = created_at_hist(result)
