import datetime
import threading
from threading import Thread

from flask import Flask
import os
from flask import render_template, redirect, url_for, request, session, flash, g
from functools import wraps
from DbClass import DbClass
import sys, os

#====Stepper and light sensor===
#forlightsensor
import spidev

import RPi.GPIO as GPIO
import time

spi = spidev.SpiDev()
spi.open(0, 0)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

ControlPin = [7,11,13,15]

#=================

#create the application object



#====THREADING=====================

class ThreadingExample(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, interval=10):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution


    def run(self):
        """ Method that runs forever """


        while True:
            # Do something

            print("Start")
            # Function to read SPI data from MCP3008 chip
            # Channel must be an integer 0-7
            def ReadChannel(channel):
                adc = spi.xfer2([1, (8 + channel) << 4, 0])
                data = ((adc[1] & 3) << 8) + adc[2]
                return data

            # Function to convert data to voltage level,
            # rounded to specified number of decimal places.
            def ConvertVolts(data, places):
                volts = (data * 3.3) / float(1023)
                volts = round(volts, places)
                return volts

            # Function to calculate temperature from
            # TMP36 data, rounded to specified
            # number of decimal places.
            def ConvertTemp(data, places):
                temp = data * 100
                return temp

            # Define sensor channels
            light_channel = 0
            temp_channel = 1

            # Define delay between readings
            delay = 2

            while True:
                print("Toestanden checken:")
                # ===TOESTANDBLIND====
                def toestandBlind():
                    db = DbClass()
                    print("toestand van fan checken:")
                    toestandBlind = db.getToestandblind()
                    if toestandBlind[0] == 1:
                        print("Blind gaat open")


                        for pin in ControlPin:
                            GPIO.setup(pin, GPIO.OUT)
                            GPIO.output(pin, 0)

                        seq = [[0, 0, 0, 1],
                               [0, 0, 1, 1],
                               [0, 0, 1, 0],
                               [0, 1, 1, 0],
                               [0, 1, 0, 0],
                               [1, 1, 0, 0],
                               [1, 0, 0, 0],
                               [1, 0, 0, 1]]

                        for i in range(128):
                            ### GO THROUGH THE SEQUENCE ONCE ###
                            for halfstep in range(8):
                                ### GO THROUGH EACH HALF-STEP ###
                                for pin in range(4):
                                    ### SET EACH PIN ###
                                    GPIO.output(ControlPin[pin], seq[halfstep][pin])
                                time.sleep(0.001)
                    elif toestandBlind[0] == 0:
                        print("Blind gaat toe")

                        for pin in ControlPin:
                            GPIO.setup(pin, GPIO.OUT)
                            GPIO.output(pin, 0)

                        seq = [[1, 0, 0, 0],
                               [1, 1, 0, 0],
                               [0, 1, 0, 0],
                               [0, 1, 1, 0],
                               [0, 0, 1, 0],
                               [0, 0, 1, 1],
                               [0, 0, 0, 1],
                               [1, 0, 0, 1]]

                        for i in range(2048):
                            ### GO THROUGH THE SEQUENCE ONCE ###
                            for halfstep in range(8):
                                ### GO THROUGH EACH HALF-STEP ###
                                for pin in range(4):
                                    ### SET EACH PIN ###
                                    GPIO.output(ControlPin[pin], seq[halfstep][pin])
                                time.sleep(0.001)

                # ===TOESTANDFAN=======
                def toestandFan():
                    db = DbClass()
                    print("toestand van fan checken:")
                    toestandFan = db.getToestandfan()
                    if toestandFan[0] == 1:
                        print("Fan staat aan")
                        # ===Data weschrijven==
                        datum = datetime.datetime.now()
                        uur = datetime.datetime.now()
                        reden = "Fan manually started by the user."

                        db = DbClass()
                        db.setDataToLog(reden, datum, uur)

                        # ===Start fan=========
                        t1=Thread(target=openfan)
                        t1.start()
                    elif toestandFan[0] == 0:
                        print("Fan staat uit")

                        # ===Stop fan=========
                        import RPi.GPIO as GPIO
                        GPIO.setmode(GPIO.BOARD)
                        print('Stop')
                        GPIO.setup(37, GPIO.OUT)
                        GPIO.output(37, GPIO.LOW)
                        GPIO.setup(37, GPIO.IN)
                        GPIO.cleanup()

                # Read the light sensor data
                light_level = ReadChannel(light_channel)
                light_volts = ConvertVolts(light_level, 2)

                # Read the temperature sensor data
                temp_level = ReadChannel(temp_channel)
                temp_volts = ConvertVolts(temp_level, 2)
                temp = ConvertTemp(temp_volts, 2)

                # Print out results

                #print("Light: {} ".format(light_level))
                #print("Temp : {} deg C".format(int(temp)))
                licht = light_level
                temperatuur = temp

                # db = DbClass()
                # db.setDataToData(temperatuur,licht)

                # Wait before repeating loop
                toestandFan()
                time.sleep(delay)

            time.sleep(self.interval)

