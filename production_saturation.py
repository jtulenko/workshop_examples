import pymysql
import pylab as pl
import numpy as np
import pandas
import db_info

# enter the following command into a terminal window
# it will create a temporary connection to the database
# and specify that ICE-D data will be sent from the database to local port 12345
# email Greg or Joe for ICE-D IP address and database name to fill out the command.

#########################################################################################
#                                                                                       #
#     ssh -f 'database'@stoneage.ice-d.org -L 12345:'ICE-D IP address':3306 -N -v       #
#                                                                                       #
#########################################################################################

[myhost,myport,myuser,mypassword,mydatabase,mydatabase2] = db_info.credentials()



def reader_connect_to_db():
    dbc = pymysql.connect(host=myhost,port=myport,user=myuser,password=mypassword,database=mydatabase)

    return dbc


def pr_sat_query_c():
    dbc = reader_connect_to_db()
    dbcursor = dbc.cursor()

    query1 = """select distinct iced._c14_quartz.N14_atoms_g, iced.base_sample.elv_m
        from iced._c14_quartz, iced.base_sample, iced.base_site, iced.base_application_sites, iced.base_calculatedage
        where iced.base_sample.id = iced._c14_quartz.sample_id
        and iced.base_sample.site_id = iced.base_site.id
        and iced.base_site.id = iced.base_application_sites.site_id
        and iced.base_calculatedage.sample_id = iced.base_sample.id
        and iced.base_calculatedage.t_St != 0
        and iced.base_sample.elv_m > 1
        and iced._c14_quartz.N14_atoms_g / iced.base_calculatedage.t_St < 100
        and iced.base_calculatedage.t_St < 25000
        and iced.base_calculatedage.nuclide LIKE "%N14quartz"
        and iced.base_application_sites.application_id = 1"""
    dbcursor.execute(query1)
    result1 = dbcursor.fetchall()

    query2 = """select distinct iced._be10_al26_quartz.N10_atoms_g, iced._be10_al26_quartz.N26_atoms_g, iced.base_sample.elv_m
        from iced._be10_al26_quartz, iced.base_sample, iced.base_site, iced.base_application_sites
        where iced.base_sample.id = iced._be10_al26_quartz.sample_id
        and iced.base_sample.site_id = iced.base_site.id
        and iced.base_site.id = iced.base_application_sites.site_id
        and iced.base_sample.elv_m > 1
        and iced.base_application_sites.application_id = 1
        and iced._be10_al26_quartz.N10_atoms_g != 0
        and iced._be10_al26_quartz.N26_atoms_g != 0"""
    dbcursor.execute(query2)
    result2 = dbcursor.fetchall()

    dbc.close()

    return result1, result2

result1, result2 = pr_sat_query_c()

def pr_sat_plot(result1, result2):
    df1 = pandas.DataFrame(list(result1))
    df2 = pandas.DataFrame(list(result2))

    lam_c = 0.00012096809
    lam_be = 0.00000071942446
    lam_al = 0.00000136986

    x1 = df1[0] * lam_c
    y1 = df1[1]
    x2 = df2[0] * lam_be
    x3 = df2[1] * lam_al
    y2 = df2[2]

    pl.ion()
    pl.figure(1)
    pl.yscale('log')
    pl.ylim(1,10000)
    pl.scatter(x3,y2, c='#d62728')
    pl.scatter(x2,y2, c='#bcbd22')
    pl.scatter(x1,y1, c='#1f77b4')
    
    

    return y1

plot1 = pr_sat_plot(result1, result2)