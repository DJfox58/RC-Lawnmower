from machine import Pin, PWM
import utime
from time import sleep
import network
import socket

#FRONT RIGHT
pwmPIN=16
cwPin=14 
acwPin=15

#BACK RIGHT
pwmPIN2 = 11
cwPin2 = 12
acwPin2 = 13

#BACK LEFT
pwmPIN3 = 20
cwPin3 = 19
acwPin3 = 18

#FRONT LEFT
pwmPIN4 = 9
cwPin4 = 7
acwPin4 = 8

pwmPIN5 = 21
cwPin5 = 22
acwPin5 = 26

def motorMove(speed, direction, speedGP, cwGP, acwGP):
    """Sets a given motor to the specificed speed and direction

    Args:
        speed (_int_): 0 - 100
        direction (_type_): 1 for fwd, -1 for reverse, 0 for stop
        speedGP (_type_): pin number of the motor's PWM pin
        cwGP (_type_): pin number of the motor's digital clockwise pin
        acwGP (_type_): pin number of the motor's digital counter-clockwise pin
    """    

    #Normalizes the speed to a set range
    if speed > 100: speed=100
    if speed < 0: speed=0
    
    #Sets pins
    Speed = PWM(Pin(speedGP))
    Speed.freq(50)
    
    cw = Pin(cwGP, Pin.OUT)
    acw = Pin(acwGP, Pin.OUT)
    
    #Sets speed
    Speed.duty_u16(int(speed/100*65536))
    
    #Determines direction
    cw.value(0)
    acw.value(0)
    
    if direction < 0:
        acw.value(1)
    elif direction > 0:
        cw.value(1)


#Used for operating the lawnmower
#Please forgive this ugly code....  
def moveForward():
    motorMove(50, -1, pwmPIN, cwPin, acwPin)
    motorMove(50, -1, pwmPIN4, cwPin4, acwPin4)
    motorMove(50, 1, pwmPIN2, cwPin2, acwPin2)
    motorMove(50, 1, pwmPIN3, cwPin3, acwPin3)

def moveBackward():
    motorMove(50, 1, pwmPIN, cwPin, acwPin)
    motorMove(50, 1, pwmPIN4, cwPin4, acwPin4)
    motorMove(50, -1, pwmPIN2, cwPin2, acwPin2)
    motorMove(50, -1, pwmPIN3, cwPin3, acwPin3)

def moveStop():
    motorMove(0, 0, pwmPIN, cwPin, acwPin)
    motorMove(0, 0, pwmPIN2, cwPin2, acwPin2)
    motorMove(0, 0, pwmPIN3, cwPin3, acwPin3)
    motorMove(0, 0, pwmPIN4, cwPin4, acwPin4)
    
def moveLeft():
    motorMove(50, -1, pwmPIN, cwPin, acwPin)
    motorMove(50, 1, pwmPIN2, cwPin2, acwPin2)
    motorMove(50, -1, pwmPIN3, cwPin3, acwPin3)
    motorMove(50, 1, pwmPIN4, cwPin4, acwPin4)
                                             
def moveRight():
    motorMove(50, 1, pwmPIN, cwPin, acwPin)
    motorMove(50, -1, pwmPIN2, cwPin2, acwPin2)
    motorMove(50, 1, pwmPIN3, cwPin3, acwPin3)
    motorMove(50, -1, pwmPIN4, cwPin4, acwPin4)
     
    
#Start and stop the mower motor independently from drive
def spinMower():
    motorMove(100, 1, pwmPIN5, cwPin5, acwPin5)
    
def stopMower():
    motorMove(0, 0, pwmPIN5, cwPin5, acwPin5)
    

#This is the whole html webpage 
def web_page():
    html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <title>Zumo Robot Control</title>
            </head>
            <center><b>
            <form action="./forward">
            <input type="submit" value="Forward" style="height:120px; width:120px" />
            </form>
            <table><tr>
            <td><form action="./left">
            <input type="submit" value="Left" style="height:120px; width:120px" />
            </form></td>
            <td><form action="./stop">
            <input type="submit" value="Stop" style="height:120px; width:120px" />
            </form></td>
            <td><form action="./right">
            <input type="submit" value="Right" style="height:120px; width:120px" />
            </form></td>
            </tr></table>
            <form action="./back">
            <input type="submit" value="Back" style="height:120px; width:120px" />
            </form>
            <td><form action="./mower">
            <input type="submit" value="Mower" style="height:120px; width:120px" />
            </form></td>
            <td><form action="./depower">
            <input type="submit" value="Depower" style="height:120px; width:120px" />
            </form></td>
            </body>
            </html>
            """
    return str(html)

# if you do not see the network you may have to power cycle
# unplug your pico w for 10 seconds and plug it in again
def ap_mode(ssid, password):
    """
        Description: This is a function to activate AP mode
        
        Parameters:
        
        ssid[str]: The name of your internet connection
        password[str]: Password for your internet connection
        
        Returns: Nada
    """
    # Just making our internet connection
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)
    
    while ap.active() == False:
        pass
    print('AP Mode Is Active, You can Now Connect')
    print('IP Address To Connect to:: ' + ap.ifconfig()[0])
    
    #creating socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    s.bind(('', 80))
    s.listen(5)

    while True:
        conn, addr = s.accept()
        print('Got a connection from ' + str(addr))
        request = conn.recv(1024)
        print('Content = ' + str(request))
        try:
            request = request.split()[1]
            print("REQUEST", request)
        except IndexError:
            pass
        print(request)
        #Different buttons on the webpage will result in different requests being sent
        #This can be used to determine which button was pressed on the webpage
        if request == b'/forward?':
            moveForward()
        elif request == b'/left?':
            moveLeft()
        elif request == b'/stop?':
            moveStop()
        elif request == b'/right?':
            moveRight()
        elif request == b'/back?':
            moveBackward()
        elif request == b"/mower?":
            spinMower()
        elif request == b"/depower?":
            stopMower()
        response = web_page()
        conn.send(response)
        conn.close()
      
#Top notch security to prevent anyone from hijacking our mower
ap_mode('Lawnmower Connection',
        '1234')
