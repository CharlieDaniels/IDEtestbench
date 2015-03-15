'''
Home any motor with two limit switches
Negatives: Slow
Positives: Robust
'''
#Import DTtypes to access PMAC parameters
from DTtypes import *
from ctypes import *

#homing procedure
def homeMotorGeneric(physicalMotorNode, macroBank, linearMacroNode, gate3CardIndex):
  
  #physicalMotorNode is the motor number
  #macroBank is 0 for A and 1 for B
  #linearMacroNode is the secondary encoder (glass scale)
  #gate3CardIndex is typically 0 (always 0 on test bench)
  
  #Clear the home status bit
  Motor[physicalMotorNode].HomeComplete=0
  Motor[physicalMotorNode].HomingInProgress=1

  #Set motor velocity, homing velocity, and acceleration/deceleration
  Motor[physicalMotorNode].JogSpeed=32
  Motor[physicalMotorNode].JogTa=-50
  Motor[physicalMotorNode].HomeVel=10

  #Enable motor to read trigger from position sensor input
  Motor[physicalMotorNode].CaptureMode=0

  #Check that motor is enabled and in closed loop mode. If not, end prgoram.
  if Motor[physicalMotorNode].AmpEna == 0:
    print('Amp is not enabled.')
    return
  elif Motor[physicalMotorNode].ClosedLoop == 0:
    print('Motor is not in closed loop control.')
    return
  #Check that the motor is phased
  elif Motor[physicalMotorNode].PhaseFound == 0:
    print('Motor is not phased. Please phase the motor before attempting to home it.')
    return

  #If the user input is macro bank A (specified by an input of 0)
  if macroBank == 0:
    #Clear the position capture register, and wait for it to clear
    Gate3[gate3CardIndex].MacroOutA[linearMacroNode,3]=0  #Gate3[0]MacroInA[0][3], second value is [0] for motor 1, and [4] for absolute encoder on motor 1
    while Gate3[gate3CardIndex].MacroInA[linearMacroNode,3]:
      pass
    #Arm the position capture register
    Gate3[gate3CardIndex].MacroOutA[linearMacroNode,3]=0x80100
    #Check that the position capture register has been set correctly
    if Gate3[gate3CardIndex].MacroOutA[linearMacroNode,3] != 0x80100:
      print('The position capture register arming failed')
      return
  #If the user input is macro bank B (specified by an input of 1)
  elif macroBank == 1:
    #Clear the position capture register
    Gate3[gate3CardIndex].MacroOutB[linearMacroNode,3]=0 #Gate3[0]MacroInB[4][3]
    #Arm the position capture register
    Gate3[gate3CardIndex].MacroOutB[linearMacroNode,3]=0x80100
    #Check that the position capture register has been set correctly 
    if Gate3[gate3CardIndex].MacroOutB[linearMacroNode,3] != 0x80100:
      print('The position capture register arming failed')
      return
  
  #I don't see no macro bank C-Z
  else:
    print('There are no macro banks other than A and B (0 and 1, respectively).')
    return

  #initiate indefinte move of the motor in the positive direction
  PPMAC.JogSpeed(physicalMotorNode,c_double(1))
  #Wait for motor to start moving
  while Motor[physicalMotorNode].DesVel == 0:
    pass

