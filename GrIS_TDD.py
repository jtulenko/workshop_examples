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

[myhost,myport,myuser,mypassword,mydatabase] = db_info.credentials()



def reader_connect_to_db():
    dbc = pymysql.connect(host=myhost,port=myport,user=myuser,password=mypassword,database=mydatabase)

    return dbc


def GrIS_query():
    dbc = reader_connect_to_db()
    dbcursor = dbc.cursor()

    query = """select iced.base_sample.lon_DD, iced.base_calculatedage.t_St, iced.base_calculatedage.dtint_St, iced.base_sample.name
        from iced.base_sample, iced.base_calculatedage, iced.base_application_sites, iced.base_site
        where iced.base_sample.id = iced.base_calculatedage.sample_id
        and iced.base_sample.site_id = iced.base_site.id
        and iced.base_site.id = iced.base_application_sites.site_id
        and iced.base_application_sites.application_id = 3
        and iced.base_sample.what LIKE "%oulder%"
        and iced.base_sample.lat_DD >= 64.8
        and iced.base_sample.lat_DD <= 71
        and iced.base_sample.lon_DD >= -60
        and iced.base_sample.lon_DD <= -48
        and iced.base_calculatedage.t_St != 0
        and iced.base_calculatedage.t_St is not null;"""
    dbcursor.execute(query)
    result = dbcursor.fetchall()

    dbc.close()

    return result

result = GrIS_query()

def GrIS_TDD(result):
    df1 = pandas.DataFrame(list(result))

    x1 = df1[0]
    x1 = x1.astype('float64')
    y1 = (df1[1] / 1.0134) / 1000
    y_min = y1 - ((df1[2] / 1.0134) / 1000)
    y_max = y1 + ((df1[2] / 1.0134) / 1000)
    name = df1[3]

    pl.ion()
    pl.figure(1)
    pl.scatter(x1,y1)
    pl.ylim(15,5)

    return y1

plot = GrIS_TDD(result)