def openfan():
    import RPi.GPIO as GPIO
    import time
    GPIO.setwarnings(False)

    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(37, GPIO.OUT)

    p = GPIO.PWM(37, 0.8)

    p.start(0)

    try:
        while True:
            print("loop")
            for i in range(100):
                p.ChangeDutyCycle(i)
                time.sleep(0.02)
            for i in range(100):
                p.ChangeDutyCycle(100 - i)
                time.sleep(0.02)

    except KeyboardInterrupt:
        pass

    p.stop()

    GPIO.cleanup()

app = Flask(__name__)
ThreadingExample()

temp = 0

print(temp)

def open_blinds(reden):
    datum = datetime.datetime.now()
    uur = datetime.datetime.now()
    reden = reden

    db = DbClass()
    db.setDataToLog(reden, datum, uur)

    for pin in ControlPin:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

    seq = [[0, 0, 0, 1],
           [0, 0, 1, 1],
           [0, 0, 1, 0],
           [0, 1, 1, 0],
           [0, 1, 0, 0],
           [1, 1, 0, 0],
           [1, 0, 0, 0],
           [1, 0, 0, 1]]

    for i in range(128):
        ### GO THROUGH THE SEQUENCE ONCE ###
        for halfstep in range(8):
            ### GO THROUGH EACH HALF-STEP ###
            for pin in range(4):
                ### SET EACH PIN ###
                GPIO.output(ControlPin[pin], seq[halfstep][pin])
            time.sleep(0.001)

def close_blinds(reden):
    datum = datetime.datetime.now()
    uur = datetime.datetime.now()
    reden = reden
    db = DbClass()
    db.setDataToLog(reden, datum, uur)

    for pin in ControlPin:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)


    seq = [[1, 0, 0, 0],
           [1, 1, 0, 0],
           [0, 1, 0, 0],
           [0, 1, 1, 0],
           [0, 0, 1, 0],
           [0, 0, 1, 1],
           [0, 0, 0, 1],
           [1, 0, 0, 1]]


    for i in range(2048):
        ### GO THROUGH THE SEQUENCE ONCE ###
        for halfstep in range(8):
            ### GO THROUGH EACH HALF-STEP ###
            for pin in range(4):
                ### SET EACH PIN ###
                GPIO.output(ControlPin[pin], seq[halfstep][pin])
            time.sleep(0.001)

# def start_fan(reden):
#     #===Data weschrijven==
#     datum = datetime.datetime.now()
#     uur = datetime.datetime.now()
#     reden = reden
#
#     db = DbClass()
#     db.setDataToLog(reden, datum, uur)
#
#     #===Start fan=========
#     import RPi.GPIO as GPIO
#     import time
#     GPIO.setwarnings(False)
#
#     GPIO.setmode(GPIO.BOARD)
#
#     GPIO.setup(37, GPIO.OUT)
#
#     p = GPIO.PWM(37, 0.8)
#
#     p.start(0)
#
#     try:
#         while True:
#             for i in range(100):
#                 p.ChangeDutyCycle(i)
#                 time.sleep(0.02)
#             for i in range(100):
#                 p.ChangeDutyCycle(100 - i)
#                 time.sleep(0.02)
#
#     except KeyboardInterrupt:
#         pass
#
#     p.stop()
#
#     GPIO.cleanup()
#     #=== STOP FAN SAFETY ======
#     if request.method == 'POST':
#         button = request.form['button']
#         if button == 'Stop':
#             import RPi.GPIO as GPIO
#             GPIO.setmode(GPIO.BOARD)
#             print('Stop')
#             GPIO.setup(37, GPIO.OUT)
#             GPIO.output(37, GPIO.LOW)
#             GPIO.setup(37, GPIO.IN)
#             GPIO.cleanup()

