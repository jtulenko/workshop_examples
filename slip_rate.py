import pymysql
import matplotlib.pylab as pl
import numpy as np
import pandas
import db_info

# enter the following command into a terminal window
# it will create a temporary connection to the database
# and specify that ICE-D data will be sent from the database to local port 12345
# email Greg or Joe for ICE-D IP address and database name to fill out the command

#########################################################################################
#                                                                                       #
#     LINUX/WINDOWS PPL USE THIS ONE                                                    #
#     ssh -f iced@stoneage.ice-d.org -L 12345:'ICE-D IP address':3306 -N -v             #
#                                                                                       #
#     MAC PPL USE THIS ONE                                                              #
#     ssh -N -L 12345:'ICE-D IP address':3306 iced@stoneage.ice-d.org                   #
#                                                                                       #
#########################################################################################

[myhost,myport,myuser,mypassword,mydatabase,mydatabase2] = db_info.credentials()



def reader_connect_to_db1():
    dbc = pymysql.connect(host=myhost,port=myport,user=myuser,password=mypassword,database=mydatabase)

    return dbc

def reader_connect_to_db2():
    dbc = pymysql.connect(host=myhost,port=myport,user=myuser,password=mypassword,database=mydatabase2)

    return dbc

def iced_query():
    dbc = reader_connect_to_db1()
    dbcursor = dbc.cursor()

    query = """select iced.base_calculatedage.t_LSDn, iced.base_calculatedage.dtint_LSDn
        from iced.base_calculatedage, iced.base_sample, iced.base_site
        where iced.base_calculatedage.sample_id = iced.base_sample.id
        and iced.base_sample.site_id = iced.base_site.id
        and iced.base_site.short_name = 'SJTI05'"""
    
    dbcursor.execute(query)
    result = dbcursor.fetchall()

    dbc.close()

    return result

def slipr_query():
    dbc = reader_connect_to_db2()
    dbcursor = dbc.cursor()

    query = """select offset_measurements.offset_m, offset_measurements.del_offset_plus_m, offset_measurements.del_offset_minus_m
        from offset_measurements
        where iced_site = 'SJTI05'"""
    
    dbcursor.execute(query)
    result = dbcursor.fetchall()

    dbc.close()

    return result

ages_r = iced_query()
offsets_r = slipr_query()

def age_offset_mesh(ages,offsets):
    df1 = pandas.DataFrame(list(ages))
    df2 = pandas.DataFrame(list(offsets))

    ages_ka = (df1[0]) / 1000
    ages_ka = ages_ka.astype('float64')
    errors_ka = (df1[1]) / 1000
    errors_ka = errors_ka.astype('float64')

    offsets_m = df2[0]
    offsets_m = offsets_m.astype('float64')
    errors_plus = df2[1]
    errors_plus = errors_plus.astype('float64')
    errors_minus = df2[2]
    errors_minus = errors_minus.astype('float64')

    sum_ages = 0
    sum_offsets = 0
    for i in range(0,len(ages_ka)):
        x1 = np.arange(((np.min(ages_ka))-(np.mean(errors_ka)*7)),((np.max(ages_ka))+(np.mean(errors_ka)*7)),0.1)
        output1 = (1/(errors_ka[i]*np.sqrt(2*np.pi)))*(np.exp(-0.5*(((x1-ages_ka[i])/errors_ka[i])**2)))
        sum_ages = sum_ages + output1

    for i in range(0,len(offsets_m)):
        x2 = np.arange(((np.min(offsets_m))-(np.mean(errors_minus)*7)),((np.max(offsets_m))+(np.mean(errors_plus)*7)),0.1)
        output2 = (1/(errors_plus[i]*np.sqrt(2*np.pi)))*(np.exp(-0.5*(((x2-offsets_m[i])/errors_plus[i])**2)))
        sum_offsets = sum_offsets + output2

    xs, ys = np.meshgrid((x1*sum_ages), (x2*sum_offsets))
    zs = xs * ys

    pl.ion()
    pl.figure(1)
    pl.subplot(2,2,1)
    pl.gca().set_position([0.05,0.25,0.2,0.7])
    pl.plot(sum_offsets, x2, 'k')
    pl.ylim((np.min(offsets_m))-(np.mean(errors_minus)*7),(np.max(offsets_m))+(np.mean(errors_plus)*7))
    pl.subplot(2,2,4)
    pl.gca().set_position([0.25,0.05,0.7,0.2])
    pl.plot(x1,sum_ages,'k')
    pl.xlim((np.min(ages_ka))-(np.mean(errors_ka)*7),(np.max(ages_ka))+(np.mean(errors_ka)*7))
    pl.subplot(2,2,2)
    pl.gca().set_position([0.25,0.25,0.7,0.7])
    pl.contourf(x1,x2,zs)
    pl.xlim((np.min(ages_ka))-(np.mean(errors_ka)*7),(np.max(ages_ka))+(np.mean(errors_ka)*7))
    pl.ylim((np.min(offsets_m))-(np.mean(errors_minus)*7),(np.max(offsets_m))+(np.mean(errors_plus)*7))
    pl.yticks([])
    pl.xticks([])
    pl.show()

    slip_interval = np.array([0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1])
    for i in range(0,len(slip_interval)):
        xslip = np.arange(((np.min(ages_ka))-(np.mean(errors_ka)*7)),((np.max(ages_ka))+(np.mean(errors_ka)*7)),0.5)
        yslip = slip_interval[i] * xslip
        textposition = np.array([xslip[-1],yslip[-1]])

        slip_label = str(slip_interval[i])

        pl.figure(1)
        pl.subplot(2,2,2)
        pl.plot(xslip, yslip, 'r--', alpha = 0.4)
        pl.text(textposition[0],textposition[1], (slip_label) + 'mm/yr', color = 'red')
    
    return output1, sum_ages, output2, sum_offsets, zs, xslip, yslip

test = age_offset_mesh(ages_r,offsets_r)