
'''
Compare a motor's elements to default factory settings and return the saved parameters (unsaved paramters 
are not considered here) and the value of those paramters that differ. Shared values will not be printed.
'''
#Import DTtypes to access PMAC parameters.
#Import nestedGetattr function for motor elements with two attributes
from DTtypes import *
from nestedGetattr import nestedGetattr

def comparetoDefault(motorNum):
  #Access text file that contains all saved motor Elements in the PMAC and their values
  with open('defaultmotorelements.txt') as f:
    defaultElements=f.read().split('\n')

  with open('defaultmotorvalues.txt') as g:
    defaultValues=g.read().split('\n')
  
    #compare saved paramters
    for i in range(len(defaultElements)):
      if defaultElements[i].count('.')==0:      #First run motor parameters with on attribute
        if 'Sys' in defaultValues[i] or 'Enc' in defaultValues[i]:      #Do nothing if the content is a string
          defaultValues[i]=defaultValues[i]
        elif '$' in defaultValues[i]:      #If value is in hex, convert string in text file from hex to int
          defaultValues[i]=defaultValues[i].lstrip('$')
          defaultValues[i]=int(defaultValues[i],16)       
        else:
          defaultValues[i]=float(defaultValues[i])    #All other cases, it should be a number. So convert to a float.
        
        same=(getattr(Motor[motorNum],defaultElements[i])==defaultValues[i])
        
        if same==False:
          print(i)
          print(same)
          print('Motor['+str(motorNum)+'].'+defaultElements[i]+'='+ str(getattr(Motor[motorNum],defaultElements[i])))
          print('Motor[default settings].'+defaultElements[i]+'='+ str(defaultValues[i]))

      elif defaultElements[i].count('.')==1:    #Now run motor parameters with two attributes
        defaultValues[i]=float(defaultValues[i])
        splitElements=defaultElements[i].split('.')        
        #Use a nested getattr function for the motor elements with two attributes
        splitSame=(nestedGetattr(Motor[motorNum],splitElements[0],splitElements[1])==defaultValues[i])
        
        if splitSame==False:
          print(i)
          print(splitSame)
          print('Motor['+str(motorNum)+'].'+defaultElements[i]+'='+ str(nestedGetattr(Motor[motorNum],splitElements[0],splitElements[1])))
          print('Motor[default settings].'+defaultElements[i]+'='+ str(defaultValues[i]))       
                    
  return
comparetoDefault(1)