def stop_fan(reden):
    #===Data weschrijven==
    datum = datetime.datetime.now()
    uur = datetime.datetime.now()
    reden = reden

    db = DbClass()
    db.setDataToLog(reden, datum, uur)

    #===Stop fan=========
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD)
    print('Stop')
    GPIO.setup(37, GPIO.OUT)
    GPIO.output(37, GPIO.LOW)
    GPIO.setup(37, GPIO.IN)
    GPIO.cleanup()
#==================================

        # config


app.secret_key = "my precious"


# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))

    return wrap


# use decorators to link the function to a url
@app.route('/login', methods=['GET', 'POST'])
def login():
    # error = None
    # if request.method == 'POST':
    #     if request.form['username'] !='admin' or request.form['password'] != 'admin':
    #         error = ' invalid credentials, Please try again.'
    #     else:
    #         session['logged_in'] = True
    #         flash('You were just logged in!')
    #         return redirect(url_for('index'))
    # return render_template('login.html', error=error)


    error = None
    if request.method == "POST":
        db = DbClass()
        user_credentials = db.getUser(request.form['username'])
        if user_credentials: #Als de lijst NIET leeg is dan...
            if (user_credentials[1]) != request.form['password']:
                error = ' Wrong password. Please try again.'
            else:
                session['logged_in'] = True
                flash('You were just logged in!')
                session['username'] = user_credentials[0]
                return redirect(url_for("index"))
        else:
            error = ' User does not excist. Please try again.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were just logged out!')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    db = DbClass()
    toestandblind = db.getToestandblind()
    toestandfan = db.getToestandfan()

    if request.method == 'POST':
        button = request.form['button']

        # 1 gesloten 0 is open
        if button == "Open" and toestandblind[0] == 0:
            db.updateToestandBlind(1)
            datum = datetime.datetime.now()
            uur = datetime.datetime.now()
            reden = "Blind manually opened by the user."

            db = DbClass()
            db.setDataToLog(reden, datum, uur)

            return redirect(url_for('index'))

        if button == "Close" and toestandblind[0] == 1:
            db.updateToestandBlind(0)

            datum = datetime.datetime.now()
            uur = datetime.datetime.now()
            reden = "Blind manually closed by the user."
            db = DbClass()
            db.setDataToLog(reden, datum, uur)
            return redirect(url_for('index'))

        # 1 gesloten 0 is open
        if button == "Start" and toestandfan[0] == 0:
            db.updateToestandFan(1)
            # ===Data weschrijven==
            datum = datetime.datetime.now()
            uur = datetime.datetime.now()
            reden = "Fan manually started by the user."

            db = DbClass()
            db.setDataToLog(reden, datum, uur)
            return redirect(url_for('index'))

        if button == "Stop" and toestandfan[0] == 1:
            db.updateToestandFan(0)
            # ===Data weschrijven==
            datum = datetime.datetime.now()
            uur = datetime.datetime.now()
            reden = "Fan manually stopped by the user."

            db = DbClass()
            db.setDataToLog(reden, datum, uur)
            return redirect(url_for('index'))


        # ventilator = 1

        # if button == 'Check':
        #     import RPi.GPIO as GPIO
        #     import time
        #     GPIO.setmode(GPIO.BOARD)
        #
        #     GPIO.setup(37, GPIO.OUT)
        #
        #     p = GPIO.PWM(37, 0.8)
        #
        #     p.start(0)
        #
        #     try:
        #         while ventilator == 1:
        #             for i in range(100):
        #                 p.ChangeDutyCycle(i)
        #                 time.sleep(0.02)
        #             for i in range(100):
        #                 p.ChangeDutyCycle(100 - i)
        #                 time.sleep(0.02)
        #     except KeyboardInterrupt:
        #         pass

        # if button == 'Open':
        #     import RPi.GPIO as GPIO
        #     switch = 1
        #     for pin in ControlPin:
        #         GPIO.setup(pin, GPIO.OUT)
        #         GPIO.output(pin, 0)
        #
        #     seq = [[1, 0, 0, 0],
        #            [1, 1, 0, 0],
        #            [0, 1, 0, 0],
        #            [0, 1, 1, 0],
        #            [0, 0, 1, 0],
        #            [0, 0, 1, 1],
        #            [0, 0, 0, 1],
        #            [1, 0, 0, 1]]
        #
        #     for i in range(512):
        #         ### GO THROUGH THE SEQUENCE ONCE ###
        #         for halfstep in range(8):
        #             ### GO THROUGH EACH HALF-STEP ###
        #             for pin in range(4):
        #                 ### SET EACH PIN ###
        #                 GPIO.output(ControlPin[pin], seq[halfstep][pin])
        #             time.sleep(0.001)
        # elif button == 'Close':
        #     import RPi.GPIO as GPIO
        #     switch = 0
        #     for pin in ControlPin:
        #         GPIO.setup(pin, GPIO.OUT)
        #         GPIO.output(pin, 0)
        #
        #     seq = [[0, 0, 0, 1],
        #            [0, 0, 1, 1],
        #            [0, 0, 1, 0],
        #            [0, 1, 1, 0],
        #            [0, 1, 0, 0],
        #            [1, 1, 0, 0],
        #            [1, 0, 0, 0],
        #            [1, 0, 0, 1]]
        #
        #     for i in range(512):
        #         ### GO THROUGH THE SEQUENCE ONCE ###
        #         for halfstep in range(8):
        #             ### GO THROUGH EACH HALF-STEP ###
        #             for pin in range(4):
        #                 ### SET EACH PIN ###
        #                 GPIO.output(ControlPin[pin], seq[halfstep][pin])
        #             time.sleep(0.001)
        #
        # if button == 'Start':
        #     import RPi.GPIO as GPIO
        #     import time
        #     GPIO.setmode(GPIO.BOARD)
        #
        #     GPIO.setup(37, GPIO.OUT)
        #
        #     p = GPIO.PWM(37, 0.8)
        #
        #     p.start(0)
        #
        #     try:
        #         while ventilator == 1:
        #             for i in range(100):
        #                 p.ChangeDutyCycle(i)
        #                 time.sleep(0.02)
        #             for i in range(100):
        #                 p.ChangeDutyCycle(100 - i)
        #                 time.sleep(0.02)
        #     except KeyboardInterrupt:
        #         pass
        #
        # elif button == 'Stop':
        #     import RPi.GPIO as GPIO
        #     GPIO.setmode(GPIO.BOARD)
        #     print('Stop')
        #     GPIO.setup(37, GPIO.OUT)
        #     GPIO.output(37, GPIO.LOW)
        #     GPIO.setup(37, GPIO.IN)
        #     GPIO.cleanup()

    #g.db = DbClass()
    #cur = g.db.execute('select * from posts')
    #posts = [dict(title=row[0], description=row[1]) for row in cur.fetchall()]
    #g.db.close()
    return render_template('index.html', toestandblind=toestandblind, toestandfan=toestandfan) #, posts=posts)

