import serial
import pynmea2
from sense_hat import SenseHat

# Makes SenseHat object
s = SenseHat()

# Defines serial port
serialPort = serial.Serial("/dev/ttyACM0", 9600, timeout=0.5)

# Functions for saving relevant data easily
def save_last(data):
    with open("last_reading.txt", "w") as f:
        f.write(data)

def read_last():
    with open("last_reading.txt", "r") as f:
        data = f.read()
    return data

def save_date(data):
    with open("last_date.txt", "w") as f:
        f.write(data)

def read_date():
    with open("last_date.txt", "r") as f:
        data = f.read()
    return data

def parseGPS(string, last, date):
    """
    This obtains relevant data from the GPS reading and prints it
    It is meant to be used with the command line program "watch" to allow an updating
    display of GPS and sensor information
    """
    # If getting fix data
    if string.find("GGA") > 0:
        # Gets the relevant data from the reading and the SenseHAT
        msg = pynmea2.parse(string)
        temp = s.get_temperature_from_pressure()
        humidity = s.get_humidity()
        pressure = s.get_pressure()

        # The data is output to the command line
        print("Date: {0}".format(date))
        current_reading = "Time: %s -- Latitude: %s deg %s min %s -- Longitude: %s deg %s min %s -- Altitude: %s %s" % (msg.timestamp, msg.lat[0:2], msg.lat[2::], msg.lat_dir, msg.lon[0:2], msg.lon[2::], msg.lon_dir, msg.altitude, msg.altitude_units)
        print("\nTime: %s -- Latitude: %s deg %s min %s -- Longitude: %s deg %s min %s -- Altitude: %s %s" % (msg.timestamp, msg.lat[0:2], msg.lat[2::], msg.lat_dir, msg.lon[0:2], msg.lon[2::], msg.lon_dir, msg.altitude, msg.altitude_units))
        print("\nTemperature: %.3f deg C -- Humidity: %.3f %%rH -- Pressure: %.3f Milibars" % (temp, humidity, pressure))

        # If the GPS reading isn't found, the last fix is also output
        if msg.lat == "":
            print()
            print("Last known GPS fix:\n%s" % (last))
            
        return msg.timestamp, msg.lat, current_reading, ""

    # If getting the date
    if string.find("RMC") > 0:
        info = string.split(",")
        # The date is returned to add to the other readings
        date = "20{0}-{1}-{2}".format(info[9][4:6], info[9][2:4], info[9][0:2])
        return "", "", "", date

def main():
    # The program keeps trying to find a reading and only outputs to shell when it finds one
    while True:
        try:
            string = serialPort.readline().decode("utf-8")
        except BlockingIOError:
            pass

        # The last readings are gained to be output if no fix is found
        last_reading = read_last()
        last_date = read_date()

        # The data is output and the reading/date is saved
        try:
            timestamp, lat, reading, date = parseGPS(string, last_reading, last_date)
            if lat != "":
                save_last(reading)
            if date != "":
                save_date(date)
            else:
                break
        except TypeError:
            pass

if __name__ == "__main__":
    main()
