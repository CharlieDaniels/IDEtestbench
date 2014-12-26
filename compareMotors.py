'''
Compare two motors of your choice and return the saved parameters (unsaved paramters 
are not considered here) and the value of those paramters that differ. Shared 
values will not be printed.
'''
#Import DTtypes to access PMAC parameters.
#Import nestedGetattr function for motor elements with two attributes
from DTtypes import *
from nestedGetattr import nestedGetattr

def compare(motorA, motorB):
  #Access text file that contains all saved motor Elements in the PMAC
  with open('SavedMotorDataStructureElements.txt') as f:
    savedElements=f.read().split('\n')

    #compare saved paramters
    for i in range(len(savedElements)):

      if savedElements[i].count('.')==0:
        #Use getattr because attributes of the motor are listed as strings in the text file
        same=(getattr(Motor[motorA],savedElements[i])==getattr(Motor[motorB],savedElements[i]))

        #If the motor elements are not the same, print out the values
        if same==False:
          print(i)
          print(same)
          print('Motor[',motorA,'].',savedElements[i],'=', getattr(Motor[motorA],savedElements[i]), sep='')
          print('Motor[',motorB,'].',savedElements[i],'=', getattr(Motor[motorB],savedElements[i]), sep='')

      #In case the motor element has two attributes, it is handled in this 'else if' case
      elif savedElements[i].count('.')==1:
        splitElements=savedElements[i].split('.')
        #Use a nested getattr function for the motor elements with two attributes
        splitSame=(nestedGetattr(Motor[motorA],splitElements[0],splitElements[1])==nestedGetattr(Motor[motorB],splitElements[0],splitElements[1]))

        #If the motor elements are not the same, print out the values
        if splitSame==False:
          print(i)
          print(splitSame)
          print('Motor[',motorA,'].',savedElements[i],'=', nestedGetattr(Motor[motorA],splitElements[0],splitElements[1]), sep='')
          print('Motor[',motorB,'].',savedElements[i],'=', nestedGetattr(Motor[motorB],splitElements[0],splitElements[1]), sep='')

  return

#compare(1,8)