#-----------------MACRO BANK A
  #Test if the motor has passed the reference index during homing move
  if macroBank == 0:
    while Motor[physicalMotorNode].DesVel !=0:
      #If reference index found, stop the motor
      if Gate3[gate3CardIndex].MacroInA[linearMacroNode,3] & 0x80000:
        PPMAC.JogSpeed(physicalMotorNode,c_double(0))
        #Initiate an unsigned 64 bit encoder pointer
        encPointer=c_ulonglong()
        encPointer2=c_ulonglong()
        #Open a macro port
        OPort=MacroPortOpen(ord('b'),0)
        MacroSlaveRead(OPort,0,0,920,byref(encPointer))
        MacroSlaveRead(OPort,4,0,921,byref(encPointer2))
        absEnc=encPointer.value
        absEnc2=encPointer2.value
        print('Reference Flag found. Absolute encoder=',absEnc)
        print('Index position=',absEnc2)
        #Set the home status bit
        Motor[physicalMotorNode].HomeComplete=1
        MacroPortClose(OPort)
        break
      elif Gate3[gate3CardIndex].MacroInA[linearMacroNode,3] != 0x80000:
        continue
     
    #If the reference flag was not found while moving positive, it must have been in the other direction. Move negative.
    if Gate3[gate3CardIndex].MacroInA[linearMacroNode,3] != 0x80000:
      PPMAC.JogSpeed(physicalMotorNode,c_double(-1))
      #Wait for motor to start moving
      while Motor[physicalMotorNode].DesVel == 0:
        pass
      #Wait for motor to stop moving
      while Motor[physicalMotorNode].DesVel != 0:
        pass
      #Once you hit the negative limit switch, move positive
      if Motor[physicalMotorNode].MinusLimit:

        #Clear the position capture register, and wait for it to clear (because it activated while you moved negative)
        Gate3[gate3CardIndex].MacroOutA[linearMacroNode,3]=0 
        while Gate3[gate3CardIndex].MacroInA[linearMacroNode,3]:
          pass
        #Arm the position capture register
        Gate3[gate3CardIndex].MacroOutA[linearMacroNode,3]=0x80100
        #Check that the position capture register has been set correctly
        if Gate3[gate3CardIndex].MacroOutA[linearMacroNode,3] != 0x80100:
          print('The position capture register arming failed')
          return

        PPMAC.JogSpeed(physicalMotorNode,c_double(1))
        while Motor[physicalMotorNode].DesVel == 0:
          pass

      while Motor[physicalMotorNode].DesVel !=0:
        #If reference index found, stop the motor
        if Gate3[gate3CardIndex].MacroInA[linearMacroNode,3] & 0x80000:
          PPMAC.JogSpeed(physicalMotorNode,c_double(0))
          #Initiate an unsigned 64 bit encoder pointer
          encPointer=c_ulonglong()
          encPointer2=c_ulonglong()
          #Open a macro port
          OPort=MacroPortOpen(ord('b'),0)
          MacroSlaveRead(OPort,0,0,920,byref(encPointer))
          MacroSlaveRead(OPort,4,0,921,byref(encPointer2))
          absEnc=encPointer.value
          absEnc2=encPointer2.value
          print('Reference Flag found. Absolute encoder=',absEnc)
          print('Index position=',absEnc2)
          #Set the home status bit
          Motor[physicalMotorNode].HomeComplete=1
          MacroPortClose(OPort)
          break
        elif Gate3[gate3CardIndex].MacroInA[linearMacroNode,3] != 0x80000:
          continue
      
 #-----------------MACRO BANK B 
  elif macroBank == 1:
    while Motor[physicalMotorNode].DesVel !=0:
      #If reference index found, stop the motor
      if Gate3[gate3CardIndex].MacroInB[linearMacroNode,3] & 0x80000: 
        PPMAC.JogSpeed(physicalMotorNode,c_double(0))
        #Initiate an unsigned 64 bit encoder pointer
        encPointer=c_ulonglong()
        encPointer2=c_ulonglong()
        #Open a macro port
        OPort=MacroPortOpen(ord('b'),0)
        MacroSlaveRead(OPort,0,0,920,byref(encPointer))
        MacroSlaveRead(OPort,4,0,921,byref(encPointer2))
        absEnc=encPointer.value
        absEnc2=encPointer2.value
        print('Reference Flag found. Absolute encoder=',absEnc)
        print('Index position=',absEnc2)
        #Set the home status bit
        Motor[physicalMotorNode].HomeComplete=1
        MacroPortClose(OPort)
        break
      elif Gate3[gate3CardIndex].MacroInB[linearMacroNode,3] != 0x80000:
        continue 

#If the reference flag was not found while moving positive, it must have been in the other direction. Move negative.
    if Gate3[gate3CardIndex].MacroInB[linearMacroNode,3] != 0x80000:
      PPMAC.JogSpeed(physicalMotorNode,c_double(-1))
      #Wait for motor to start moving
      while Motor[physicalMotorNode].DesVel == 0:
        pass
      #Wait for motor to stop moving
      while Motor[physicalMotorNode].DesVel != 0:
        pass
      #Once you hit the negative limit switch, move positive
      if Motor[physicalMotorNode].MinusLimit:

        #Clear the position capture register, and wait for it to clear (because it activated while you moved negative)
        Gate3[gate3CardIndex].MacroOutB[linearMacroNode,3]=0 
        while Gate3[gate3CardIndex].MacroInB[linearMacroNode,3]:
          pass
        #Arm the position capture register
        Gate3[gate3CardIndex].MacroOutB[linearMacroNode,3]=0x80100
        #Check that the position capture register has been set correctly
        if Gate3[gate3CardIndex].MacroOutB[linearMacroNode,3] != 0x80100:
          print('The position capture register arming failed')
          return

        PPMAC.JogSpeed(physicalMotorNode,c_double(1))
        while Motor[physicalMotorNode].DesVel == 0:
          pass

      while Motor[physicalMotorNode].DesVel !=0:
        #If reference index found, stop the motor
        if Gate3[gate3CardIndex].MacroInB[linearMacroNode,3] & 0x80000:
          PPMAC.JogSpeed(physicalMotorNode,c_double(0))
          #Initiate an unsigned 64 bit encoder pointer
          encPointer=c_ulonglong()
          encPointer2=c_ulonglong()
          #Open a macro port
          OPort=MacroPortOpen(ord('b'),0)
          MacroSlaveRead(OPort,0,0,920,byref(encPointer))
          MacroSlaveRead(OPort,4,0,921,byref(encPointer2))
          absEnc=encPointer.value
          absEnc2=encPointer2.value
          print('Reference Flag found. Absolute encoder=',absEnc)
          print('Index position=',absEnc2)
          #Set the home status bit
          Motor[physicalMotorNode].HomeComplete=1
          MacroPortClose(OPort)
          break
        elif Gate3[gate3CardIndex].MacroInB[linearMacroNode,3] != 0x80000:
          continue

  #I still don't see no macro bank C-Z
  else:
    print('There are no macro banks other than A and B (0 and 1, respectively).')
    return

  return

homeMotorGeneric(1,0,4,0)