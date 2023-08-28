import pymysql
import pylab as pl
import numpy as np
import pandas
import geopandas as gpd
import geodatasets
import contextily as cx

import db_info

# enter the following command into a terminal window
# it will create a temporary connection to the database
# and specify that ICE-D data will be sent from the database to local port 12345
# email Greg or Joe for ICE-D IP address and database name to fill out the command

#########################################################################################
#                                                                                       #
#           ssh -N -L 12345:'ICE-D IP address':3306 iced@stoneage.ice-d.org             #
#                                                                                       #
#########################################################################################

#credentials from the db_info script get assigned to variables to be used in the reader connect function
[myhost,myport,myuser,mypassword,mydatabase,mydatabase2] = db_info.credentials()


#establish SSH tunnel connection from local machine to MySQL database hosted remotely
def reader_connect_to_db():
    dbc = pymysql.connect(host=myhost,port=myport,user=myuser,password=mypassword,database=mydatabase)

    return dbc

def TheQuery():
    dbc = reader_connect_to_db()
    dbcursor = dbc.cursor()

    query = """SELECT DISTINCT base_site.short_name, base_calculatedage.t_St, base_calculatedage.dtint_St, base_sample.id, base_sample.lat_DD
        FROM base_sample
        JOIN base_site ON base_sample.site_id = base_site.id
        JOIN base_application_sites ON base_site.id = base_application_sites.site_id
        JOIN (
            SELECT base_sample.site_id, AVG(base_calculatedage.t_St) AS avg_age, STDDEV(base_calculatedage.t_St) AS std_dev
            FROM base_sample
            JOIN base_calculatedage ON base_sample.id = base_calculatedage.sample_id
            GROUP BY base_sample.site_id
        ) AS stats ON base_sample.site_id = stats.site_id
        JOIN base_calculatedage ON base_sample.id = base_calculatedage.sample_id
        WHERE base_calculatedage.t_St BETWEEN stats.avg_age - (1.5 * stats.std_dev) AND stats.avg_age + (1.5 * stats.std_dev)
        AND base_sample.what LIKE "%oulder%"
        AND base_site.what LIKE "%oraine%"
        AND (base_sample.lat_DD > 35 AND base_sample.lat_DD < 48)
        AND base_sample.lon_DD > -123
        AND base_sample.lon_DD < -117
        AND base_calculatedage.t_St > 17000
        AND base_calculatedage.t_St < 30000
        AND base_application_sites.application_id = 2
        AND base_sample.site_id IN (
	        SELECT base_sample.site_id
	        FROM base_sample
	        GROUP BY base_sample.site_id
	        HAVING COUNT(*) > 2)
        """
    # AND base_sample.site_id IN (
	#         SELECT base_sample.site_id
	#         FROM base_sample, base_calculatedage
	#         WHERE base_sample.id = base_calculatedage.sample_id
	#         GROUP BY base_sample.site_id
	#         HAVING (AVG(base_calculatedage.t_St) > 13000 AND AVG(base_calculatedage.t_St) < 30000) AND STDDEV(base_calculatedage.t_St) < 4000)
    #     ORDER BY base_sample.lat_DD
    #AND STDDEV(base_calculatedage.t_St) < 4000
    dbcursor.execute(query)
    result = dbcursor.fetchall()

    dbc.close()

    return result

result1 = TheQuery()

def TheCamels(result):
    df1 = pandas.DataFrame(list(result))
    df1 = df1.groupby([0]).filter(lambda x: len(x) > 1)

    grouped_data = df1.groupby([0], sort=False)
    groups = np.array([group.values for notused, group in grouped_data], dtype=object)
    means = np.array(df1.groupby([0], sort=False)[1].mean()).astype(float)
    stds = np.array(df1.groupby([0], sort=False)[1].std(ddof=0)).astype(float)
    stds[stds == 0] = 500
    count = np.array(df1.groupby([0], sort=False)[1].count()).astype(int)

    print(np.sum(count),len(count))
    for i, g in enumerate(groups):
        print(f"Group {i} shape: {g.shape}")


    for group_id, group_data in grouped_data:

        ages = group_data[1].values
        errors = group_data[2].values

        pl.figure()


        summ = 0
        for age, error in zip(ages,errors):
            x = np.arange(((np.min(ages))-(np.mean(errors)*7)),((np.max(ages))+(np.mean(errors)*7)),50)
            output = np.exp(-0.5 * ((x - age) / error) ** 2) / (error * np.sqrt(2 * np.pi))
            output /= np.max(output)

            summ = summ + output

            pl.plot(x,output,'r')

        pl.plot(x,summ, 'k')
        pl.xlim(0,40000)
        pl.ylim(0,6)
        pl.title(f"Group {group_id} - Probability Density Functions")
    pl.show(block=False)

    return df1

plot = TheCamels(result1)