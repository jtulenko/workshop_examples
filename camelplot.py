import pylab as pl
import numpy as np
import pdb

#open space-delimited text file with two columns, ages and errors.
#you can delimit the txt file however you want, just change the argument 
#in line 29 @ .split(' ') ex: comma delimited would be .split(',')
#If columns have headers make sure the hearders are 'ages' and 'errors'
sample_file1 = open('/home/jtulenko/sw/iced_lab/workshop_examples/example_data/test-dataset-lognorm.txt', 'r')
sample_file2 = open('/home/jtulenko/sw/iced_lab/workshop_examples/example_data/LC-2.txt', 'r')
sample_file3 = open('/home/jtulenko/sw/iced_lab/workshop_examples/example_data/LC-3.txt', 'r')

#assign empty variables to ages and errors from each txt file read in
ages1=[]
errors1=[]
ages2=[]
errors2=[]
ages3=[]
errors3=[]

#strip split and append data into ages and errors lists
def readinfile(file):
    #the function
    ages = []
    errors = []
    for line in file:
        if not line.startswith('ages'):

            cline = line.strip().split(' ')

            ages.append(cline[0])
            errors.append(cline[1])

    return ages, errors

# create ages and errors lists from the text files read in
ages_1, errors_1 = readinfile(sample_file1)
ages_2, errors_2 = readinfile(sample_file2)
ages_3, errors_3 = readinfile(sample_file3)


#convert ages and errors lists into arrays
ages_1 = np.array(ages_1).astype(float)
errors_1 = np.array(errors_1).astype(float)
ages_2 = np.array(ages_2).astype(float)
errors_2 = np.array(errors_2).astype(float)
ages_3 = np.array(ages_3).astype(float)
errors_3 = np.array(errors_3).astype(float)


#make arrays for colors for each set of ages
color_ramp = ['#f74a4a','#4090e6','#9a56a6']

colors1 = np.array([color_ramp[0]])
colors2 = np.array([color_ramp[1]])
colors3 = np.array([color_ramp[2]])

#function to make a for loop that cycles thru each age & error array pairs, plot each age and error,
# then sum up the plots into a summed plot at the end.
#indivual age-error pair as a normal distribution function (ndf) where age = mean, error = SD
def camelplot(ages,errors,colors):
    sum_ages = 0
    for i in range(0,len(ages)):
        #for each set of ages that correspond to one landform, the x-range is between the 
        #minimum age in the array - 7(population averaged)SD and the maximum age + 7(population averaged)SD.
        #Gives each plot nice (but not an excessively long) tails. Makes the summed plot easy to calculate.
        x = np.arange(((np.min(ages))-(np.mean(errors)*7)),((np.max(ages))+(np.mean(errors)*7)),50)

        #the actual equation for each ndf
        output = (1/(errors[i]*np.sqrt(2*np.pi)))*(np.exp(-0.5*(((x-ages[i])/errors[i])**2)))

        #a potential update to the camelplot that removes age as a factor of camel hump height.
        #i.e., older ages with the same precision as younger ages will still have shorter humps
        #because the absolute value for error is greater even if error% is the same.
        #comment out the one above and substitue this one in if interested.
        #output = (1/(np.sqrt(2*np.pi*((errors[i]/ages[i])*(errors[i]**2)))))*(1/(errors[i]*np.sqrt(2*np.pi)))*(np.exp(-0.5*(((x-ages[i])/errors[i])**2)))
        
        #this sums up all of the individual ndfs and adds them to the sum_ages variable created prior to the for loop.
        sum_ages = sum_ages + output

        c = colors[0]

        #all of the plotting code to plot each age and color them by landform
        pl.ion()
        pl.figure(1)
        pl.xlim(0,40000)
        pl.xlabel('Age [years]')
        pl.ylabel('Relative probability')
        pl.plot(x,output,c)

    #plot the sum of all the ndfs on top once finished with the for loop
    pl.plot(x,sum_ages,'k')

    return output, sum_ages

#varilables to store the results in for each landform
kenai_plot1 = camelplot(ages_1,errors_1,colors1)
#kenai_plot2 = camelplot(ages_2,errors_2,colors2)
#kenai_plot3 = camelplot(ages_3,errors_3,colors3)