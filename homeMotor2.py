'''
Home a motor with two limit switches
'''
#Import DTtypes to access PMAC parameters
from DTtypes import *
from ctypes import *
#Import sleep to allow a wait time
from time import sleep

#homing procedure
def homeMotor(linearMacroNode, physicalMotorNode, gate3CardIndex, macroBank):
  
  #Clear the home status bit
  Motor[physicalMotorNode].HomeComplete=0
  Motor[physicalMotorNode].HomingInProgress=1

  #Set motor velocity, homing velocity and acceleration/deceleration
  Motor[physicalMotorNode].JogSpeed=32
  Motor[physicalMotorNode].JogTa=-50
  Motor[physicalMotorNode].HomeVel=10

  #Enable motor to read trigger from position sensor input
  Motor[physicalMotorNode].CaptureMode=1

  #Check that motor is enabled and in closed loop mode. If not, end prgoram.
  if Motor[physicalMotorNode].AmpEna == 0:
    print('Amp is not enabled.')
    return
  elif Motor[physicalMotorNode].ClosedLoop == 0:
    print('Motor is not in closed loop control.')
    return
  #Check that motor is phased
  elif Motor[physicalMotorNode].PhaseFound == 0:
    print('Motor is not phased. Please phase the motor before attempting to home it.')
    return

  print(Motor[physicalMotorNode].Pos)
  
  #Initiate an indefinite move for the motor
  JogPosition(1,-1)
  #PPMAC.JogSpeed(1,32) #positive & negative velocity travels left :/
  sleep(3)
  print(Motor[physicalMotorNode].Pos)

  #Read absolute encoder at the reference mark on the glass scale
  encPointer=c_ulonglong()
  OPort=MacroPortOpen(ord('b'),0)
  MacroSlaveRead(OPort,0,0,920,byref(encPointer))
  absEnc=encPointer.value
  absEnc2 = absEnc
  
  #Convert absolute encoder value if negative
  if absEnc>=0x200000000000:
    absEnc2-=0x400000000000
  print(absEnc,'(',absEnc2,')')
  
  MacroPortClose(OPort)

  return

homeMotor(0,1,0,'A')

