The files in this repo are all python scripts that:
1) connect to the ICE-D database
2) request a bunch of specified data from ICE-D through an SQL query
3) take the raw data, package it into arrays, and then plot the data using pyplot

For #1, users will need to create a new python script and import it into their own scripts.
My example imported script is called db_info.py and in it, I wrote a function called 'credentials()'
The function defines the following 5 variables: host, port, user, password, database and returns all of them.
The user will have to create these variables and assign values to them. Email me and I can help you fill in this info.
Then, in the main scripts (for example, created_at.py), users can call the 'credentials()' function
and assign 5 new variables to the ones previously defined in the db_info.py script.
Those 5 new variables contain the values from the db_info.py script and are substituted in inside the
reader_connect_to_db(): function.

Additionally, users will need to correctly fill out the command specified at the beginning of the script by
substituting in the 'database' and 'ICE-D IP address' values.