@app.route('/devices')
@login_required
def devices():
    db = DbClass()
    devicelijst = db.getDevices()
    return render_template('devices.html', devicelijst=devicelijst)

@app.route('/devicedetail/<deviceid>', methods=['GET', 'POST'])
@login_required
def devicedetail(deviceid):
    db = DbClass()
    devicedetail = db.getDevice(deviceid)
    switch = 0
    if request.method == 'POST':
        button = request.form['button']
        if button == 'Open':
            for pin in ControlPin:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, 0)

            seq = [[1, 0, 0, 0],
                   [1, 1, 0, 0],
                   [0, 1, 0, 0],
                   [0, 1, 1, 0],
                   [0, 0, 1, 0],
                   [0, 0, 1, 1],
                   [0, 0, 0, 1],
                   [1, 0, 0, 1]]

            for i in range(512):
                ### GO THROUGH THE SEQUENCE ONCE ###
                for halfstep in range(8):
                    ### GO THROUGH EACH HALF-STEP ###
                    for pin in range(4):
                        ### SET EACH PIN ###
                        GPIO.output(ControlPin[pin], seq[halfstep][pin])
                    time.sleep(0.001)
        elif button == 'Close':
            for pin in ControlPin:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, 0)

            seq = [[0, 0, 0, 1],
                   [0, 0, 1, 1],
                   [0, 0, 1, 0],
                   [0, 1, 1, 0],
                   [0, 1, 0, 0],
                   [1, 1, 0, 0],
                   [1, 0, 0, 0],
                   [1, 0, 0, 1]]

            for i in range(512):
                ### GO THROUGH THE SEQUENCE ONCE ###
                for halfstep in range(8):
                    ### GO THROUGH EACH HALF-STEP ###
                    for pin in range(4):
                        ### SET EACH PIN ###
                        GPIO.output(ControlPin[pin], seq[halfstep][pin])
                    time.sleep(0.001)
        if button == 'Geen licht-open gordijn':
            # Define Variables
            delay = 0.5
            ldr_channel = 0

            # Create SPI
            spi = spidev.SpiDev()
            spi.open(0, 0)

            def readadc(adcnum):
                # read SPI data from the MCP3008, 8 channels in total
                if adcnum > 7 or adcnum < 0:
                    return -1
                r = spi.xfer2([1, 8 + adcnum << 4, 0])
                data = ((r[1] & 3) << 8) + r[2]
                return data

            while True:
                ldr_value = readadc(ldr_channel)
                print(ldr_value)
                time.sleep(delay)

                if ldr_value > 800 and switch ==0:
                    switch=1
                    for pin in ControlPin:
                        GPIO.setup(pin, GPIO.OUT)
                        GPIO.output(pin, 0)
                    seq = [[1, 0, 0, 0],
                           [1, 1, 0, 0],
                           [0, 1, 0, 0],
                           [0, 1, 1, 0],
                           [0, 0, 1, 0],
                           [0, 0, 1, 1],
                           [0, 0, 0, 1],
                           [1, 0, 0, 1]]
                    for i in range(512):
                        ### GO THROUGH THE SEQUENCE ONCE ###
                        for halfstep in range(8):
                            ### GO THROUGH EACH HALF-STEP ###
                            for pin in range(4):
                                ### SET EACH PIN ###
                                GPIO.output(ControlPin[pin], seq[halfstep][pin])
                            time.sleep(0.001)

                elif ldr_value < 800 and switch ==1:
                    switch = 0
                    for pin in ControlPin:
                        GPIO.setup(pin, GPIO.OUT)
                        GPIO.output(pin, 0)

                    seq = [[0, 0, 0, 1],
                           [0, 0, 1, 1],
                           [0, 0, 1, 0],
                           [0, 1, 1, 0],
                           [0, 1, 0, 0],
                           [1, 1, 0, 0],
                           [1, 0, 0, 0],
                           [1, 0, 0, 1]]

                    for i in range(512):
                        ### GO THROUGH THE SEQUENCE ONCE ###
                        for halfstep in range(8):
                            ### GO THROUGH EACH HALF-STEP ###
                            for pin in range(4):
                                ### SET EACH PIN ###
                                GPIO.output(ControlPin[pin], seq[halfstep][pin])
                            time.sleep(0.001)

        # if button == 'Warmer dan'
        #
        #
        #
        # if button == 'Kouder dan'
        if button == 'updaten':
            temp = request.form['temperatuur']
    return render_template('devicedetail.html', devicedetail=devicedetail)

