import serial
import pynmea2
import datetime
import time
import csv
from sense_hat import SenseHat

# Makes SenseHat object
s = SenseHat()

# Defines serial port
serialPort = serial.Serial("/dev/ttyACM0", 9600, timeout=0.5)

# Functions for saving relevant data easily
def save_date(data):
    with open("last_date.txt", "w") as f:
        f.write(data)

def read_date():
    with open("last_date.txt", "r") as f:
        data = f.read()
    return data

def save_row(data):
    with open("last_row.txt", "w") as f:
        f.write(str(data))

def read_row():
    with open("last_row.txt", "r") as f:
        data = f.read()
    return int(data)

def save_fno(data):
    with open("last_file_no.txt", "w") as f:
        f.write(str(data))

def read_fno():
    with open("last_file_no.txt", "r") as f:
        data = f.read()
    return int(data)

def parseGPS(string, date):
    """
    This obtains relevant data from the GPS and either
     - returns fix data including a timestamp with an empty string for the date
     - or returns the date and nothing else
    """
    # If getting fix data
    if string.find("GGA") > 0:
        msg = pynmea2.parse(string)
        #print("Timestamp: %s -- Lat: %s %s -- Lon: %s %s -- Altitude: %s %s" % (msg.timestamp,msg.lat,msg.lat_dir,msg.lon,msg.lon_dir,msg.altitude,msg.altitude_units))
        # If date from the GPS is unavailable it uses datetime
        if date == "":
            full_timestamp = str(msg.timestamp) + 'T{:%Y-%m-%d}'.format(datetime.datetime.now())
        else:
            full_timestamp = str(msg.timestamp) + "T" + date
        # Returns GPS fix data and nothing for the date
        return msg.timestamp, full_timestamp, msg.lat, msg.lat_dir, msg.lon, msg.lon_dir, msg.altitude, msg.altitude_units, ""
    
    # If getting the date
    if string.find("RMC") > 0:
        items = string.split(",")
        date1 = items[9]
        # Returns nothing but a constructed date
        return "", "", "", "", "", "", "", "", "20{2}-{1}-{0}".format(date1[0:2], date1[2:4], date1[4:6])

def write_to_file(name, mpf):
    """
    This gets the current file name and the number of minutes the program should run for per file
    The function saves GPS data and SenseHAT sensor data to the CSV file
    It runs until the allotted time is elapsed, then opens a new file to save to
    (this means that there is still infomation saved if the program crashes)
    """
    # Converts to number of seconds to run and starts the timer to count time elapsed
    seconds_to_run = mpf * 60
    start_time = time.time()

    # Creates an object to write to CSV with and adds the column headings
    writefile = open(name, "w")
    datawriter = csv.writer(writefile, delimiter=",")
    datawriter.writerow(["ROW_ID", "TIMESTAMP", "LONG", "LONG_DIR", "LAT", "LAT_DIR", "ALT", "ALT_UNITS",
                         "TEMP_HUMIDITY", "TEMP_PRESSURE", "HUMIDITY", "PRESSURE"])

    # This loop runs for the allotted time per file
    while time.time() - start_time <= seconds_to_run:
    
         # Takes last read date from file
        date = read_date()
        
        while True:
            # Gets the message from the serial port
            string = serialPort.readline().decode("utf-8")
            try:
                # Assigns the GPS data to variables
                timestamp, full_timestamp, lat, lat_dir, lon, lon_dir, altitude ,altitude_units, date = parseGPS(string, date)
                if timestamp != None:
                    if date != "":
                        # If it's the date being found, then save date
                        save_date(date)
                    else:
                        # Otherwise continue to save to CSV
                        break
            except TypeError:
                pass

        # Gets the sensor data from the SenseHat
        temph = s.get_temperature_from_humidity()
        tempp= s.get_temperature_from_pressure()
        humidity = s.get_humidity()
        pressure = s.get_pressure()

        # Gets the row ID to save to file
        row_id = read_row()

        # Outputs what will be saved to file to the shell and then saves it as a CSV row
        print(row_id, full_timestamp, lat, lat_dir,lon,lon_dir,altitude,altitude_units, temph, tempp, humidity, pressure)
        datawriter.writerow([row_id, full_timestamp, lat, lat_dir,lon,lon_dir,altitude,altitude_units, temph, tempp, humidity, pressure])

        # The saved row ID is incremented for the next row
        save_row(row_id + 1)

    # Closes the file 
    writefile.close()

def main():
    # The number of minutes for writing to each file
    mpf = 1
    
    while True:
        # Reads the the last file number
        file_no = read_fno()

        # Saves GPS data to a file using a certain file name and a duration for the file
        write_to_file("GPS_values_%s.csv" % file_no, mpf)

        # Increments file number
        save_fno(file_no + 1)

if __name__ == "__main__":
    main()