@app.route('/logs')
@login_required
def logs():
    db = DbClass()
    logskeuze = db.getLogsKeuze()
    return render_template('logs.html', logskeuze=logskeuze)

@app.route('/logskeuze/<idchoice>')
@login_required
def logskeuze(idchoice):
    db = DbClass()
    logskeuze = db.getLogKeuze(idchoice)
    logauto = db.getLogsAutomatic()
    logmanual = db.getLogsManual()
    logall = db.getLogsAll()
    return render_template('logskeuze.html', logskeuze=logskeuze, logauto=logauto, logmanual=logmanual, logall=logall)


@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT",5000))
    app.run(host='0.0.0.0', port=5000, debug=True)

# def checkLight():
#     db = DbClass
#     if db.getLicht() == 'Wakeup':
#         for pin in ControlPin:
#             GPIO.setup(pin, GPIO.OUT)
#             GPIO.output(pin, 0)
#
#         seq = [[1, 0, 0, 0],
#                [1, 1, 0, 0],
#                [0, 1, 0, 0],
#                [0, 1, 1, 0],
#                [0, 0, 1, 0],
#                [0, 0, 1, 1],
#                [0, 0, 0, 1],
#                [1, 0, 0, 1]]
#
#         for i in range(512):
#             ### GO THROUGH THE SEQUENCE ONCE ###
#             for halfstep in range(8):
#                 ### GO THROUGH EACH HALF-STEP ###
#                 for pin in range(4):
#                     ### SET EACH PIN ###
#                     GPIO.output(ControlPin[pin], seq[halfstep][pin])
#                 time.sleep(0.001)
#         GPIO.cleanup()



#===Steppermotor=========================


print(temp)