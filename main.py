import math
from flask import Flask, render_template, request, flash, redirect, url_for, request, session, jsonify
from flask_session import Session
import sqlite3
import os, string, random
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from math import *
import re
from geopy.geocoders import Nominatim

web_site = Flask(__name__)

web_site.config["SESSION_PERMANENT"] = False
web_site.config["SESSION_TYPE"] = "filesystem"
Session(web_site)


@web_site.route('/', methods=['GET', 'POST'])
@web_site.route('/Index', methods=['GET', 'POST'])
def index():
    msg = "" #default nothing
    usermsg = "" #default nothing
    empty = "" #set to nothing
    if request.method == 'POST':
        username = request.form["username"] #get the inputted username
        password = request.form["password"] #get the inputted password
        if username and password != "": #if they both aren't empty
            con = sqlite3.connect('database.db')
            sql = "SELECT password FROM Accounts WHERE username = ?" #if a password already exists with that username
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            getpassword = cursor.fetchone()
            critera = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!?*%@$&]).{8,}$") #password critera match
            if getpassword is None: #no password associated with inputted username then username is unique
                if " " not in username and len(username) >= 3 and len(username) <= 15: #username critera check
                    if bool(critera.match(password)): #password is valid
                        password = hash(password) #hash the password
                        sql = "INSERT INTO Accounts(username, password, description, dob) VALUES(?, ?, ?, ?)" #insert details into database
                        cursor = con.cursor()
                        cursor.execute(sql, (username, password, empty, empty))
                        con.commit()
                        return redirect("/login") #redirect them to login
                    else:
                        msg = "Password does not meet criteria" #error message if password isn't valid
                else:
                    usermsg = "Username does not meet criteria"#error message if username isn't valid
        else:
            msg = "Do not leave blank" #error message if either password or username left blank
    return render_template("Index.html", msg=msg, usermsg=usermsg) #render html page and send variables


def moderate(string):
    badworddict = {
        "shit": "shirt",  # little reference to "the good place", probably remove for actual project...
        "fuck": "fork",
        "bitch": "bench",
        "ass": "ash",
        "dick": "deck",
        "cock": "cork"
    }
    wordlist = string.split()
    moderatedlist = []

    for i in wordlist:
        lowerword = i.lower()
        if lowerword in badworddict:
            moderatedlist.append(badworddict[lowerword])
        else:
            moderatedlist.append(i)

    string = " ".join(moderatedlist)
    return string


def GetNamedLocation(lat, lng, id): #takes the lat, lng and id of the post/album
    try:
        geolocator = Nominatim(user_agent="web_site")
        latlng = str(lat) + ", " + str(lng) #concatonate the lat and lng to format required by library
        location = geolocator.reverse(latlng, language='en') #get entire location (place names in english)
        #try/except statements incase a marker isnt in a country/city/town

        try:
            country = location.raw['address']['country'] #location.raw is a dictionary so key/value pairs can be obtained
        except:
            country = "N/A"

        try:
            city = location.raw['address']['city']
        except:
            city = "N/A"

        try:
            town = location.raw['address']['town']
        except:
            town = "N/A"

        #if any are none, then set to n/a
        if country == None:
            country = "N/A"
        if city == None:
            city = "N/A"
        if town == None:
            town = "N/A"
        #since the id is passed the update can happen in the function
        con = sqlite3.connect('database.db')  #
        sql = "UPDATE Posts SET country = ?, city = ?, town = ? WHERE id = ?"
        cursor = con.cursor()
        cursor.execute(sql, (country, city, town, id,))
        con.commit()

        return
    except: #if any errors then default all to n/a
        country = "N/A"
        city = "N/A"
        town = "N/A"
        con = sqlite3.connect('database.db')
        sql = "UPDATE Posts SET country = ?, city = ?, town = ? WHERE id = ?"
        cursor = con.cursor()
        cursor.execute(sql, (country, city, town, id,))
        con.commit()
        return


def hash(password):
    def xor_bytes(byte1, byte2):
        return byte1 ^ byte2

    ascii = ""
    for i in password:
        ascii += str(ord(i))

    if len(ascii) % 2 != 0:
        ascii += '0' * len(ascii)

    ascii = [ascii[i:i + 2] for i in range(0, len(ascii), 2)]

    newstring = ""
    for i in ascii:
        newstring += str(bin(int(i)))

    newstring = newstring.replace("0b", "")

    while len(newstring) < 128:
        newstring += "0"

    newstring = [newstring[i:i + 16] for i in range(0, len(newstring), 16)]
    nextbyte = int()
    for i in range(len(newstring) - 1):
        nextbyte = xor_bytes(nextbyte, int(newstring[i + 1]))
    return str(nextbyte)


@web_site.route('/ajaxsearchusernames/<search>')
def ajaxsearchusernames(search):
    search = search.replace("%20", " ") #replaces any "%20"s with spaces

    con = sqlite3.connect('database.db')
    sql = "SELECT password FROM Accounts WHERE username = ?"
    cursor = con.cursor()
    cursor.execute(sql, (search,))
    getpassword = cursor.fetchone() #checks if unique
    if getpassword is None:
        unique = "Check_green_circle.svg.png" #if unique, a tick should show
    else:
        unique = "1024px-Cross_red_circle.svg.png"
    if len(search) >= 3 and len(search) <= 15: #checks length is between 3 and 15 chars
        length = "Check_green_circle.svg.png"
    else:
        length = "1024px-Cross_red_circle.svg.png"

    if " " not in search and not search[0].isspace() and not search[-1].isspace(): #makes sure no spaces are present and there aren't any spaces at the beginning or end
        space = "Check_green_circle.svg.png"
    else:
        space = "1024px-Cross_red_circle.svg.png"

    if search == "empty":
        unique = "1024px-Cross_red_circle.svg.png"
        length = "1024px-Cross_red_circle.svg.png"

    return jsonify({'unique': unique, 'space': space, 'length': length})
    #constructs the json to send to the javascript

@web_site.route('/ajaxpasswords/<search>')
def ajaxpasswords(search):
    search = search.replace("%20", " ")
    username = session["username"]
    con = sqlite3.connect('database.db')
    sql = "SELECT password FROM Accounts WHERE username = ?"
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    getpassword = cursor.fetchone()
    oldpassword = getpassword[0]
    uppercheck = False
    lowercheck = False
    digitcheck = False
    symbcheck = False
    upper = "1024px-Cross_red_circle.svg.png"
    lower = "1024px-Cross_red_circle.svg.png"
    digit = "1024px-Cross_red_circle.svg.png"
    symb = "1024px-Cross_red_circle.svg.png"
    symbols = ["!", "*", "%", "@", "$", "&"]
    if len(search) >= 8:  # Check length is at least 8
        length = "Check_green_circle.svg.png"
    else:
        length = "1024px-Cross_red_circle.svg.png"
    for i in range(0, len(search)):
        if search[i].isupper():  # Check if at least one char is uppercase
            uppercheck = True
            upper = "Check_green_circle.svg.png"
        if search[i].islower():  # Check if at least one char is lowercase
            lowercheck = True
            lower = "Check_green_circle.svg.png"
        if search[i].isdigit():  # Check if at least one char is a digit
            digitcheck = True
            digit = "Check_green_circle.svg.png"
        if search[i] in symbols:  # Check if at least one char is in the list symbols
            symbcheck = True
            symb = "Check_green_circle.svg.png"
    if not uppercheck or search == "empty":#if empty or not true then set to red cross
        upper = "1024px-Cross_red_circle.svg.png"
    if not lowercheck or search == "empty":
        lower = "1024px-Cross_red_circle.svg.png"
    if not digitcheck or search == "empty":
        digit = "1024px-Cross_red_circle.svg.png"
    if not symbcheck or search == "empty":
        symb = "1024px-Cross_red_circle.svg.png"

    if hash(search) == oldpassword:
        matching = "Check_green_circle.svg.png"
    else:
        matching = "1024px-Cross_red_circle.svg.png"

    return jsonify(
        {'upper': upper, 'length': length, 'lower': lower, 'digit': digit, 'symb': symb, 'matching': matching})


@web_site.route('/ajaxpasswordsindex/<search>')
def ajaxpasswordsindex(search):
    search = search.replace("%20", " ") #replace any "%20" with spaces
    uppercheck = False #default to False
    lowercheck = False #default to False
    digitcheck = False #default to False
    symbcheck = False #default to False
    upper = "1024px-Cross_red_circle.svg.png" #default to the red cross (False)
    lower = "1024px-Cross_red_circle.svg.png" #default to the red cross (False)
    digit = "1024px-Cross_red_circle.svg.png" #default to the red cross (False)
    symb = "1024px-Cross_red_circle.svg.png" #default to the red cross (False)
    symbols = ["!", "*", "%", "@", "$", "&"] #valid symbols
    if len(search) >= 8:  # Check length is at least 8
        length = "Check_green_circle.svg.png" #if True set to green tick
    else:
        length = "1024px-Cross_red_circle.svg.png"
    for i in range(0, len(search)):
        if search[i].isupper():  # Check if at least one char is uppercase
            uppercheck = True
            upper = "Check_green_circle.svg.png"
        if search[i].islower():  # Check if at least one char is lowercase
            lowercheck = True
            lower = "Check_green_circle.svg.png"
        if search[i].isdigit():  # Check if at least one char is a digit
            digitcheck = True
            digit = "Check_green_circle.svg.png"
        if search[i] in symbols:  # Check if at least one char is in the list symbols
            symbcheck = True
            symb = "Check_green_circle.svg.png"
    if not uppercheck or search == "empty": #if empty or not true then set to red cross
        upper = "1024px-Cross_red_circle.svg.png"
    if not lowercheck or search == "empty":
        lower = "1024px-Cross_red_circle.svg.png"
    if not digitcheck or search == "empty":
        digit = "1024px-Cross_red_circle.svg.png"
    if not symbcheck or search == "empty":
        symb = "1024px-Cross_red_circle.svg.png"

    return jsonify({'upper': upper, 'length': length, 'lower': lower, 'digit': digit, 'symb': symb})
    #construct json to send to the javascript

@web_site.route('/login', methods=['GET', 'POST'])
def login():
    msg = "" #defaults to blank
    if request.method == "POST":
        username = request.form["username"] #gets inputted username
        password = request.form["password"] #gets inputted password
        if username and password != "": #if both fields aren't blank
            con = sqlite3.connect('database.db')
            sql = "SELECT password FROM Accounts WHERE username = ?" #gets the password that corresponds to the account
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            getpassword = cursor.fetchone()
            if getpassword is not None: #if a password actually exists, then its an existing/valid account
                getpassword = getpassword[0] #remove from tuple
                password = hash(password) #hash the inputted password
                if password == getpassword: #if the hash of the inputted password matches the hash stored in the database
                    session["username"] = username #set the session username to the inputted username
                    return redirect(url_for('listmyposts')) #redirect to "my account" page
                else:
                    msg = "Incorrect Password" #error message if password does not match
            else:
                msg = "Username not found" #error message if username does not exist
        else:
            msg = "Do not leave blank" #error message if either password or username are left blank
    return render_template("login.html", msg=msg)


@web_site.route('/coords', methods=['POST'])
def coords():
    data = request.get_json()
    lat = data.get('lat')
    lng = data.get('lng')
    clicked = data.get('clicked')
    session['lat'] = round(lat, 8)
    session['lng'] = round(lng, 8)
    session['clicked'] = clicked

    return "Success"


@web_site.route('/filtercoords', methods=['POST'])
def filtercoords():
    data = request.get_json()
    lat = data.get('lat')
    lng = data.get('lng')

    session['filterlat'] = round(lat, 8)
    session['filterlng'] = round(lng, 8)
    radius = data.get('radius')
    session['radius'] = radius

    return "Success"


def get_metadata(photo_path):
    metadata = {}
    image = Image.open(photo_path) #open image
    exifdata = image._getexif() #get EXIF daya
    if exifdata is not None:  #if there is any EXIF data
        for tag, value in exifdata.items(): #go through all the EXIF data
            tagname = TAGS.get(tag, tag)  #get the name of the tag (from numberical form)
            metadata[tagname] = value #add to dictionary with name of tag and its value
    return metadata


def convertGPS(gpsdata):  # converts DMS to lat and lng
    try:
        latdegrees = float((gpsdata[2][0]))
        print(latdegrees)
        latmin = float((gpsdata[2][1]))
        print(latmin)
        latsec = float((gpsdata[2][2]))
        print(latsec)

        lngdegrees = float((gpsdata[4][0]))
        print(lngdegrees)
        lngmin = float((gpsdata[4][1]))
        print(lngmin)
        lngsec = float((gpsdata[4][2]))
        print(lngsec)

        lat = latdegrees + (latmin / 60) + (latsec / 3600) #equation
        lng = lngdegrees + (lngmin / 60) + (lngsec / 3600)

        lat = round(lat, 8) #round to standard of 8 decimal points
        lng = round(lng, 8)
        if gpsdata[1] == 'S': #if s then lat needs to be flipped
            lat = -lat
        if gpsdata[3] == 'W': #if w then lng needs to be flipped
            lng = -lng

        return lat, lng
    except:
        return None, None


def randomfilename(path):  # calc the probability
    randstr = ""
    letters = string.ascii_letters
    for i in range(20):
        randstr += random.choice(letters)
    datetimenow = datetime.now()
    formattedtime = datetimenow.strftime("%d%m%y%H%M%S%f")[:-3]
    filename = (randstr + formattedtime)

    filepath = os.path.join(path, filename)

    if os.path.exists(filepath):
        return randomfilename(
            path)  # recursive until you find a unique one, but probably unnecessary (guarantees unique anyway)
    else:
        return filename


@web_site.route('/uploadphoto', methods=['GET', 'POST'])
def uploadphoto():
    if "username" not in session: #if no user is logged in
        return redirect("/login") #redirect to login page

    posted = False #set posted to false (nothing posted yet)
    prevpostid = request.args.get('id') #if the user has just previously posted a post, get its id
    if prevpostid != None: #if there is actually a previous post id
        posted = True #set posted to true
    msg = "" #if nothing posted previously set message to empty

    if request.method == 'POST': #a button clicked
        datetimenow = datetime.now() #get time now
        formattedtime = datetimenow.strftime("%d/%m/%y %H:%M") #put time now in known format
        randfilename = randomfilename(os.path.join(web_site.root_path, 'static', 'UploadedPhotos')) #create a random filename
        username = session["username"] #get the user that is logged in (posted the post)
        photo = request.files['photo'] #get the photo they uploaded
        if photo.filename != "": #if there is a photo (error prevention)
            filename = randfilename + "_" + photo.filename.replace(" ", "") #concatonate the filename
            try: #erros likely if not proper file type
                photo.save(os.path.join(web_site.root_path, 'static', 'UploadedPhotos', filename)) #save the file
                con = sqlite3.connect('database.db')
                sql = "INSERT INTO tempphotos(filename, user) VALUES(?,?)" #save the file to database
                cursor = con.cursor()
                cursor.execute(sql, (filename, username))
                con.commit()

                sql = "SELECT id FROM tempphotos WHERE filename = ? AND user = ?" #get the id of the post whos photo it is
                cursor = con.cursor() #filename and username both unique so able to get id with no clashes
                cursor.execute(sql, (filename, username))
                getid = cursor.fetchone()
                getid = getid[0] #out of tuple form

                photo_path = os.path.join(web_site.root_path, 'static', 'UploadedPhotos', filename) #get the filepath of the photo they uploaded

                metadata = get_metadata(photo_path) #try to get metadata using func (this is where errors will occur if wrong file type)
                #get all metadata I chose, format is tag, followed by alternative if nothing there i.e., "N/A"
                make = str(metadata.get('Make', 'N/A'))
                model = str(metadata.get('Model', 'N/A'))
                metadatadatetime = str(metadata.get('DateTime', 'N/A'))
                ISO = str(metadata.get('ISOSpeedRatings', 'N/A'))
                LensModel = str(metadata.get('LensModel', 'N/A'))
                FNumber = str(metadata.get('FNumber', 'N/A'))
                ExposureTime = str(metadata.get('ExposureTime', 'N/A'))
                if ExposureTime != "N/A":
                    ExposureTime = str(round(1 / float(ExposureTime))) #stored as decimal but common format is fraction so convert
                if metadatadatetime == "N/A":
                    metadatadatetime = str(metadata.get('DateTimeOriginal', 'N/A'))  # try other tag if other is empty

                if metadatadatetime != "N/A": #if a datetime found
                    metadatadatetime = metadatadatetime[:-3]# remove the last 3 chars which are milliseconds (not wanted)
                    metadatadatetime = metadatadatetime.replace(":", "-", 2) #library uses - not : for date so replace first 2 occurances (2023-12-18 18:12 instead of 2023:12:18 18:12)

                gps_string = metadata.get('GPSInfo', 'N/A') #get gps
                if gps_string != "N/A": #if none then convert Degrees, minutes and seconds into long lat using function
                    output = convertGPS(gps_string)
                    lat = output[0]
                    lng = output[1]
                else:
                    lat = None #if no gps data then set to none
                    lng = None

                sql = "UPDATE tempphotos SET make = ?, model = ?, timeposted = ?, datetime = ?, ISO = ?, lensmodel = ?, fstop = ?, shutterspeed = ?, lat = ?, lng = ? WHERE id = ?"
                cursor = con.cursor() #insert into tempphotos table
                cursor.execute(sql, (
                make, model, formattedtime, metadatadatetime, ISO, LensModel, FNumber, ExposureTime, lat, lng, getid,))
                con.commit()

                return redirect(url_for('addpost', id=getid)) #redirect to add post with the id of the tempphoto
            except:
                msg = "Image Error..." #if there is an error during this process, the file type is incorrect so provide error message
                os.remove(os.path.join(web_site.root_path, 'static', 'UploadedPhotos', filename)) #delete the file
                con = sqlite3.connect('database.db')
                sql = "DELETE FROM tempphotos WHERE filename = ? and user = ?" #delete any information related to the filename from temphotos
                cursor = con.cursor()
                cursor.execute(sql, (filename, username))
                con.commit()
        else:
            msg = "Please select an image" #if button pressed but no image selected, provide error message
    return render_template("uploadphoto.html", prevpostid=prevpostid, posted=posted, msg=msg)


@web_site.route('/addpost', methods=['GET', 'POST'])
def addpost():
    if "username" not in session: #check if a user is logged in
        return redirect("/login") #if no user logged in, redirect to login page

    photoid = request.args.get('id') #get the id of the photo in tempphotos
    username = session["username"] #get the user that is logged in
    emptytitle = False #set the title and descr empty state to False
    emptydescr = False
    con = sqlite3.connect('database.db')
    sql = "SELECT filename FROM tempphotos WHERE id = ?" #get the filename
    cursor = con.cursor()
    cursor.execute(sql, (photoid,))
    getfilename = cursor.fetchone()
    filename = getfilename[0] #out of tuple form

    con = sqlite3.connect('database.db')
    sql = "SELECT user FROM tempphotos WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (photoid,))
    getuser = cursor.fetchone()
    getuser = getuser[0] #get the user that posted it
    if not getuser: #if doesnt exist
        return render_template('404.html') #
    if getuser != username:
        return render_template('404.html') #if it is not the user's post then give error (avoids manual entry of URL)

    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT * FROM tempphotos WHERE id = ? AND user = ?" #get all the info
    cursor.execute(sql, (photoid, username))
    con.commit()
    rows2 = cursor.fetchall()

    sql = "Select datetime FROM tempphotos WHERE id = ? AND user = ?" #get the datetime
    cursor = con.cursor()
    cursor.execute(sql, (photoid, username))
    datetimeup = cursor.fetchone()
    datetimeup = datetimeup[0]

    date = datetimeup[:10] #split datetime into date and time
    time = datetimeup[11:]

    msg = "" #default message to empty

    sql = "SELECT privacy FROM Accounts WHERE username = ?"
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    getprivacy = cursor.fetchone()
    getprivacy = getprivacy[0] #get the privacy of the user

    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT * FROM Posts WHERE album = 'True' AND user = ?" #get all the existing albums the user has
    cursor.execute(sql, (username,))
    rows = cursor.fetchall()

    if request.method == 'POST':
        datetimenow = datetime.now() #get the datetime now
        formattedtime = datetimenow.strftime("%d/%m/%y %H:%M") #format datetime
        sessionlat = session.get('lat') #get the lng and lat they clicked
        sessionlng = session.get('lng')

        text = request.form["text"] #get the title they chose
        text = moderate(text)
        descr = request.form["descr"] #get the description they chose
        descr = moderate(descr)
        selected_option = request.form['selected_option'] #add to album choice
        make = request.form["make"] #get the camera make they entered
        model = request.form["model"] #get the camera model they entered
        date = request.form["date"] #get the date they chose
        time = request.form["time"] #get the time they chose
        if date != "" and time != "": #if date and time have been modified
            metadatadatetime = str(date) + " " + str(time) #concactonate so can be stored together in database
        elif date != "" and time == "":
            metadatadatetime = str(date) + " " + "12:00" #if date chosen but not time, set time to default 12:00
        else:
            metadatadatetime = "N/A" #if only time chosen or neither, set to N/A
        ISO = request.form["ISO"] #get the ISO they chose
        LensModel = request.form["lensmodel"] #get the lensmodel they chose
        FNumber = request.form["fstop"] #get the aperture they chose
        ExposureTime = request.form["shutterspeed"] #get the shutterspeed they chose

        #if any details are left empty then set to N/A
        if make == "" or make.isspace():
            make = "N/A"
        if model == "" or model.isspace():
            model = "N/A"
        if metadatadatetime == "" or metadatadatetime.isspace():
            metadatadatetime = "N/A"
        if ISO == "" or ISO.isspace():
            ISO = "N/A"
        if LensModel == "" or LensModel.isspace():
            LensModel = "N/A"
        if FNumber == "" or FNumber.isspace():
            FNumber = "N/A"
        if ExposureTime == "" or ExposureTime.isspace():
            ExposureTime = "N/A"


        if "cancel" in request.form: #if they clicked cancel
            con = sqlite3.connect('database.db')
            sql = "Select filename FROM tempphotos WHERE id = ?" #get the filename
            cursor = con.cursor()
            cursor.execute(sql, (photoid,))
            getfilename = cursor.fetchone()
            filename = getfilename[0]
            os.remove(os.path.join(web_site.root_path, 'static', 'UploadedPhotos', filename)) #delete the file

            sql = "DELETE FROM tempphotos WHERE id = ? AND user = ?" #delete from tempphotos
            cursor = con.cursor()
            cursor.execute(sql, (photoid, username))
            con.commit()
            session['lat'] = 0 #set lat and lng back to 0
            session['lng'] = 0
            return redirect(url_for('uploadphoto')) #back to upload photo page
        if "drafts" in request.form: #if they chose to save to drafts
            if sessionlng == None or sessionlat == None: #if no location chosen
                sessionlng = 0 #default the post location to 0,0
                sessionlat = 0
            #if title or descr are empty, give default title/descr or "untitled"
            if text == "":
                text = "Untitled"
            if descr == "":
                descr = "Untitled"
            con = sqlite3.connect('database.db')  #
            sql = "UPDATE tempphotos SET make = ?, model = ?, timeposted = ?, datetime = ?, ISO = ?, lensmodel = ?, fstop = ?, shutterspeed = ?, lng = ?, lat = ?, text = ?, descr = ? WHERE id = ?" #update tempphotos table
            cursor = con.cursor()
            cursor.execute(sql, (
            make, model, formattedtime, metadatadatetime, ISO, LensModel, FNumber, ExposureTime, sessionlng, sessionlat,
            text, descr, photoid))
            con.commit()
            session['lat'] = 0 #set lng and lat back to 0
            session['lng'] = 0
            return redirect(url_for('uploadphoto'))
        elif "submit" in request.form: #they chose to post the...post
            if text != "": #title isnt empty
                if descr != "": #descr isnt empty
                    if sessionlng == None or sessionlat == None:
                        sessionlng = 0 #if no location chosen, default to 0,0
                        sessionlat = 0
                    timeposted = formattedtime #(just a rename)
                    con = sqlite3.connect('database.db')
                    sql = "INSERT INTO Posts(text,timeposted,user,filename, descr, privacy, lng, lat) VALUES(?,?,?,?,?,?,?,?)" #add into posts table
                    cursor = con.cursor()
                    cursor.execute(sql, (text, timeposted, username, filename, descr, getprivacy, sessionlng, sessionlat,))
                    con.commit()
                    sql = "SELECT id FROM Posts WHERE text = ? AND filename = ? AND user = ? AND timeposted = ? AND descr = ?"  #get the id of the post, filename is unique so ok, others for security
                    cursor.execute(sql, (text, filename, username, timeposted, descr))
                    postidtup = cursor.fetchone()
                    postid = postidtup[0] #post id

                    sql = "INSERT INTO photodetails(make, model, datetime, ISO, lensmodel, fstop, shutterspeed,id) VALUES(?,?,?,?,?,?,?,?)" #insert the post info into the photodetails table
                    cursor = con.cursor()
                    cursor.execute(sql, (make, model, metadatadatetime, ISO, LensModel, FNumber, ExposureTime, postid))
                    con.commit()

                    GetNamedLocation(sessionlat, sessionlng, postid) #get the town,city and country the post location is in

                    if selected_option != "none": #if an album selected
                        con = sqlite3.connect('database.db')
                        sql = "SELECT id FROM Posts WHERE text = ? AND user = ? AND album = 'True'" #get the id of the album with the title (titles are unique)
                        cursor = con.cursor()
                        cursor.execute(sql, (selected_option, username,))
                        getalbumid = cursor.fetchone()
                        getalbumid = getalbumid[0]

                        sql = "INSERT INTO albums(albumid, postid, user) VALUES(?,?,?)" #insert into albums table the post id and the album id
                        cursor = con.cursor()
                        cursor.execute(sql, (getalbumid, postid, username,))  #
                        con.commit()
                        updatealbumlocation(getalbumid)

                    con = sqlite3.connect('database.db')
                    sql = "DELETE FROM tempphotos WHERE id = ? AND user = ?" #delete post from tempphotos (not a draft anymore)
                    cursor = con.cursor()
                    cursor.execute(sql, (photoid, username))
                    con.commit()
                    session['lat'] = 0 #set lng and lat to 0
                    session['lng'] = 0
                    return redirect(url_for('uploadphoto', id=postid)) #redirect to upload photo page with id to allow for "view post" button
                else:
                    session['lat'] = 0 #if they left the descr field empty
                    session['lng'] = 0
                    msg = "Do not leave blank" #give appropriate error message
                    emptydescr = True #set the empty descr state to true (allows for auto scroll)
            else:
                session['lat'] = 0 #if they left the title field empty
                session['lng'] = 0
                msg = "Do not leave blank" #give appropriate error message
                emptytitle = True #set the empty title state to true (allows for auto scroll)
    return render_template("addpost.html", msg=msg, rows=rows, filename=filename, rows2=rows2, date=date, time=time, emptydescr=emptydescr, emptytitle=emptytitle)


@web_site.route('/drafts', methods=['GET', 'POST'])
def drafts():
    if "username" not in session:
        return redirect("/login")

    msg = ""
    username = session["username"]

    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT * FROM tempphotos WHERE user = ?"  # gets every postid that the user has posted to drafts
    cursor.execute(sql, (username,))
    rows = cursor.fetchall()
    for row in rows:
        text = row["text"]
        descr = row["descr"]
        if text == None:
            newtext = "Untitled"
            sql = "UPDATE tempphotos SET text = ? WHERE id = ?"  # gets every postid that the user has posted to drafts
            cursor.execute(sql, (newtext, row["id"]))
            con.commit()
        if descr == None:
            newdescr = "Untitled"
            sql = "UPDATE tempphotos SET descr = ? WHERE id = ?"  # gets every postid that the user has posted to drafts
            cursor.execute(sql, (newdescr, row["id"]))
            con.commit()

    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT * FROM tempphotos WHERE user = ?"  # gets every postid that the user has posted to drafts
    cursor.execute(sql, (username,))
    rows = cursor.fetchall()
    rowsinsec = []
    for row in rows:
        getdatetime = datetime.strptime(row["timeposted"], "%d/%m/%y %H:%M")  # converts to known format
        datetimenow = datetime.now()  # Gets time now
        datetimedif = datetimenow - getdatetime  # finds dif
        timedif = datetimedif.total_seconds()  # converts dif to s
        rowdict = dict(row)  # sets var to old dict of row
        rowdict['timedif'] = timedif  # adds sec dif to dict
        rowsinsec.append(rowdict)  # appends to list

    rows = sorted(rowsinsec, key=lambda x: x.get('timedif'))
    if rows == []:
        msg = "No drafts"

    return render_template("drafts.html", rows=rows, msg=msg)


@web_site.route('/removefromdrafts', methods=['GET', 'POST'])
def removefromdrafts():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    postid = request.args.get('id')

    con = sqlite3.connect('database.db')
    sql = "SELECT user FROM tempphotos WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    getuser = cursor.fetchone()
    if not getuser:
        return render_template('404.html')
    if getuser[0] != username:
        return render_template('404.html')

    deleted = False
    if request.method == "POST":
        if "yes" in request.form:
            con = sqlite3.connect('database.db')
            sql = "Select filename FROM tempphotos WHERE id = ?"
            cursor = con.cursor()
            cursor.execute(sql, (postid,))
            getfilename = cursor.fetchone()
            filename = getfilename[0]
            os.remove(os.path.join(web_site.root_path, 'static', 'UploadedPhotos', filename))  # deletes the file

            con.row_factory = sqlite3.Row
            sql = "DELETE FROM tempphotos WHERE id = ?"
            cursor = con.cursor()
            cursor.execute(sql, (postid,))
            con.commit()

            deleted = True
        elif "no" in request.form:
            return redirect(url_for('drafts'))
    return render_template("removefromdrafts.html", deleted=deleted)


@web_site.route('/addalbum', methods=['GET', 'POST'])
def addalbum():
    if "username" not in session:
        return redirect("/login")

    msg = ""
    msg2 = ""
    username = session["username"]
    filename = "7da6b012d99beac0c7eff0949b27b7e6.png"
    if request.method == "POST":
        datetimenow = datetime.now()
        formattedtime = datetimenow.strftime("%d/%m/%y %H:%M")
        con = sqlite3.connect('database.db')
        sql = "SELECT privacy FROM Accounts WHERE username = ?"
        cursor = con.cursor()
        cursor.execute(sql, (username,))
        getprivacy = cursor.fetchone()
        getprivacy = getprivacy[0]
        if "create" in request.form:
            text = request.form["text"]
            text = moderate(text)
            descr = request.form["descr"]
            descr = moderate(descr)

            if text != "":
                if descr == "":
                    descr = "Untitled"
                con = sqlite3.connect('database.db')
                sql = "SELECT id FROM Posts WHERE user = ? AND text = ? AND album = 'True'"
                cursor = con.cursor()
                cursor.execute(sql, (username, text,))
                getunid = cursor.fetchone()

                if getunid is None:
                    con = sqlite3.connect('database.db')
                    sql = "INSERT INTO Posts(text,user, descr, filename, privacy,album, timeposted) VALUES(?,?,?,?,?,?,?)"
                    cursor = con.cursor()
                    cursor.execute(sql, (text, username, descr, filename, getprivacy, "True", formattedtime,))
                    con.commit()
                    return redirect(url_for('listmyposts'))
                else:
                    msg = "Cannot have duplicate album names"
            else:
                msg2 = "Do not leave title blank"
    return render_template("addalbum.html", msg=msg, msg2=msg2)


def sortdatetime(dict):
    sorteddict = sorted(dict.items(), key=lambda dict: dict[1])
    return sorteddict


def formatdattime(datetimeprovided):
    if datetimeprovided != "N/A":
        datetimenow = datetime.now()
        datetimedif = datetimenow - datetimeprovided
        total = datetimedif.total_seconds()
        return total
    else:
        total = 0
        return total


def updatealbumlocation(albumid):  # also updates the average likes
    listofpostids = []
    latavg = 0
    lngavg = 0
    total = 0
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT postid FROM albums WHERE albumid = ?"  # gets every postid that the user has posted
    cursor.execute(sql, (albumid,))
    for row in cursor.fetchall():
        listofpostids.append(row[0])

    for i in listofpostids:
        sql = "SELECT lat, lng FROM Posts WHERE id = ?"  # go through every post and get lat lng of each
        cursor.execute(sql, (i,))
        lnglat = cursor.fetchone()
        if lnglat is not None:
            if lnglat[0] is not None and lnglat[1] is not None:
                latavg += float(lnglat[0])
                lngavg += float(lnglat[1])

    if latavg != 0 and lngavg != 0:
        latavg = latavg / len(listofpostids)
        lngavg = lngavg / len(listofpostids)
    else:
        latavg = None
        lngavg = None
    con = sqlite3.connect('database.db')
    sql = "UPDATE Posts SET lat = ?, lng = ? WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (latavg, lngavg, albumid,))  #
    con.commit()

    listofpostids = []
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT postid FROM albums WHERE albumid = ?"
    cursor.execute(sql, (albumid,))
    allids = cursor.fetchall()
    for row in allids:
        listofpostids.append(row[0])
    for x in listofpostids:
        sql = "SELECT likes FROM Posts WHERE id = ?"  # avg likes of all posts (rounded up)
        cursor.execute(sql, (x,))
        likes = cursor.fetchone()
        if likes is not None:
            total += int(likes[0])
    if total != 0:
        average = total / len(listofpostids)
    else:
        average = 0

    average = math.ceil(average)

    sql = "UPDATE Posts SET likes = ? WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (average, albumid,))  #
    con.commit()

    GetNamedLocation(latavg, lngavg, albumid)
    return


@web_site.route('/viewalbum', methods=['GET', 'POST'])
def viewalbum():
    if "username" not in session:
        return redirect("/login")

    listofpostids = []
    sorteddatetime = {}
    username = session["username"]
    albumid = request.args.get('id')

    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    sql = "SELECT privacy,user FROM Posts WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (albumid,))
    postinfo = cursor.fetchall()
    if not postinfo:
        return render_template('404.html')
    getprivacy = postinfo[0]['privacy']
    getuser = postinfo[0]['user']
    # get the album id if its in one

    sql = "SELECT status FROM friendrequests WHERE usersend = ? AND userreceive = ? "
    cursor = con.cursor()
    cursor.execute(sql, (username, getuser,))
    getstatus = cursor.fetchone()
    if getstatus is None:
        getstatus = "0"
    getstatus = getstatus[0]
    if getprivacy == "private" and getstatus != 2 and getuser != username:
        return redirect(url_for('viewaccount', id=getuser))

    sql = "SELECT * FROM Accounts WHERE username = (SELECT user FROM Posts WHERE id = ?)"
    cursor = con.cursor()
    con.row_factory = sqlite3.Row
    cursor.execute(sql, (albumid,))
    userrows = cursor.fetchall()

    sql = "SELECT user FROM Posts WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (albumid,))
    getalbumuser = cursor.fetchone()
    getalbumuser = getalbumuser[0]

    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT postid FROM albums WHERE albumid = ?"
    cursor.execute(sql, (albumid,))
    for row in cursor.fetchall():
        listofpostids.append(row[0])

    datetimedict = {}
    unformatposts = []
    for i in listofpostids:
        sql = "SELECT datetime FROM photodetails WHERE id = ?"  # go through every post and get datetime of each
        cursor.execute(sql, (i,))
        getdatetime = cursor.fetchone()
        if getdatetime[0] != "N/A":
            getdatetime = datetime.strptime(getdatetime[0], "%Y-%m-%d %H:%M")
            formatdattimetotal = formatdattime(getdatetime)  # gets how many seconds ago it was taken
            datetimedict[
                i] = formatdattimetotal  # adds the seconds value to a dictionary with the key being the post id (i)
            sorteddatetime = sortdatetime(datetimedict)
            sorteddatetime = sorteddatetime[::-1]  # sorts it
        else:
            unformatposts.append(i)  # posts without a time
    sortedpostids = []
    for i in sorteddatetime:
        sortedpostids.append(i[
                                 0])  # once the dictinary is sorted in seconds ago then remove the seconds so just a list of postids in chronological order
    sortedpostids += unformatposts
    lnglatpoints = []
    filenames = []

    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    postinfo = []
    for postid2 in sortedpostids:
        sql = """SELECT Posts.*, Accounts.pfp
                 FROM Posts
                 JOIN Accounts ON Accounts.username = Posts.user
                 WHERE Posts.id = ?"""
        cursor.execute(sql, (postid2,))
        postresult = cursor.fetchone()
        if postresult:
            postinfo.append(postresult)

    cursor = con.cursor()
    for postid2 in sortedpostids:
        sql = "SELECT lng, lat, filename FROM Posts WHERE id = ?"
        cursor.execute(sql, (postid2,))
        postresult = cursor.fetchone()
        if postresult:
            lnglattemp = []
            lnglattemp.append(postresult[1])
            lnglattemp.append(postresult[0])
            lnglattemp.append(postid2)
            lnglatpoints.append(lnglattemp)
            filenames.append(postresult[2])

    con.row_factory = sqlite3.Row
    sql = "Select * FROM Posts WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (albumid,))
    rows2 = cursor.fetchall()  # rows 2 is for album info

    con = sqlite3.connect('database.db')
    sql = "SELECT savedpostid FROM savedposts WHERE savedpostid = ? and username = ?"
    cursor = con.cursor()
    cursor.execute(sql, (albumid, username))
    getsavedid = cursor.fetchone()
    if getsavedid is not None:
        checksaved = True
    else:
        checksaved = False

    imagesize = []
    for i in filenames:
        path = "static/UploadedPhotos/" + i
        with Image.open(path) as img:
            heightwidth = []
            heightwidth.append(img.size[1])
            heightwidth.append(img.size[0])  # get the width and height of the image
            imagesize.append(heightwidth)

    if request.method == "POST":
        if "save" in request.form:
            if checksaved == False:
                con = sqlite3.connect('database.db')
                sql = "INSERT INTO savedposts(savedpostid, username) VALUES(?, ?)"
                cursor = con.cursor()
                cursor.execute(sql, (albumid, username))
                con.commit()
                return redirect(url_for('viewalbum', id=albumid))
        elif "unsave" in request.form:
            con = sqlite3.connect('database.db')
            sql = "DELETE FROM savedposts WHERE savedpostid = ? AND username = ?"
            cursor = con.cursor()
            cursor.execute(sql, (albumid, username))
            con.commit()
            return redirect(url_for('viewalbum', id=albumid))
    return render_template("viewalbum.html", rows=postinfo, rows2=rows2, username=username, userrows=userrows,
                           getalbumuser=getalbumuser, checksaved=checksaved, lnglatpoints=lnglatpoints,
                           filenames=filenames, imagesize=imagesize)


@web_site.route('/removefromalbum', methods=['GET', 'POST'])
def removefromalbum():
    if "username" not in session:
        return redirect("/login")

    albumid = request.args.get('albumid')
    postid = request.args.get('postid')

    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "DELETE FROM albums WHERE albumid = ? AND postid = ?"
    cursor.execute(sql, (albumid, postid))
    con.commit()

    updatealbumlocation(albumid)
    msg = "Post was removed"
    return render_template("removefromalbum.html", msg=msg, albumid=albumid)


@web_site.route('/editalbum', methods=['GET', 'POST'])
def editalbum():
    if "username" not in session:
        return redirect("/login")

    albumid = request.args.get('id')
    username = session["username"]
    con = sqlite3.connect('database.db')
    msg = ""
    msg2 = ""
    sql = "SELECT user FROM Posts WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (albumid,))
    getuser = cursor.fetchone()
    if not getuser:
        return render_template('404.html')
    if getuser[0] != username:
        return render_template('404.html')

    con.row_factory = sqlite3.Row
    sql = "SELECT * FROM Posts WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (albumid,))
    rows = cursor.fetchall()
    if request.method == "POST":
        if "cancel" in request.form:
            return redirect(url_for('viewalbum', id=albumid))

        description = request.form["description"]
        description = moderate(description)
        text = request.form["text"]
        text = moderate(text)
        if text != "":
            if description == "":
                description = "Untitled"
            con = sqlite3.connect('database.db')
            sql = "SELECT id FROM Posts WHERE user = ? AND text = ? AND album = 'True'"
            cursor = con.cursor()
            cursor.execute(sql, (username, text,))
            getunid = cursor.fetchone()

            if getunid is None:
                con = sqlite3.connect('database.db')
                sql = "UPDATE Posts SET descr = ?, text = ? WHERE id = ?"
                cursor = con.cursor()
                cursor.execute(sql, (description, text, albumid,))
                con.commit()
                return redirect(url_for('viewalbum', id=albumid))
            else:
                msg = "Cannot have duplicate album names"
        else:
            msg2 = "Do not leave title blank"
    return render_template("editalbum.html", rows=rows, albumid=albumid, msg=msg, msg2=msg2)


def calcage(dob):
    try: #incase the date of birth has not been set and is null
        dobtime = datetime.strptime(dob, "%Y-%m-%d") #convert to known format
        currentdate = datetime.now() #get time now
        age = currentdate.year - dobtime.year  # find the difference in years
        if currentdate.month < dobtime.month:  # if the birthday month has not been then we take off one from the age
            age -= 1
        elif currentdate.month == dobtime.month and currentdate.day < dobtime.day:  # if we are in the month, but the birth day day has not been we take away one from the age
            age -= 1


    except:
        return dob #if not in the right format or any error just return what was sent
    return age


@web_site.route('/account', methods=['GET', 'POST'])
def listmyposts():
    if "username" not in session: #checks if a user is actually logged in
        return redirect("/login") #if not, redirect them to the login page

    username = session["username"] #gets the username stored in the session
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT * FROM Posts WHERE user = ?" #gets all posts by the user
    cursor.execute(sql, (username,))
    con.commit()
    rows = cursor.fetchall()
    rows = rows[::-1] #reverses the order so they are shown in order of when they were posted

    sql = "SELECT description, dob,gender,pfp FROM Accounts WHERE username = ?"  #select details about the user
    cursor = con.cursor()
    cursor.execute(sql, (username,))

    row2 = cursor.fetchone()
    desc = row2[0] #[0] gets it out of tuple form
    dobget = row2[1]
    ageget = calcage(dobget)
    genderget = row2[2]
    pfp = row2[3]

    sql = """SELECT COUNT(*) as frequency
        FROM Posts
        WHERE user = ? AND album IS NULL
        GROUP BY user;
        """ #selects the number of posts the user has created
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    postcount = cursor.fetchone()
    if postcount is not None: #if they have created some posts
        postcount = postcount[0]
    else:
        postcount = 0 #if no posts found, set it to 0

    sql = """SELECT COUNT(*) as frequency
            FROM Posts
            WHERE user = ? AND album = 'True'
            GROUP BY user;
            """ #selects the number of albums the user has created
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    albumcount = cursor.fetchone()
    if albumcount is not None: #if they have created some albums
        albumcount = albumcount[0]
    else:
        albumcount = 0 #if no albums found, set it to 0

    sql = """SELECT COUNT(*) as frequency
            FROM friendrequests
            WHERE usersend = ? AND status = 2
            GROUP BY usersend;
            """ #selects the number of people they follow
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    followingcount = cursor.fetchone()
    if followingcount is not None: #if they follow at least one person
        followingcount = followingcount[0]
    else:
        followingcount = 0 #else set count to 0

    sql = """SELECT COUNT(*) as frequency
                FROM friendrequests
                WHERE userreceive = ? AND status = 2
                GROUP BY userreceive;
                """ #selects the number of people who follow them
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    followercount = cursor.fetchone()
    if followercount is not None: #if they are followed by at least one person
        followercount = followercount[0]
    else:
        followercount = 0 #else set count to 0

    return render_template("account.html", rows=rows, desc=desc, age=ageget, gender=genderget, pfp=pfp,
                           postcount=postcount, albumcount=albumcount, followercount=followercount,
                           followingcount=followingcount, username=username)


def convertorads(coord):
    radcoord = math.radians(coord)
    return radcoord


def CheckWithinRadius(dict):
    inside = []
    chosenlat = session.get('filterlat')  # gets the lat they chose
    chosenlng = session.get('filterlng')  # gets the lng the chose
    radius = session.get('radius')  # gets the radius they chose

    if radius == None:
        radius = 6371000
    if chosenlat == None or chosenlng == None:
        chosenlat = 52.000000
        chosenlng = -2.5000000
    for i in dict:
        postlat = float(dict[i][0])  # lat of each post
        postlng = float(dict[i][1])  # lng of each post

        postlng = convertorads(postlng)
        postlat = convertorads(postlat)  # convert to rads
        chosenlng2 = convertorads(chosenlng)
        chosenlat2 = convertorads(chosenlat)

        # haversine formula
        lngdifference = chosenlng2 - postlng  # finds difference
        latdifference = chosenlat2 - postlat
        a = sin(latdifference / 2) ** 2 + cos(postlat) * cos(chosenlat2) * sin(lngdifference / 2) ** 2  # special eq
        c = 2 * asin(sqrt(a))  # special eq
        r = 6371000  # radius of earth in m
        distance = c * r  # special eq

        if distance <= radius:  # if the distance is less than the radius, it must be inside it
            inside.append(i)  # so add it to the final list
    return inside


def recommendation(username):
    inside = []
    listofallpostids = []
    baseids = []
    listofallalbumids = []
    alluserpostids = []

    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = """
        SELECT id, lat, lng
        FROM Posts
        WHERE user = ?
    """
    cursor.execute(sql, (username,))
    lnglatlist = []
    for row in cursor.fetchall():
        lat = row['lat']
        lng = row['lng']
        baseids.append(row['id'])  # adds all the posts youve Created so we can remove later
        if lat is not None and lng is not None:
            lnglatlist.append([lat, lng])  # gets list of lists of longs and lats of each post you have posted

    # saved posts
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = """SELECT Posts.id, Posts.lat, Posts.lng
    FROM Posts
    JOIN savedposts ON Posts.id = savedposts.savedpostid
    WHERE savedposts.username = ?"""
    # gets every postid that the user has saved
    cursor.execute(sql, (username,))
    for row in cursor.fetchall():
        lat = row['lat']
        lng = row['lng']
        baseids.append(row['id'])
        if lat is not None and lng is not None:
            lnglatlist.append([lat, lng])
    # end of saved posts

    # liked posts
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = """SELECT Posts.id, Posts.lat, Posts.lng
    FROM Posts 
    JOIN Likes ON Posts.id = Likes.id
    WHERE Likes.usersliked = ?"""  # gets every postid that the user has liked
    cursor.execute(sql, (username,))
    for row in cursor.fetchall():
        lat = row['lat']
        lng = row['lng']
        baseids.append(row['id'])
        if lat is not None and lng is not None:
            lnglatlist.append([lat, lng])
    # liked posts end

    # location
    cursor = con.cursor()
    sql = "SELECT lat, lng FROM Accounts WHERE username = ?"  # go through every post and get lat lng of each
    cursor.execute(sql, (username,))
    lnglat4 = cursor.fetchone()
    if lnglat4 is not None:
        if lnglat4[0] is not None and lnglat4[1] is not None:
            lnglatlist.append([lnglat4[0], lnglat4[1]])
            geolocator = Nominatim(user_agent="web_site")
            latlng = str(lnglat4[0]) + ", " + str(lnglat4[1])
            location = geolocator.reverse(latlng,
                                          language='en')  # gets the named location of your location from account settings
            try:
                country = location.raw['address']['country']
            except:
                country = ""
            try:
                city = location.raw['address']['city']
            except:
                city = ""
            try:
                town = location.raw['address']['town']
            except:
                town = ""
        else:
            country = ""
            city = ""
            town = ""
    else:
        country = ""
        city = ""
        town = ""
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = """SELECT Posts.id
    FROM Posts
    WHERE (country = ? OR city = ? OR town = ?) AND user != ?"""  # gets every albumid (that is public)
    cursor.execute(sql, (country, city, town, username))
    for row in cursor.fetchall():
        inside.append(row[0])

    # end locaton

    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT id FROM Posts WHERE privacy = 'public' AND album = 'True'"  # gets every albumid (that is public)
    cursor.execute(sql)
    for row in cursor.fetchall():
        listofallalbumids.append(row[0])

    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT id FROM Posts WHERE privacy = 'public' AND album IS NULL"  # gets every postid (that is public)
    cursor.execute(sql)
    for row in cursor.fetchall():
        listofallpostids.append(row[0])

    # haversine formula to find posts close to ones we have positively interacted with
    allpostsdict = {}
    for i in listofallpostids:
        sql = "SELECT lat, lng FROM Posts WHERE id = ?"  # go through every post and get lat lng of each
        cursor.execute(sql, (i,))
        lnglat2 = cursor.fetchone()
        if lnglat2 is not None:
            if lnglat2[0] is not None and lnglat2[1] is not None:
                latlngtup2 = []
                latlngtup2.append(lnglat2[0])  # add it to a tuple so its in the format (51.2323, -2.121)
                latlngtup2.append(lnglat2[1])
                allpostsdict[i] = latlngtup2
    radius = 15000  # sets a radius of 15000 around each post
    for i in lnglatlist:
        postlat = float(i[0])  # lat of each post
        postlng = float(i[1])
        for x in allpostsdict:  # getting the lng lat of each post through a for loop
            complat = float(allpostsdict[x][0])
            complng = float(allpostsdict[x][1])

            postlng2 = convertorads(postlng)
            postlat2 = convertorads(postlat)  # convert to rads
            complng2 = convertorads(complng)
            complat2 = convertorads(complat)

            # haversine formula
            lngdifference = complng2 - postlng2  # finds difference
            latdifference = complat2 - postlat2
            a = sin(latdifference / 2) ** 2 + cos(postlat2) * cos(complat2) * sin(lngdifference / 2) ** 2  # special eq
            c = 2 * asin(sqrt(a))  # special eq
            r = 6371000  # radius of earth in m
            distance = c * r  # special eq
            if distance <= radius and x not in inside:  # if the distance is less than the radius, it must be inside it
                inside.append(x)  # so add it to a list
    # haversine end

    listofdisids = []
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = """SELECT Posts.id 
           FROM Posts 
           JOIN Dislikes ON Posts.id = Dislikes.id
           WHERE Dislikes.usersdisliked = ?"""  # removes any posts you have disliked (incase they are recommended for some reason)
    cursor.execute(sql, (username,))
    for row in cursor.fetchall():
        listofdisids.append(row[0])

    # inside is all the recommended posts
    # basids is all posts youve already seen
    # we obv want to remove ones youve already seen so we find them in "inside" and remove them

    # list of ids inside
    # pop
    allids = listofallpostids + listofallalbumids
    sortedpopids = sortpopularity(allids)
    sortedpopids = sortedpopids[:math.ceil(0.2 * len(sortedpopids))]  # gets top 20% most popular posts
    sucloop = 0
    totloop = 0
    while sucloop < 10 and totloop < 100:  # 10 times we select a random post from the top 20% of pop posts, (try 100 times to avoid infite loop)
        randnumber = random.randint(0, len(sortedpopids) - 1)
        if sortedpopids[randnumber] not in inside:
            inside.append(sortedpopids[randnumber])
            sucloop += 1
        else:
            totloop += 1
            pass
    # endpop

    # similar gender
    samegender = []
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = """SELECT Posts.id
            FROM Posts
            JOIN Accounts ON Posts.user = Accounts.username
            WHERE Accounts.gender = (SELECT gender FROM Accounts WHERE username = ?)
            AND Accounts.username != ?
            AND Posts.privacy = 'public'
            AND CAST(strftime('%Y', (Accounts.dob)) AS INTEGER) BETWEEN CAST(strftime('%Y',(SELECT dob FROM Accounts WHERE username = ?)) AS INTEGER) -3
            AND CAST(strftime('%Y',(SELECT dob FROM Accounts WHERE username = ?)) AS INTEGER) +3"""
    # finds accounts with similar age and gender
    cursor.execute(sql, (username, username, username, username))
    for row in cursor.fetchall():
        samegender.append(row[0])
    if len(samegender) < 5:
        inside += samegender
    else:
        for i in range(math.ceil(
                0.2 * len(samegender))):  # loops (20% of posts by users of same gender) times and gets random post
            randnumber = random.randint(0, len(samegender) - 1)
            if samegender[randnumber] not in inside:
                inside.append(samegender[randnumber])
    # gender stop

    # similar camera
    # get a list of all camera makes, and a list of all camera models
    makes = []
    models = []
    for i in alluserpostids:
        sql = "Select make FROM photodetails WHERE id = ?"
        cursor = con.cursor()
        cursor.execute(sql, (i,))
        getmake = cursor.fetchone()
        make = getmake[0]
        if make != "N/A":
            makes.append(make)

        sql = "Select model FROM photodetails WHERE id = ?"
        cursor = con.cursor()
        cursor.execute(sql, (i,))
        getmodel = cursor.fetchone()
        model = getmodel[0]
        if model != "N/A":
            models.append(model)

    for i in makes:
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        sql = """SELECT photodetails.id
        FROM photodetails
        JOIN Posts ON photodetails.id = Posts.id
        WHERE photodetails.make LIKE ?
        AND Posts.privacy = 'public'"""
        cursor.execute(sql, (i,))
        for row in cursor.fetchall():
            if row[0] not in alluserpostids:  # makes sure it isnt your post OBV hehe
                inside.append(row[0])
    for i in models:
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        sql = """SELECT photodetails.id
        FROM photodetails
        JOIN Posts ON photodetails.id = Posts.id
        WHERE photodetails.model LIKE ?
        AND Posts.privacy = 'public'"""
        cursor.execute(sql, (i,))
        for row in cursor.fetchall():
            if row[0] not in alluserpostids:
                inside.append(row[0])
    # similar camera stop

    # mutuals
    following = []
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT userreceive from friendrequests WHERE usersend = ? AND status = 2"  # getting the people you follow
    cursor.execute(sql, (username,))
    for row in cursor.fetchall():
        following.append(row[0])
    followingplus = []
    for i in following:
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        sql = """SELECT friendrequests.userreceive
        FROM friendrequests
        JOIN Accounts ON Accounts.username = friendrequests.userreceive
        WHERE friendrequests.usersend = ? 
        AND friendrequests.status = 2
        AND Accounts.username != ?
        AND Accounts.privacy = 'public'"""  # getting the people they then follow privacy = 'public'
        cursor.execute(sql, (i, username))
        for row in cursor.fetchall():
            followingplus.append(row[0])
    # we remove the ones you do follow, then sort by freq and add the top few
    intersect = []
    for i in following:
        if i in followingplus:
            intersect.append(i)
    for i in intersect:
        followingplus.remove(i)
    insidefreqmut = {}
    for i in followingplus:  # gets frequency of each post
        if i in insidefreqmut:
            insidefreqmut[i] += 1
        else:
            insidefreqmut[i] = 1
    intersectfreq = sortdatetime(
        insidefreqmut)  # able to use this func as not acc specifc to func, sorts it based on freq
    for i in intersectfreq:
        intersect.append(i[0])
    if len(intersect) > 5:
        intersect = intersect[:math.ceil(0.2 * len(intersect))]

    intersectposts = []
    for i in intersect:
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        sql = "SELECT id from posts WHERE user = ?"  # get a few of their posts
        cursor.execute(sql, (i,))
        for row in cursor.fetchall():
            intersectposts.append(row[0])
    if len(intersectposts) > 2:
        intersectposts = intersectposts[:math.ceil(0.2 * len(intersectposts))]

    if len(intersectposts) < 5:
        inside += intersectposts
    else:
        for i in range(math.ceil(
                0.2 * len(intersectposts))):  # loops (20% of posts by users of same gender) times and gets random post
            randnumber = random.randint(0, len(intersectposts) - 1)
            if intersectposts[randnumber] not in inside:
                inside.append(intersectposts[randnumber])

    # mutuals stop
    # people loc
    cursor = con.cursor()
    sql = "SELECT lat, lng FROM Accounts WHERE username = ?"  # go through every post and get lat lng of each
    cursor.execute(sql, (username,))
    lnglat4 = cursor.fetchone()
    if lnglat4 is not None:
        if lnglat4[0] is not None and lnglat4[1] is not None:
            latlngtup4 = []
            latlngtup4.append(lnglat4[0])  # add it to a tuple so its in the format (51.2323, -2.121)
            latlngtup4.append(lnglat4[1])
            lnglatlist.append(latlngtup4)
    # get your latlng ^
    allpostsdict = {}
    closeaccounts = []
    sql = "SELECT lat, lng, username FROM Accounts WHERE privacy = 'public'"  # go through every post and get lat lng of each
    cursor.execute(sql)
    for row in cursor.fetchall():
        if row[0] != None and row[1] != None:
            latlngtup2 = []
            latlngtup2.append(row[0])  # add it to a tuple so its in the format (51.2323, -2.121)
            latlngtup2.append(row[1])
            allpostsdict[row[2]] = latlngtup2
    radius = 15000  # sets a radius of 15000 around user
    for i in lnglatlist:
        postlat = float(i[0])  # lat of each post
        postlng = float(i[1])
        for x in allpostsdict:  # getting the lng lat of each post through a for loop
            complat = float(allpostsdict[x][0])
            complng = float(allpostsdict[x][1])

            postlng2 = convertorads(postlng)
            postlat2 = convertorads(postlat)  # convert to rads
            complng2 = convertorads(complng)
            complat2 = convertorads(complat)

            # haversine formula
            lngdifference = complng2 - postlng2  # finds difference
            latdifference = complat2 - postlat2
            a = sin(latdifference / 2) ** 2 + cos(postlat2) * cos(complat2) * sin(lngdifference / 2) ** 2  # special eq
            c = 2 * asin(sqrt(a))  # special eq
            r = 6371000  # radius of earth in m
            distance = c * r  # special eq
            if distance <= radius and x not in closeaccounts and x != username:  # if the distance is less than the radius, it must be inside it
                closeaccounts.append(x)  # so add it to a list
    closeaccountposts = []
    for i in closeaccounts:
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        sql = "SELECT id from posts WHERE user = ?"
        cursor.execute(sql, (i,))
        for row in cursor.fetchall():
            closeaccountposts.append(row[0])

    for i in range(math.ceil(
            0.2 * len(closeaccountposts))):  # loops (20% of posts by users of same gender) times and gets random post
        randnumber = random.randint(0, len(closeaccountposts) - 1)
        if closeaccountposts[randnumber] not in inside:
            inside.append(closeaccountposts[randnumber])
    # people loc end
    insidetemp = inside
    for i in insidetemp:
        sql = "SELECT albumid FROM albums WHERE postid = ?"  # go through every post and get lat lng of each
        cursor.execute(sql, (i,))
        albumids = cursor.fetchone()
        try:  # if it is not NULL
            inside.append(albumids[0])  # get any albums the good posts are in
        except:
            pass
    intersect = []
    for i in inside:
        if i in baseids:
            intersect.append(i)  # removes posts that shouldnt be shown (your own or already liked/saved)
    for i in intersect:
        inside.remove(i)

    insidefreq = {}
    for i in inside:  # gets frequency of each post
        if i in insidefreq:
            insidefreq[i] += 1
        else:
            insidefreq[i] = 1
    insidefreq = sortdatetime(insidefreq)  # able to use this func as not acc specifc to func, sorts it based on freq
    # #things which are in the list multiple times means they are more relevant
    inside = []

    for i in insidefreq:
        inside.append(i[0])  # adds all the post ids (removing the datetime)
    inside = inside[::-1]  # reverse to get the most relevant first (append adds to the end)
    listofall = listofallpostids + listofallalbumids
    if len(listofall) >= 1:  # deals with if no posts
        minnum = math.ceil(
            (len(listofall) * 0.2))  # gets the value that is 20% of all posts, this is how many we recommend (the min)
        totloop2 = 0
        while len(
                inside) < minnum and totloop2 < 100:  # if the number of recommendation posts is < 20% of allposts (the min) then we add some random ones to fill it (#totloop < 100 to avoid infinte loop)
            for i in range(minnum - len(inside)):
                randnumber = random.randint(0, len(listofall) - 1)
                if listofall[randnumber] not in inside and listofall[
                    randnumber] not in baseids:  # make sure we dont dupe the random ones/add your ones
                    inside.append(listofall[randnumber])
            for i in inside:
                if i in listofdisids:  # removes disliked post
                    inside.remove(i)
            totloop2 += 1
    else:
        inside = []

    return inside  # a list of all post ids that are recommended, in order of how relevant they are


@web_site.errorhandler(404)
def error404(error):
    return render_template('404.html'), 404


@web_site.route('/recommended', methods=['GET', 'POST'])
def recommended():
    if "username" not in session:
        return redirect("/login")

    msg = ""
    username = session["username"]
    postids = recommendation(username)
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    postinfo = []
    for postid2 in postids:
        sql = """SELECT Posts.*, Accounts.pfp
        FROM Posts
        JOIN Accounts ON Accounts.username = Posts.user
        WHERE Posts.id = ?"""  # get the info about each post in the list
        cursor.execute(sql, (postid2,))
        postresult = cursor.fetchone()
        if postresult:
            postinfo.append(postresult)  # add to a list of all posts

    if postinfo == []:
        msg = "This does not exist"
    return render_template("recommended.html", rows=postinfo, username=username, msg=msg)


def sortdatetimefunc(listofpostids):
    datetimedict = {}
    unsortedpostids = []
    sorteddatetime = {}
    for i in listofpostids:
        con = sqlite3.connect('database.db')
        cursor = con.cursor()
        sql = "SELECT timeposted FROM Posts WHERE id = ?"  # go through every post and get datetime of each
        cursor.execute(sql, (i,))
        getdatetime = cursor.fetchone()
        if getdatetime is not None:
            if getdatetime[0] != "N/A":
                getdatetime = datetime.strptime(getdatetime[0], "%d/%m/%y %H:%M")
                formatdattimetotal = formatdattime(getdatetime)  # gets how many seconds ago it was taken
                datetimedict[
                    i] = formatdattimetotal  # adds the seconds value to a dictionary with the key being the post id (i)
                sorteddatetime = sortdatetime(datetimedict)  # sorts it
            else:
                unsortedpostids.append(i)  # adds posts with no date and time to a seperate list
        else:
            unsortedpostids.append(i)
    sortedpostids2 = []
    for i in sorteddatetime:
        sortedpostids2.append(i[0])  # adds all the post ids (removing the datetime)
    sortedpostids2 += unsortedpostids
    return sortedpostids2


def sortpopularity(listofpostids):
    likesdict = {}
    sortlikes = {}
    for i in listofpostids:
        con = sqlite3.connect('database.db')
        cursor = con.cursor()
        sql = "SELECT likes FROM Posts WHERE id = ?"
        cursor.execute(sql, (i,))
        getlikes = cursor.fetchone()
        likesdict[i] = getlikes[0]  # adds the seconds value to a dictionary with the key being the post id (i)
        sortlikes = sortdatetime(likesdict)  # sorts it (able to use other func as not actually specific to datetime)
        # only sort likes as if you have many likes and many dislikes, its got lots of interaction so must be popular

    sortedpostids2 = []
    for i in sortlikes:
        sortedpostids2.append(i[0])  # adds all the post ids (removing the datetime)
    return sortedpostids2[::-1]


@web_site.route('/allposts', methods=['GET', 'POST'])
def listallposts():
    if "username" not in session:
        return redirect("/login")

    msg = ""
    username = session["username"]
    listofpostids = []
    getallalbumids = []
    filtered = False
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT id FROM Posts WHERE privacy = 'public'"  # gets every postid
    cursor.execute(sql)
    for row in cursor.fetchall():
        listofpostids.append(row[0])
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT id FROM Posts WHERE album = 'True'"  # gets every postid
    cursor.execute(sql)
    for row in cursor.fetchall():
        getallalbumids.append(row[0])

    lnglatdict = {}
    for i in listofpostids:
        sql = "SELECT lat, lng FROM Posts WHERE id = ?"  # go through every post and get lat lng of each
        cursor.execute(sql, (i,))
        lnglat = cursor.fetchone()
        if lnglat is not None:
            if lnglat[0] is not None and lnglat[1] is not None:
                latlngtup = []
                latlngtup.append(lnglat[0])  # add it to a tuple so its in the format (51.2323, -2.121)
                latlngtup.append(lnglat[1])
                lnglatdict[i] = latlngtup  # add this tuple to a dictionary with the key as the post id

    if "sortedpostids" in session:
        if session['sortedpostids'] == []:  # if filtered post is emptied than no filter is active so use all posts
            sortedpostids = sortdatetimefunc(listofpostids)  # filtered set to false as default so no need to set again

        else:
            sortedpostids = session['sortedpostids']  # if there is a filter active then set filtered to true
            filtered = True

    else:
        sortedpostids = sortdatetimefunc(listofpostids)  # else if it is there first time loggin on then use all posts
        session['sortedpostids'] = []

    if request.method == "POST":
        selected_option = request.form['selected_option']
        checkboxposts = request.form.get('posts')
        checkboxalbums = request.form.get('albums')
        if "unfilter" in request.form:
            session['sortedpostids'] = []  # so when the page is reloaded, it tells the bit above that no filter is set
            return redirect(url_for('listallposts'))

        if "filter" in request.form:
            filtered = True
            slidervalue = int(request.form['slidervalue'])
            insideposts = CheckWithinRadius(lnglatdict)

            for i in getallalbumids:  # makes sure we incl albums (if a post is inside the circle and in an album, give the album too)
                updatealbumlocation(i)
                allpostsdict = {}
                con = sqlite3.connect('database.db')
                con.row_factory = sqlite3.Row
                cursor = con.cursor()
                sql = """SELECT albums.postid, Posts.lat, Posts.lng
                        FROM albums
                        JOIN Posts ON albums.postid = Posts.id
                        WHERE albums.albumid = ?"""
                cursor.execute(sql, (i,))
                for row in cursor.fetchall():
                    lat = row['lat']
                    lng = row['lng']
                    if lat is not None and lng is not None:
                        lnglatlist = []
                        lnglatlist.append(lat, )
                        lnglatlist.append(lng)
                        allpostsdict[i] = lnglatlist
                postalbuminside = CheckWithinRadius(allpostsdict)
                if postalbuminside != []:
                    insideposts.append(i)

            if checkboxposts != None or checkboxalbums != None:  # if at least one is clicked (slider could be)
                sortedpostids2 = []
                if checkboxalbums != None and checkboxposts == None:  # if only albums is clicked (slider could be)
                    con = sqlite3.connect('database.db')
                    con.row_factory = sqlite3.Row
                    cursor = con.cursor()
                    sql = "SELECT id FROM Posts WHERE album = 'True' AND privacy = 'public'"
                    cursor.execute(sql)
                    con.commit()
                    rows = cursor.fetchall()
                    sortedpostids = []
                    for row in rows:
                        sortedpostids.append(row[0])
                    sortedpostids = sortdatetimefunc(sortedpostids)
                    session['sortedpostids'] = sortedpostids


                elif checkboxposts != None and checkboxalbums == None:  # if only posts is clicked (slider could be)
                    con = sqlite3.connect('database.db')
                    con.row_factory = sqlite3.Row
                    cursor = con.cursor()
                    sql = "SELECT id FROM Posts WHERE album IS NULL AND privacy = 'public'"
                    cursor.execute(sql)
                    con.commit()
                    rows = cursor.fetchall()
                    sortedpostids = []
                    for row in rows:
                        sortedpostids.append(row[0])
                    sortedpostids = sortdatetimefunc(sortedpostids)
                    session['sortedpostids'] = sortedpostids
                if slidervalue > 0:
                    for i in sortedpostids:
                        if i in insideposts:
                            sortedpostids2.append(i)
                    sortedpostids = sortedpostids2
                    session['sortedpostids'] = sortedpostids

            elif checkboxposts == None and checkboxalbums == None:  # if neither are clicked (slider could be)
                sortedpostids = insideposts
                session['sortedpostids'] = sortedpostids
                sortedpostids = sortdatetimefunc(sortedpostids)
            elif checkboxposts != None and checkboxalbums != None:  # if both are clicked (slider could be)
                sortedpostids = insideposts
                session['sortedpostids'] = sortedpostids
                sortedpostids = sortdatetimefunc(sortedpostids)
            if checkboxposts == None and checkboxalbums == None and slidervalue == 0:  # absolutely nothing selected
                session['sortedpostids'] = []
                return redirect(url_for('listallposts'))
        if "sort" in request.form:
            if session['sortedpostids'] != []:
                sortedpostids = session['sortedpostids']
            if selected_option == "Newest":
                sortedpostids = sortdatetimefunc(sortedpostids)
                sortedpostids = sortedpostids  # sorted posts
            elif selected_option == "Oldest":
                sortedpostids = sortdatetimefunc(sortedpostids)
                sortedpostids = sortedpostids[::-1]
            elif selected_option == "Popularity":
                sortedpostids = sortpopularity(sortedpostids)

    postinfo = []
    for postid2 in sortedpostids:
        sql = """SELECT Posts.*, Accounts.pfp
                     FROM Posts
                     JOIN Accounts ON Accounts.username = Posts.user
                     WHERE Posts.id = ?"""  # get the info about each post in the list
        cursor.execute(sql, (postid2,))
        postresult = cursor.fetchone()
        if postresult:
            postinfo.append(postresult)  # add to a list of all posts
    latlnglist = []
    for i in listofpostids:
        sql = "SELECT lat, lng, album FROM Posts WHERE id = ?"  # go through every post and get lat lng of each
        cursor.execute(sql, (i,))
        lnglat = cursor.fetchone()
        if lnglat is not None:
            if lnglat[0] is not None and lnglat[1] is not None:
                latlng = []
                latlng.append(lnglat[0])  # add it to a tuple so its in the format (51.2323, -2.121)
                latlng.append(lnglat[1])
                latlng.append(i)
                if lnglat[2] == "True":
                    latlng.append("True")
                else:
                    latlng.append("False")
                latlnglist.append(latlng)
    if not postinfo:
        msg = "No results found. It's Hard to Explain..."

    return render_template("allposts.html", rows=postinfo, username=username, filtered=filtered, latlnglist=latlnglist,
                           msg=msg)


@web_site.route('/friends', methods=['GET', 'POST'])
def friends():
    if "username" not in session:
        return redirect("/login")

    msg = ""
    username = session["username"]
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cursor = con.cursor()

    sql = """
    SELECT 
    Posts.*, Accounts.pfp
    FROM Posts
    JOIN Accounts ON Accounts.username = Posts.user
    LEFT JOIN friendrequests ON Posts.user = friendrequests.userreceive
    WHERE friendrequests.usersend = ? AND friendrequests.status = 2"""
    cursor.execute(sql, (username,))
    con.commit()
    rows = cursor.fetchall()

    if rows == []:
        msg = "No posts found"
    return render_template("friends.html", rows=rows, msg=msg)


@web_site.route('/account_settings', methods=['GET', 'POST'])
def account_settings():
    if "username" not in session: #checks that a user is actually logged in
        return redirect("/login") #if not, redirect to login page

    filename = "1024px-Cross_red_circle.svg.png" #defaults to red cross
    username = session["username"] #gets the user that is logged in

    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    sql = "SELECT * FROM Accounts WHERE username = ?" #selects all info about user
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    con.commit()
    rows = cursor.fetchall()

    sql = "SELECT privacy FROM Accounts WHERE username = ?" #selects the privacy seperately
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    getprivacy = cursor.fetchone()
    getprivacy = getprivacy[0]

    genders = ["None", "Male", "Female", "Other"] #options for genders

    if request.method == "POST":
        lat = session.get('lat') #get the lat and lng clicked (marker on the map)
        lng = session.get('lng')
        clicked = session.get('clicked') #checks if the user has interacted with the map
        if "cancel" in request.form: #if the user wants to discard any changes
            session['lat'] = 0 #sets default lng lat to 0, 0
            session['lng'] = 0
            return redirect('account') #redirects back to account

        description = request.form["description"] #gets inputted description
        description = moderate(description) #moderates description
        dob = request.form["dob"] #gets inputted date of birth
        username_update = request.form["Username"] #gets inputted username (to update to)
        checkbox_privacy = request.form.get('privacy') #gets inputted privacy choice
        checkbox_resetpfp = request.form.get('resetpfp') #gets if they want to reset their profile picture
        gender = request.form['gender'] #gets gender choice
        oldpassword = request.form["oldpassword"] #gets inputted old password
        newpassword = request.form["newpassword"] #gets the password they want to make their new password
        con = sqlite3.connect('database.db')
        sql = "SELECT username FROM Accounts WHERE username = ?" # gets old username
        cursor = con.cursor()
        cursor.execute(sql, (username_update,))
        getusername = cursor.fetchone()
        sql = "UPDATE Accounts SET description = ? WHERE username = ?"  # updates account description, no checks needed
        cursor = con.cursor()
        cursor.execute(sql, (description, username))
        con.commit()

        sql = "UPDATE Accounts SET dob = ? WHERE username = ?" # updates account dob, no checks needed
        cursor = con.cursor()
        cursor.execute(sql, (dob, username))
        con.commit()

        sql = "UPDATE Accounts SET gender = ? WHERE username = ?" # updates account gender, no checks needed
        cursor = con.cursor()
        cursor.execute(sql, (gender, username))
        con.commit()

        if lat != 0 and lng != 0 and clicked: #ensures the user has actually clicked on the map, and not from a previous session
            sql = "UPDATE Accounts SET lat = ?, lng = ? WHERE username = ?" #updates account lng and lat
            cursor = con.cursor()
            cursor.execute(sql, (lat, lng, username,))
            con.commit()

        randfilename = randomfilename(os.path.join(web_site.root_path, 'static', 'ProfilePictures')) #gets a random filename, passing the path in
        photo = request.files['photo'] #gets photo they chose for their filename
        if photo.filename != "": #if photo filename is not blank
            filename = randfilename + "_" + photo.filename.replace(" ", "") #removes any spaces from the filename and adds it to the random filename generated before
            try:
                photo.save(os.path.join(web_site.root_path, 'static', 'ProfilePictures', filename)) #saves the filename
                photo_path = os.path.join(web_site.root_path, 'static', 'ProfilePictures', filename) #gets the path of the saved filename
                metadata = get_metadata(photo_path)  #tests for correct filetype

                con = sqlite3.connect('database.db')
                sql = "SELECT pfp FROM Accounts WHERE username = ?" #gets old filename
                cursor = con.cursor()
                cursor.execute(sql, (username,))
                getoldfilename = cursor.fetchone()
                getoldfilename = getoldfilename[0] #gets it out of tuple form
                if getoldfilename != "blank-profile-picture-973460_960_720.jpg": #if old filename isnt the default one
                    os.remove(os.path.join(web_site.root_path, 'static', 'ProfilePictures',
                                           getoldfilename))  # deletes the old filename

                sql = "UPDATE Accounts SET pfp = ? WHERE username = ?" #upadates the database with new filename
                cursor = con.cursor()
                cursor.execute(sql, (filename, username))
                con.commit()



            except:
                os.remove(os.path.join(web_site.root_path, 'static', 'ProfilePictures', filename)) #if not the correct filetype, delete the file

        if username_update != username: #if the new username isnt their old one
            if getusername is None:  # checks if the username is unique
                if username_update != "": #checks new username isnt blank
                    if " " not in username_update and len(username_update) >= 3 and len(username_update) <= 15: #checks username between 3 and 15 chars
                        con = sqlite3.connect('database.db')
                        sql = "UPDATE Accounts SET username = ? WHERE username = ?"  # updates accounts
                        cursor = con.cursor()
                        cursor.execute(sql, (username_update, username))
                        con.commit()
                        session["username"] = username_update #updates session

                        #need to update all tables with new username
                        sql = "UPDATE Posts SET user = ? WHERE user = ?"
                        cursor = con.cursor()
                        cursor.execute(sql, (username_update, username))
                        con.commit()

                        sql = "UPDATE Likes SET usersliked = ? WHERE usersliked = ?"
                        cursor = con.cursor()
                        cursor.execute(sql, (username_update, username))
                        con.commit()

                        sql = "UPDATE Dislikes SET usersdisliked = ? WHERE usersdisliked = ?"
                        cursor = con.cursor()
                        cursor.execute(sql, (username_update, username))
                        con.commit()

                        sql = "UPDATE Albums SET user = ? WHERE user = ?"
                        cursor = con.cursor()
                        cursor.execute(sql, (username_update, username))
                        con.commit()

                        sql = "UPDATE friendrequests SET userreceive = ? WHERE userreceive = ?"
                        cursor = con.cursor()
                        cursor.execute(sql, (username_update, username))
                        con.commit()

                        sql = "UPDATE friendrequests SET usersend = ? WHERE usersend = ?"
                        cursor = con.cursor()
                        cursor.execute(sql, (username_update, username))
                        con.commit()

                        sql = "UPDATE savedposts SET username = ? WHERE username = ?"
                        cursor = con.cursor()
                        cursor.execute(sql, (username_update, username))
                        con.commit()

                        sql = "UPDATE tempphotos SET user = ? WHERE user = ?"
                        cursor = con.cursor()
                        cursor.execute(sql, (username_update, username))
                        con.commit()
                        username = username_update
        if checkbox_privacy == "on": #if they chose their account to be private
            con = sqlite3.connect('database.db')
            sql = "UPDATE Accounts SET privacy = 'private' WHERE username = ?" #update accounts, set to private
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = "UPDATE Posts SET privacy = 'private' WHERE user = ?" #update posts so that posts are also private
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()
        if checkbox_privacy is None: #if they chose their account to be public
            con = sqlite3.connect('database.db')
            sql = "UPDATE Accounts SET privacy = 'public' WHERE username = ?" #update account setting to public
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = "UPDATE Posts SET privacy = 'public' WHERE user = ?" #update posts setting to public
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()
        if checkbox_resetpfp == "on": #if they want to reset the profile picture back to default

            con = sqlite3.connect('database.db')
            sql = "SELECT pfp FROM Accounts WHERE username = ?"  # gets old filename
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            getoldfilename = cursor.fetchone()
            getoldfilename = getoldfilename[0]  # gets it out of tuple form
            if getoldfilename != "blank-profile-picture-973460_960_720.jpg":  # if old filename isnt the default one
                os.remove(os.path.join(web_site.root_path, 'static', 'ProfilePictures',
                                       getoldfilename))  # deletes the old filename


            con = sqlite3.connect('database.db')
            sql = "UPDATE Accounts SET pfp = ? WHERE username = ?" #updates account with new filename
            cursor = con.cursor()
            cursor.execute(sql, ("blank-profile-picture-973460_960_720.jpg", username)) #filename set to the default profile picture
            con.commit()

        con = sqlite3.connect('database.db')
        sql = "SELECT password FROM Accounts WHERE username = ?" #get old (hashed) password
        cursor = con.cursor()
        cursor.execute(sql, (username,))
        getpassword = cursor.fetchone()
        getpassword = getpassword[0] # gets it out of tuple form
        critera = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!?*%@$&]).{8,}$") #sets criteria

        if bool(critera.match(newpassword)):  # fits critera add ticks if they match
            newpassword = hash(newpassword) #hashes the new password
            oldpassword = hash(oldpassword) #hashes what they think is their old password
            if oldpassword != "" and getpassword != "": #if both fields are not blank
                if oldpassword == getpassword: #if old password equals their actual password (both hashed)
                    con = sqlite3.connect('database.db')
                    sql = "UPDATE Accounts SET password = ? WHERE username = ?" #update their password
                    cursor = con.cursor()
                    cursor.execute(sql, (newpassword, username))
                    con.commit()
        session['lat'] = 0 #set lng and lat back to 0
        session['lng'] = 0
        return redirect("account")

    return render_template("account_settings.html", rows=rows, getprivacy=getprivacy, filename=filename,
                           genders=genders)


@web_site.route('/logout')
def logout():
    try: #try to get the user that is logged in and remove that username from session
        username = session["username"]
        session.pop('username', None)
    except:
        return redirect("/login") #if the user's username isn't in the session, they are already logged out so redirect to login page
    return render_template("logout.html", username=username)


@web_site.route('/viewpost', methods=['GET', 'POST'])
def viewpost():
    if "username" not in session: #if no user is logged in
        return redirect("/login") #redirect to login page
    liked = False #set liked status to false
    disliked = False #set disliked status to false
    username = session["username"] #get the user that is logged in
    postid = request.args.get('id') #get the id of the post
    thumbs = bool(request.args.get('ld')) #ld = like/dislike and get if state is True or False (auto scroll)
    scrollsaved = bool(request.args.get('s')) #s = save and get if state is True or False (auto scroll)
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    sql = "SELECT privacy,user FROM Posts WHERE id = ?" #get the privacy of, and the user who posted the post
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    postinfo = cursor.fetchall()
    if not postinfo: #if a post doesnt exist, e.g. a user manually typed in a post id that doesnt exist
        return render_template('404.html') #give error page
    getprivacy = postinfo[0]['privacy']
    getuser = postinfo[0]['user']

    sql = "SELECT status FROM friendrequests WHERE usersend = ? AND userreceive = ? " #get the relationship between the user viewing and the user who posted
    cursor = con.cursor()
    cursor.execute(sql, (username, getuser,))
    getstatus = cursor.fetchone()
    if getstatus is None: #if no relationship, then status is 0
        getstatus = "0"
    getstatus = getstatus[0] # get out of tuple form
    if getprivacy == "private" and getstatus != 2 and getuser != username: #if the user is private and the user doesnt follow them then redirect, (ignore if its your post)
        return redirect(url_for('viewaccount', id=getuser)) #redirect to view account, as not allowed to view post so must send a friend request first

    sql = "SELECT user FROM Posts WHERE id = ?" #get the user who posted (clean)
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    getpostuser = cursor.fetchone()
    getpostuser = getpostuser[0]

    con.row_factory = sqlite3.Row
    sql = "SELECT * FROM Posts WHERE id = ?" #get all info about the post
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    rows = cursor.fetchall()
    albumtitles = []
    try: #try to get all the albums it is in
        con = sqlite3.connect('database.db')  # get the album id if its in one
        con.row_factory = sqlite3.Row
        sql = """SELECT Posts.text, Posts.id
                FROM Posts
                JOIN albums ON Posts.id = albums.albumid
                WHERE albums.postid = ?"""
        cursor = con.cursor()
        cursor.execute(sql, (postid,))
        allalbums = cursor.fetchall()
        for album in allalbums: #create a list so that each item in the list is a dictionary relating to an album that stores the title and the id of the album
            dict = {}
            dict["title"] = album[0]
            dict["id"] = album[1]
            albumtitles.append(dict)
    except: #if in none, set to an empty string
        albumtitles = ""
        pass

    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    sql = "SELECT * FROM photodetails WHERE id = ?" #get all photo details about the post
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    rows2 = cursor.fetchall()

    sql = "Select datetime FROM photodetails WHERE id = ?" #get the datetime
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    datetimeup = cursor.fetchone()
    datetimeup = datetimeup[0]
    date = datetimeup[:10] #split into date and into time
    time = datetimeup[11:]

    con = sqlite3.connect('database.db')
    sql = "SELECT usersliked FROM Likes WHERE usersliked = ? AND id = ?" #if the user viewing has liked the post
    cursor = con.cursor()
    cursor.execute(sql, (username, postid))
    getusersliked = cursor.fetchone()
    if getusersliked != None: #set the like status to true
        liked = True

    sql = "SELECT usersdisliked FROM Dislikes WHERE usersdisliked = ? AND id = ?" #if the user viewing has liked the post
    cursor = con.cursor()
    cursor.execute(sql, (username, postid))
    getusersdisliked = cursor.fetchone()
    if getusersdisliked != None: #set dislike status to true
        disliked = True


    con.row_factory = sqlite3.Row
    cursor3 = con.cursor()
    sql3 = "SELECT * FROM Posts WHERE album = 'True' AND user = ?" #get all of albums created by the user who posted the post
    cursor3.execute(sql3, (username,))
    rows3 = cursor3.fetchall()

    sql = "SELECT savedpostid FROM savedposts WHERE savedpostid = ? and username = ?" #get if the viewing user has already saved the post
    cursor = con.cursor()
    cursor.execute(sql, (postid, username))
    getsavedid = cursor.fetchone()
    if getsavedid is not None: #if they have saved, set checksaved to true
        checksaved = True
    else:
        checksaved = False #if nothing in database, set checksaved to false

    con = sqlite3.connect('database.db')
    sql = "SELECT * FROM Accounts WHERE username = (SELECT user FROM Posts WHERE id = ?)" #get all info from the accounts page about the user who posted it
    cursor = con.cursor()
    con.row_factory = sqlite3.Row
    cursor.execute(sql, (postid,))
    userrows = cursor.fetchall()

    if request.method == "POST":
        if "add" in request.form: #if its your post, and they choose to add it to an album
            selected_option = request.form['selected_option'] #get the album title they added it to
            if selected_option != "none": #if they chose an album
                con = sqlite3.connect('database.db')
                sql = "SELECT id FROM Posts WHERE text = ? AND user = ? AND album = 'True'" #get the album id from the album name and the username (album names are unique for each user)
                cursor = con.cursor()
                cursor.execute(sql, (selected_option, username,))
                con.commit()
                getalbumid = cursor.fetchone()
                getalbumid = getalbumid[0]

                sql = "SELECT albumid FROM albums WHERE postid = ?" #select if the post has already been added to an album
                cursor = con.cursor()
                con.row_factory = sqlite3.Row
                cursor.execute(sql, (postid,))
                con.commit()
                postinalbumid = cursor.fetchall()
                listofpostalbumids = []
                if postinalbumid != None:  # if the post is already in other albums
                    for i in postinalbumid:
                        listofpostalbumids.append(i[0])  # get all the album ids that the post is in
                if getalbumid not in listofpostalbumids or postinalbumid == None:  # if the post isnt already in the selected album, or if the post isnt in any albums then add it
                    con = sqlite3.connect('database.db')
                    sql = "INSERT INTO albums(albumid, postid, user) VALUES(?,?,?)" #add to the selected album
                    cursor = con.cursor()
                    cursor.execute(sql, (getalbumid, postid, username,))
                    con.commit()
                    updatealbumlocation(getalbumid)
                    return redirect(url_for('viewpost', id=postid)) #refresh the page to show the "view album" button

        #like and dislike START
        con = sqlite3.connect('database.db')
        sql = "SELECT usersliked FROM Likes WHERE usersliked = ? AND id = ?" #get if the viewing user has already liked it
        cursor = con.cursor()
        cursor.execute(sql, (username, postid))
        getusersliked = cursor.fetchone()

        sql = "SELECT usersdisliked FROM Dislikes WHERE usersdisliked = ? AND id = ?" #get if the viewing user has already disliked it
        cursor = con.cursor()
        cursor.execute(sql, (username, postid))
        getusersdisliked = cursor.fetchone()

        # find it
        sql = "SELECT likes FROM Posts WHERE id = ?" #select the like count
        cursor = con.cursor()
        cursor.execute(sql, (postid,))
        getlikecount = cursor.fetchone()
        likecount = int(getlikecount[0])

        sql = "SELECT dislikes FROM Posts WHERE id = ?" #select the dislike count
        cursor = con.cursor()
        cursor.execute(sql, (postid,))
        getdislikecount = cursor.fetchone()
        dislikecount = int(getdislikecount[0])

        if "Like" in request.form: #if they clicked like
            datetimenow = datetime.now() #get the time when they liked it
            formattedtime = datetimenow.strftime("%d/%m/%y %H:%M:%S")
            if getusersliked is None: #if they havnt already liked it before
                if getusersdisliked is None: #if they havnt aleady disliked it before
                    #no interaction state
                    likecount += 1 #increment like count by 1
                    # update it
                    sql = "UPDATE Posts SET likes = ? WHERE id = ?" #update the like count
                    cursor = con.cursor()
                    cursor.execute(sql, (likecount, postid,))
                    con.commit()

                    con = sqlite3.connect('database.db')
                    sql = "INSERT INTO Likes(usersliked, id,timesent) VALUES(?,?,?)" #insert username, post id and time into Likes table
                    cursor = con.cursor()
                    cursor.execute(sql, (username, postid, formattedtime))
                    con.commit()
                    return redirect(url_for('viewpost', id=postid, ld=True)) #refresh and set ld to True so not taken to the top of the page
                elif getusersdisliked is not None: #if they have already disliked it
                    dislikecount -= 1 #decrement dislikecount by one
                    likecount += 1 #increment likecount by one
                    con = sqlite3.connect('database.db')
                    sql = "UPDATE Posts SET likes = ? WHERE id = ?" #update like count
                    cursor = con.cursor()
                    cursor.execute(sql, (likecount, postid,))
                    con.commit()

                    sql = "UPDATE Posts SET dislikes = ? WHERE id = ?" #update disliked count
                    cursor = con.cursor()
                    cursor.execute(sql, (dislikecount, postid,))
                    con.commit()

                    sql = "DELETE FROM Dislikes WHERE usersdisliked = ? and id = ?" #remove from dislikes table
                    cursor = con.cursor()
                    cursor.execute(sql, (username, postid))
                    con.commit()

                    sql = "INSERT INTO Likes(usersliked, id,timesent) VALUES(?,?,?)" #add to likes table
                    cursor = con.cursor()
                    cursor.execute(sql, (username, postid, formattedtime))
                    con.commit()
                    return redirect(url_for('viewpost', id=postid, ld=True))

            elif getusersliked is not None: #if they have already liked it and they click it
                likecount -= 1 #decrement by one
                con = sqlite3.connect('database.db')
                sql = "UPDATE Posts SET likes = ? WHERE id = ?" #update like count
                cursor = con.cursor()
                cursor.execute(sql, (likecount, postid,))
                con.commit()
                sql = "DELETE FROM Likes WHERE usersliked = ? and id = ?" #delete from like table
                cursor = con.cursor()
                cursor.execute(sql, (username, postid))
                con.commit()
                return redirect(url_for('viewpost', id=postid, ld=True))

        elif "Dislike" in request.form: #if they clicked dislike
            if getusersliked is None: #if they havnt liked it yet
                if getusersdisliked is None: #if they havnt disliked it yet
                    #no interaction yet
                    dislikecount += 1 #increment dislike count by one
                    # update it
                    sql = "UPDATE Posts SET dislikes = ? WHERE id = ?" #update dislike count
                    cursor = con.cursor()
                    cursor.execute(sql, (dislikecount, postid,))
                    con.commit()

                    con = sqlite3.connect('database.db')
                    sql = "INSERT INTO Dislikes(usersdisliked, id) VALUES(?,?)" #add to dislike table, username, postid (time not needed as too toxic to tell people when their post has been disliked)
                    cursor = con.cursor()
                    cursor.execute(sql, (username, postid))
                    con.commit()
                    return redirect(url_for('viewpost', id=postid, ld=True)) #redirect and set ld to true so the user isnt taken to the top of the site
                elif getusersdisliked is not None: #if they have disliked it before
                    dislikecount -= 1 #decrement dislikecount by one
                    con = sqlite3.connect('database.db')
                    sql = "UPDATE Posts SET dislikes = ? WHERE id = ?" #update the dislike count
                    cursor = con.cursor()
                    cursor.execute(sql, (dislikecount, postid,))
                    con.commit()

                    sql = "DELETE FROM Dislikes WHERE usersdisliked = ? and id = ?" #delete from dislike table
                    cursor = con.cursor()
                    cursor.execute(sql, (username, postid))
                    con.commit()
                    return redirect(url_for('viewpost', id=postid, ld=True)) #redirect
            elif getusersliked is not None: #if they have liked it before
                dislikecount += 1 #increase dislikecount by one
                likecount -= 1 #decrease like count by one
                con = sqlite3.connect('database.db')
                sql = "UPDATE Posts SET likes = ? WHERE id = ?" #update the like count
                cursor = con.cursor()
                cursor.execute(sql, (likecount, postid,))
                con.commit()

                sql = "UPDATE Posts SET dislikes = ? WHERE id = ?" #update the dislike count
                cursor = con.cursor()
                cursor.execute(sql, (dislikecount, postid,))
                con.commit()

                sql = "DELETE FROM Likes WHERE usersliked = ? and id = ?" #delete from likes table
                cursor = con.cursor()
                cursor.execute(sql, (username, postid))
                con.commit()

                sql = "INSERT INTO Dislikes(usersdisliked, id) VALUES(?,?)" #add to dislikes table
                cursor = con.cursor()
                cursor.execute(sql, (username, postid))
                con.commit()
                return redirect(url_for('viewpost', id=postid, ld=True))
        # like and dislike END
        if "save" in request.form: #if they click "save"
            if checksaved == False: #if they havnt saved it aready
                con = sqlite3.connect('database.db')
                sql = "INSERT INTO savedposts(savedpostid, username) VALUES(?, ?)" #add to savedpost table
                cursor = con.cursor()
                cursor.execute(sql, (postid, username))
                con.commit()
                return redirect(url_for('viewpost', id=postid, s=True)) #redirect and set s to true so user not taken to top of page
        elif "unsave" in request.form: #if they click unsave
            con = sqlite3.connect('database.db')
            sql = "DELETE FROM savedposts WHERE savedpostid = ? AND username = ?" #delete from savedpost table
            cursor = con.cursor()
            cursor.execute(sql, (postid, username))
            con.commit()
            return redirect(url_for('viewpost', id=postid, s=True))

    return render_template("viewpost.html", userrows=userrows, rows=rows, getpostuser=getpostuser, username=username,
                           checksaved=checksaved, rows2=rows2, rows3=rows3, albumtitles=albumtitles, date=date,
                           time=time, disliked =disliked, liked=liked, thumbs=thumbs, scrollsaved=scrollsaved)


@web_site.route('/viewaccount', methods=['GET', 'POST'])
def viewaccount():
    if "username" not in session:
        return redirect("/login")

    username = request.args.get('id')
    usernamesend = session["username"]
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = """SELECT Posts.*, Accounts.pfp
                         FROM Posts
                         JOIN Accounts ON Accounts.username = Posts.user
                         WHERE Posts.user = ?"""
    cursor.execute(sql, (username,))
    con.commit()
    rows = cursor.fetchall()
    rows = rows[::-1]

    if username == usernamesend:
        return redirect(url_for('listmyposts'))

    sql = "SELECT description, dob,gender,pfp FROM Accounts WHERE username = ?"
    cursor = con.cursor()
    cursor.execute(sql, (username,))

    row2 = cursor.fetchone()
    try:
        desc = row2[0]  # if this causes an error it means the user doesnt exist
        dobget = row2[1]
        ageget = calcage(dobget)
        gender = row2[2]
        pfp = row2[3]
    except:
        return render_template('404.html')

    sql = """SELECT COUNT(*) as frequency
    FROM Posts
    WHERE user = ? AND album IS NULL
    GROUP BY user;
    """
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    postcount = cursor.fetchone()
    if postcount is not None:
        postcount = postcount[0]
    else:
        postcount = 0

    sql = """SELECT COUNT(*) as frequency
        FROM Posts
        WHERE user = ? AND album = 'True'
        GROUP BY user;
        """
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    albumcount = cursor.fetchone()
    if albumcount is not None:
        albumcount = albumcount[0]
    else:
        albumcount = 0

    sql = """SELECT COUNT(*) as frequency
        FROM friendrequests
        WHERE usersend = ? AND status = 2
        GROUP BY usersend;
        """
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    followingcount = cursor.fetchone()
    if followingcount is not None:
        followingcount = followingcount[0]
    else:
        followingcount = 0

    sql = """SELECT COUNT(*) as frequency
            FROM friendrequests
            WHERE userreceive = ? AND status = 2
            GROUP BY userreceive;
            """
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    followercount = cursor.fetchone()
    if followercount is not None:
        followercount = followercount[0]
    else:
        followercount = 0

    sql = "SELECT privacy FROM Accounts WHERE username = ?"
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    getprivacy = cursor.fetchone()
    getprivacy = getprivacy[0]

    cursor = con.cursor()
    sql = "SELECT status FROM friendrequests WHERE usersend = ? AND userreceive = ?"
    cursor.execute(sql, (usernamesend, username))
    getstatus = cursor.fetchone()

    if getstatus != None:
        getstatusclean = getstatus[0]
    else:
        getstatusclean = 0
        con = sqlite3.connect('database.db')
        cursor = con.cursor()
        sql = "INSERT INTO friendrequests(usersend, userreceive, status) VALUES(?,?,0)"
        cursor.execute(sql, (usernamesend, username))
        con.commit()

    if request.method == "POST":
        datetimenow = datetime.now()
        formattedtime = datetimenow.strftime("%d/%m/%y %H:%M:%S")
        if "send" in request.form:
            if getstatus == None:
                con = sqlite3.connect('database.db')
                cursor = con.cursor()
                sql = "INSERT INTO friendrequests(usersend, userreceive, status,timesent) VALUES(?,?,1,?)"
                cursor.execute(sql, (usernamesend, username, formattedtime))
                con.commit()
                return redirect(url_for('viewaccount', id=username))
            else:
                con = sqlite3.connect('database.db')
                cursor = con.cursor()
                sql = "UPDATE friendrequests SET usersend = ?, userreceive = ?, status = 1, timesent = ? WHERE usersend = ? AND userreceive = ?"  # update where
                cursor.execute(sql, (usernamesend, username, formattedtime, usernamesend, username))
                con.commit()
                return redirect(url_for('viewaccount', id=username))

        elif "cancel" in request.form:
            con = sqlite3.connect('database.db')
            cursor = con.cursor()
            sql = "DELETE FROM friendrequests WHERE usersend = ? AND userreceive = ?"
            cursor.execute(sql, (usernamesend, username))
            con.commit()
            return redirect(url_for('viewaccount', id=username))
        elif "remove" in request.form:
            con = sqlite3.connect('database.db')
            cursor = con.cursor()
            sql = "DELETE FROM friendrequests WHERE userreceive = ? AND usersend = ?"
            cursor.execute(sql, (username, usernamesend))
            con.commit()
            return redirect(url_for('viewaccount', id=username))
        elif "add" in request.form:
            con = sqlite3.connect('database.db')
            cursor = con.cursor()
            sql = "UPDATE friendrequests SET status = 2,timesent = ? WHERE userreceive = ? AND usersend = ?"
            cursor.execute(sql, (formattedtime, username, usernamesend,))
            con.commit()

            return redirect(url_for('viewaccount', id=username))

    return render_template("viewaccount.html", rows=rows, username=username, desc=desc, age=ageget,
                           getstatusclean=getstatusclean, getprivacy=getprivacy, gender=gender, pfp=pfp,
                           postcount=postcount, albumcount=albumcount, followercount=followercount,
                           followingcount=followingcount)


@web_site.route('/activity', methods=['GET', 'POST'])
def activity():
    if "username" not in session: #if no user is logged in
        return redirect("/login") #redirect to login page

    msg = "" #default to empty
    username = session["username"] #get the user that is logged in
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = """SELECT Likes.usersliked, Likes.id, Likes.timesent
       FROM Likes
       JOIN Posts ON Likes.id = Posts.id
       WHERE Posts.user = ?""" #get all the user's post that have been liked and by who and also when
    cursor.execute(sql, (username,))
    rows = cursor.fetchall()
    newrows = []
    for row in rows:
        rowdict = dict(row) #add the likes to a dictionary and id each bit of info with type = Like
        rowdict['type'] = 'like'
        newrows.append(rowdict)

    con.row_factory = sqlite3.Row
    cursor = con.cursor() #get all the users who have successfully followed the user
    sql = """SELECT friendrequests.usersend, friendrequests.timesent
           FROM friendrequests
           WHERE friendrequests.userreceive = ? AND status = 2"""
    cursor.execute(sql, (username,))
    rows2 = cursor.fetchall()
    newrows2 = []
    for row in rows2:
        rowdict = dict(row) #turn the followers into a dictionary and give each info a type of "follower"
        rowdict['type'] = 'follower'
        newrows2.append(rowdict)

    con.row_factory = sqlite3.Row
    cursor = con.cursor() #get all the friend requests to the user
    sql = "SELECT * FROM friendrequests WHERE userreceive = ? AND status = 1"
    cursor.execute(sql, (username,))
    rows3 = cursor.fetchall()
    newrows3 = []
    for row in rows3:
        rowdict = dict(row) #give each friend request a type of "request"
        rowdict['type'] = 'request'
        newrows3.append(rowdict)

    con.row_factory = sqlite3.Row
    cursor = con.cursor() #get all the users that the logged in user now follows
    sql = "SELECT * FROM friendrequests WHERE usersend = ? AND status = 2"
    cursor.execute(sql, (username,))
    rows4 = cursor.fetchall()
    newrows4 = []
    for row in rows4:
        rowdict = dict(row) #add to a new dictionary with type "following"
        rowdict['type'] = 'following'
        newrows4.append(rowdict)

    con.row_factory = sqlite3.Row
    cursor = con.cursor() #get all the friend requests the user has sent
    sql = "SELECT * FROM friendrequests WHERE usersend = ? AND status = 1"
    cursor.execute(sql, (username,))
    rows5 = cursor.fetchall()
    newrows5 = []
    for row in rows5:
        rowdict = dict(row) #give each sent friend request a type of "requestfollowing"
        rowdict['type'] = 'requestfollowing'
        newrows5.append(rowdict)

    newrows += newrows2 #add each dictionary together
    newrows += newrows3
    newrows += newrows4
    newrows += newrows5

    rowsinsec = []
    for row in newrows:
        getdatetime = datetime.strptime(row["timesent"], "%d/%m/%y %H:%M:%S")  # converts to known format
        datetimenow = datetime.now()  # Gets time now
        datetimedif = datetimenow - getdatetime  # finds difference
        timedif = datetimedif.total_seconds()  # converts difference to seconds
        rowdict = dict(row)  # creates a new dictionary of each bit of info
        rowdict['timedif'] = timedif  # adds how long ago it happened (time difference in seconds)
        rowsinsec.append(rowdict)  # appends to list

    sortedrows = sorted(rowsinsec, key=lambda x: x.get('timedif')) #sort based on how long ago it was

    if sortedrows == []: #if there is no activity
        msg = "No recent activity" #provide message
    return render_template("activity.html", rows=sortedrows, username=username, msg=msg)


@web_site.route('/acceptignore', methods=['GET', 'POST'])
def acceptignore():
    if "username" not in session: #if no user is logged in
        return redirect("/login") #redirect them back to login page

    username = session["username"] #get the user that is logged in
    usernamesend = request.args.get('id') #get the user that sent the follow request / the user they clicked

    if request.method == "POST":
        if "accept" in request.form: #if accept clicked
            datetimenow = datetime.now() #get the date time now
            formattedtime = datetimenow.strftime("%d/%m/%y %H:%M:%S") #format into common format
            con = sqlite3.connect('database.db')
            cursor = con.cursor()
            sql = "UPDATE friendrequests SET status = 2,timesent = ? WHERE userreceive = ? AND usersend = ?"  #update relationship (and add when they accepted)
            cursor.execute(sql, (formattedtime, username, usernamesend))
            con.commit()
            return redirect('/activity') #redirect back to activity page
        elif "ignore" in request.form: #if declined
            con = sqlite3.connect('database.db')
            cursor = con.cursor()
            sql = "DELETE FROM friendrequests WHERE userreceive = ? AND usersend = ?" #delete the relationship
            cursor.execute(sql, (username, usernamesend))
            con.commit()
            return redirect('/activity') #redirect back to activity page
    return render_template("acceptignore.html")


@web_site.route('/followinglist')
def followinglist():
    if "username" not in session: #if no user is logged in
        return redirect("/login") #redirect to login page

    msg = "" #default to empty
    username = session["username"] #get user that is logged in
    viewusername = request.args.get('id') #get whos list they are viewing
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    sql = "SELECT * FROM friendrequests WHERE usersend = ? AND status = 2" #get who follows the viewusername
    cursor = con.cursor()
    cursor.execute(sql, (viewusername,))
    rows = cursor.fetchall()
    usernames = []

    for row in rows:
        usernames.append(row['userreceive']) #add usernames to a list
    usernames = mergesort(usernames) #merge sort the names

    # sorts it based of the index of x.lower() in list "usernames"
    rows = sorted(rows, key=lambda x: usernames.index(x["userreceive"].lower()))

    if rows == []: #if the user doesn't follow anyone
        msg = "No followers found" #provide error message

    return render_template("followinglist.html", rows=rows, username=username, msg=msg)


def mergesort(usernames):
    username2 = []

    for i in usernames:
        newitem = ""
        for x in i:
            newitem += x.lower()  # we need to convert to lower as it uses ascii so capitals can mess it up (s > T)
        username2.append(newitem)
    usernames = username2

    # if less than one then obv we cant sort
    if len(usernames) <= 1:
        return usernames
    # if greater than 1, all good so we split in two and sort each half
    middle = len(usernames) // 2
    halfone = usernames[:middle]
    halftwo = usernames[middle:]

    halfone = mergesort(halfone)  # recursion
    halftwo = mergesort(halftwo)  # recursion

    # merge the two halves together

    index1 = 0
    index2 = 0
    output = []
    while index1 < len(halfone) and index2 < len(halftwo):  # while the end of each half has not been reached
        if halfone[index1] <= halftwo[index2]:  # if half one is less than half two, half one gets added first
            output.append(halfone[index1])
            index1 += 1  # halfone at that index has been added, so we move to the next one
        else:  # else half two must be smaller, so half to gets added before
            output.append(halftwo[index2])
            index2 += 1  # halftwo at that index has been added, so we move to the next one

    # add remaining stuff
    output += halfone[index1:]
    output += halftwo[index2:]

    return output


@web_site.route('/removefollowing', methods=['GET', 'POST'])
def removefollowing():
    if "username" not in session: #if no user is logged in
        return redirect("/login") #redirect to login page

    username = session["username"] #get the user that is logged in
    follower = request.args.get('id') #get the user they have clicked
    if "remove" in request.form: #if remove clicked
        con = sqlite3.connect('database.db')
        cursor = con.cursor()
        sql = "DELETE FROM friendrequests WHERE usersend = ? AND userreceive = ?" #remove the relationship where they follow that user
        cursor.execute(sql, (username, follower))
        con.commit()
        return redirect(url_for('followinglist', id=username)) #redirect back to following list
    return render_template("removefollowing.html", follower=follower)


@web_site.route('/followerlist')
def followerlist():
    if "username" not in session: #if a user is not logged in
        return redirect("/login") #redirect to the login page

    msg = ""
    username = session["username"] #get the user that is logged in
    viewusername = request.args.get('id') #get the user that the list is related to (so it works for view account)
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    sql = "SELECT * FROM friendrequests WHERE userreceive = ? AND status = 2" #get all the people that follow the user
    cursor = con.cursor()
    cursor.execute(sql, (viewusername,))
    rows = cursor.fetchall()

    usernames = []

    for row in rows:
        usernames.append(row['usersend']) #add all the usernames to a list
    usernames = mergesort(usernames) #merge sort the usernames

    # sorts it based of the index of x.lower() in list "usernames"
    rows = sorted(rows, key=lambda x: usernames.index(x["usersend"].lower())) #sort the rows based on what the merge sort has provided

    if rows == []: #if the user has no followers
        msg = "No followers...yet? :(" #provide an error message
    return render_template("followerlist.html", rows=rows, username=username, msg=msg)


@web_site.route('/removefollower', methods=['GET', 'POST'])
def removefollower():
    if "username" not in session: #if no user is logged in
        return redirect("/login") #redirect them to the login page

    username = session["username"] #get the user who is logged in
    follower = request.args.get('id') #get the follower they have clicked on
    if "remove" in request.form: #if they click remove
        con = sqlite3.connect('database.db')
        cursor = con.cursor()
        sql = "DELETE FROM friendrequests WHERE userreceive = ? AND usersend = ?" #remove the connection from the database
        cursor.execute(sql, (username, follower))
        con.commit()
        return redirect(url_for('followerlist', id=username)) #redirect back to follower list
    return render_template("removefollower.html", follower=follower)


@web_site.route('/editpost', methods=['GET', 'POST'])
def editpost():
    if "username" not in session: #if no user is logged in
        return redirect("/login") #redirect to login page

    username = session["username"] #get the user that is logged in
    postid = request.args.get('id') #get the post that has been clicked / chosen to edit
    con = sqlite3.connect('database.db')

    # get the album id if its in one

    sql = "SELECT user FROM Posts WHERE id = ?" #get the user that created the post / has permissions to edit the post
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    getuser = cursor.fetchone()
    print(session.get("lat"))
    if not getuser: #if there is no user associtated with the post id, the post doesnt exist (prevents manual entry)
        return render_template('404.html') #redirect to error page
    if getuser[0] != username: #if the logged in user isnt the same as the user who created the post (prevents manual entry)
        return render_template('404.html') #redirect to error page

    con.row_factory = sqlite3.Row
    sql = "SELECT * FROM Posts WHERE id = ?" #get all info about the post
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    rows = cursor.fetchall()

    con.row_factory = sqlite3.Row
    sql = "SELECT * FROM photodetails WHERE id = ?" #get all photodetails about the post
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    rows2 = cursor.fetchall()

    sql = "Select datetime FROM photodetails WHERE id = ?" #get the datetime seperately
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    datetimeup = cursor.fetchone()
    datetimeup = datetimeup[0]
    date = datetimeup[:10] #split into the date and into the time
    time = datetimeup[11:]

    if request.method == "POST":
        lat = session.get('lat') #if they updated the location, get the place (lng/lat) they clicked
        lng = session.get('lng')
        if "cancel" in request.form: #if they clicked cancel, discard changes
            session['lat'] = 0 #set session lat/lng back to 0 as others use it
            session['lng'] = 0
            return redirect(url_for('viewpost', id=postid)) #redirect back to viewpost
        con = sqlite3.connect('database.db')
        description = request.form["description"] #get the new description
        description = moderate(description)
        text = request.form["text"] #get the new title
        text = moderate(text)
        if text == "": #if the title and descr are empty, just default to "untitled"
            text = "Untitled"
        if description == "":
            description = "Untitled"
        sql = "UPDATE Posts SET descr = ?, text = ?, lat = ?, lng = ? WHERE id = ?" #update title, descr and location in posts table
        cursor = con.cursor()
        cursor.execute(sql, (description, text, lat, lng, postid))
        con.commit()

        GetNamedLocation(lat, lng, postid) #get the new named location if it changes (update database done in the function)

        make = request.form["make"] #get the new details about the photo
        model = request.form["model"]

        date = request.form["date"]
        time = request.form["time"]
        if date != "" and time != "": #if neither are emtpy
            metadatadatetime = str(date) + " " + str(time) #concatonate so can be stored together in database
        elif date != "" and time == "": #if date is valid but time is empty, default time to 12:00
            metadatadatetime = str(date) + " " + "12:00"
        else:
            metadatadatetime = "N/A" #if date chosen (even if time chosen) default back to N/A
        ISO = request.form["ISO"] #continue getting info about the post
        LensModel = request.form["lensmodel"]
        FNumber = request.form["fstop"]
        ExposureTime = request.form["shutterspeed"]
        #if any left emtpy, default to N/A
        if make == "" or make.isspace():
            make = "N/A"
        if model == "" or model.isspace():
            model = "N/A"
        if ISO == "" or ISO.isspace():
            ISO = "N/A"
        if LensModel == "" or LensModel.isspace():
            LensModel = "N/A"
        if FNumber == "" or FNumber.isspace():
            FNumber = "N/A"
        if ExposureTime == "" or ExposureTime.isspace():
            ExposureTime = "N/A"

        #update the photodetails table with the new info
        con = sqlite3.connect('database.db')
        sql = "UPDATE photodetails SET make = ?, model = ?, datetime = ?, ISO = ?, lensmodel = ?, fstop = ?, shutterspeed = ? WHERE id = ?"
        cursor = con.cursor()
        cursor.execute(sql, (make, model, metadatadatetime, ISO, LensModel, FNumber, ExposureTime, postid,))
        con.commit()

        listofalbumids = []
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        sql = "SELECT albumid FROM albums WHERE postid = ?"  # gets a list of all the albums the post is in
        cursor.execute(sql, (postid,))
        allids = cursor.fetchall()
        for row in allids:
            listofalbumids.append(row[0])

        for i in listofalbumids:
            updatealbumlocation(i) #update the album location (see album section)
        session['lat'] = 0 #set lng lat session to 0
        session['lng'] = 0
        return redirect(url_for('viewpost', id=postid)) #once edited, redirect back to viewpost
    return render_template("editpost.html", rows=rows, postid=postid, rows2=rows2, date=date, time=time)


@web_site.route('/deletealbum', methods=['GET', 'POST'])
def deletealbum():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    albumid = request.args.get('id')

    con = sqlite3.connect('database.db')
    sql = "SELECT user FROM Posts WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (albumid,))
    getuser = cursor.fetchone()

    if not getuser:
        return render_template('404.html')
    if getuser[0] != username:
        return render_template('404.html')

    deleted = False

    if request.method == "POST":
        if "yes" in request.form:
            con = sqlite3.connect('database.db')
            con.row_factory = sqlite3.Row
            sql = "DELETE FROM Posts WHERE id = ?"
            cursor = con.cursor()
            cursor.execute(sql, (albumid,))
            con.commit()

            con.row_factory = sqlite3.Row
            sql = "DELETE FROM albums WHERE albumid = ?"
            cursor = con.cursor()
            cursor.execute(sql, (albumid,))
            con.commit()

            con.row_factory = sqlite3.Row
            sql = "DELETE FROM savedposts WHERE savedpostid = ?"
            cursor = con.cursor()
            cursor.execute(sql, (albumid,))
            con.commit()

            deleted = True
        elif "no" in request.form:
            return redirect(url_for('viewalbum', id=albumid))
    return render_template("deletealbum.html", deleted=deleted)


@web_site.route('/deleteaccount', methods=['GET', 'POST'])
def deleteaccount():
    if "username" not in session: #if a user is not logged in
        return redirect("/login") #redirect them to login page

    username = session["username"] #get user who is logged in
    msg = "" #set default empty
    con = sqlite3.connect('database.db')
    sql = "Select password FROM Accounts WHERE username = ?" #select their (hashed) password
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    getpassword = cursor.fetchone()
    getpassword = getpassword[0] #get out of tuple form
    if request.method == "POST":
        password = request.form["password"] #get what they think is their password
        if getpassword == hash(password): #if their inputted hashed password equals their old hashed password delete it
            sql = "Select pfp FROM Accounts WHERE username = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            getfilename = cursor.fetchone()
            getfilename = getfilename[0]
            if getfilename != "blank-profile-picture-973460_960_720.jpg": #if pfp not the default one
                os.remove(
                    os.path.join(web_site.root_path, 'static', 'ProfilePictures', getfilename))  # delete their pfp

            con.row_factory = sqlite3.Row
            sql = "SELECT * FROM Posts WHERE user = ?" #gets all info about all their posts
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            rows = cursor.fetchall()
            for row in rows:
                filename = row["filename"] #gets filename of each posts' picture
                if filename != "7da6b012d99beac0c7eff0949b27b7e6.png": #if not album picture (used by all so must remain)
                    os.remove(os.path.join(web_site.root_path, 'static', 'UploadedPhotos', filename)) #delete post picture

            sql = "DELETE FROM tempphotos WHERE user = ?" #delete their drafts
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = "DELETE FROM savedposts WHERE username = ?" #delete any posts they have saved
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            # update like and dislike counts of the stuff we have liked/disliked
            con.row_factory = sqlite3.Row
            sql = "Select id FROM Likes WHERE usersliked = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            rows = cursor.fetchall()
            for row in rows:
                sql = "Select likes FROM Posts WHERE id = ?" #remove 1 like from all posts they have liked
                cursor = con.cursor()
                cursor.execute(sql, (row[0],))
                getlikes = cursor.fetchone()
                getlikes = getlikes[0]
                getlikes -= 1

                sql = "UPDATE Posts SET likes = ? WHERE id = ?" #update like count for each of those posts
                cursor = con.cursor()
                cursor.execute(sql, (getlikes, row[0],))
                con.commit()

            con.row_factory = sqlite3.Row
            sql = "Select id FROM Dislikes WHERE usersdisliked = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            rows = cursor.fetchall()
            for row in rows:
                sql = "Select dislikes FROM Posts WHERE id = ?" #remove 1 dislike from all posts they have disliked
                cursor = con.cursor()
                cursor.execute(sql, (row[0],))
                getdislikes = cursor.fetchone()
                getdislikes = getdislikes[0]
                getdislikes -= 1

                sql = "UPDATE Posts SET dislikes = ? WHERE id = ?" #update dislike count for each of those posts
                cursor = con.cursor()
                cursor.execute(sql, (getdislikes, row[0],))
                con.commit()
            # END OF update like and dislike counts of the stuff we have liked/disliked

            sql = "DELETE FROM Likes WHERE usersliked = ?" #delete from the like table where they have liked
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = "DELETE FROM Dislikes WHERE usersdisliked = ?" #delete from the dislike table where they have liked
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = "DELETE FROM friendrequests WHERE usersend = ? OR userreceive = ?" #delete all friend relationships
            cursor = con.cursor()
            cursor.execute(sql, (username, username,))
            con.commit()

            sql = """DELETE FROM Likes
            WHERE id IN (SELECT id FROM Posts WHERE user = ?)""" #delete their posts from the like table (recommendation)
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = """DELETE FROM Dislikes
            WHERE id IN (SELECT id FROM Posts WHERE user = ?)""" #delete their posts from the dislike table
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = """DELETE FROM albums
            WHERE albumid IN (SELECT id FROM Posts WHERE user = ?)""" #delete from album table their albums and the posts associated
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = """DELETE FROM savedposts
                        WHERE savedpostid IN (SELECT id FROM Posts WHERE user = ?)""" #delete their posts from other peoples saved posts
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = """DELETE FROM photodetails
            WHERE id IN (SELECT id FROM Posts WHERE user = ?)""" #delete the photodetails of all their posts
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = """DELETE FROM Posts
            where user = ?"""
            cursor = con.cursor() #delete all their posts, must happen (almost) last so the other stuff can happen first (likes etc)
            cursor.execute(sql, (username,))
            con.commit()

            sql = "DELETE FROM Accounts WHERE username = ?" #finally delete account from account table, must happen last
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()
            if "username" in session and session["username"] == username: #remove name from session
                del session["username"]
            return redirect("/Index")
        else:
            msg = "Incorrect Password" #if inputted password doesn't match then provide appropriate error message

    return render_template("deleteaccount.html", msg=msg)


@web_site.route('/deletepost', methods=['GET', 'POST'])
def deletepost():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    postid = request.args.get('id')

    con = sqlite3.connect('database.db')
    sql = "SELECT user FROM Posts WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    getuser = cursor.fetchone()
    if not getuser:
        return render_template('404.html')
    if getuser[0] != username:
        return render_template('404.html')

    deleted = False
    if request.method == "POST":
        if "yes" in request.form:
            con = sqlite3.connect('database.db')
            sql = "Select filename FROM Posts WHERE id = ?"
            cursor = con.cursor()
            cursor.execute(sql, (postid,))
            getfilename = cursor.fetchone()
            filename = getfilename[0]
            os.remove(os.path.join(web_site.root_path, 'static', 'UploadedPhotos', filename))  # deletes the file

            listofalbumids = []
            con.row_factory = sqlite3.Row
            cursor = con.cursor()
            sql = "SELECT albumid FROM albums WHERE postid = ?"
            cursor.execute(sql, (postid,))
            allids = cursor.fetchall()
            for row in allids:
                listofalbumids.append(row[0])

            con = sqlite3.connect('database.db')
            con.row_factory = sqlite3.Row
            sql = "DELETE FROM Posts WHERE id = ?"
            cursor = con.cursor()
            cursor.execute(sql, (postid,))
            con.commit()

            con.row_factory = sqlite3.Row
            sql = "DELETE FROM albums WHERE postid = ?"
            cursor = con.cursor()
            cursor.execute(sql, (postid,))
            con.commit()

            con.row_factory = sqlite3.Row
            sql = "DELETE FROM photodetails WHERE id = ?"
            cursor = con.cursor()
            cursor.execute(sql, (postid,))
            con.commit()

            con.row_factory = sqlite3.Row
            sql = "DELETE FROM Likes WHERE id = ?"
            cursor = con.cursor()
            cursor.execute(sql, (postid,))
            con.commit()

            con.row_factory = sqlite3.Row
            sql = "DELETE FROM Dislikes WHERE id = ?"
            cursor = con.cursor()
            cursor.execute(sql, (postid,))
            con.commit()

            con.row_factory = sqlite3.Row
            sql = "DELETE FROM savedposts WHERE savedpostid = ?"
            cursor = con.cursor()
            cursor.execute(sql, (postid,))
            con.commit()

            for i in listofalbumids:
                updatealbumlocation(i)

            deleted = True
        elif "no" in request.form:
            return redirect(url_for('viewpost', id=postid))
    return render_template("deletepost.html", deleted=deleted)


@web_site.route('/savedposts')
def savedposts():
    if "username" not in session: #if no user is logged in
        return redirect("/login") #redirect to login page

    msg = "" #set default to empty
    username = session["username"] #get user that is logged in
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = """SELECT Posts.*, Accounts.pfp
    FROM Posts
    JOIN Accounts ON Accounts.username = Posts.user
    LEFT JOIN savedposts ON savedposts.savedpostid = Posts.id
    WHERE savedposts.username = ?""" #get all the post info of each saved post, and the user's pfp for each
    cursor.execute(sql, (username,))
    rows = cursor.fetchall()
    rows = rows[::-1] #reverse order so its most recently saved to least

    if rows == []: #if no posts saved
        msg = "No saved posts found" #provide appropriate message
    return render_template("savedposts.html", rows=rows, username=username, msg=msg)


@web_site.route('/search')
def search():
    if "username" not in session:
        return redirect("/login")

    return render_template("search.html")


@web_site.route('/create')
def create():
    if "username" not in session:
        return redirect("/login")

    return render_template("create.html")


@web_site.route('/GeoSnaps')
def GeoSnaps():
    return render_template("GeoSnaps.html")

@web_site.route('/helppage')
def helppage():
    return render_template("helppage.html")

@web_site.route('/ajaxsearchposts/<search>')
def ajaxsearchposts(search):
    search = search.replace("%20", " ")
    msg = ""
    username = session["username"]
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cursor = con.cursor()

    sql = '''
      SELECT DISTINCT Posts.*, Accounts.pfp
      FROM Posts
      LEFT JOIN photodetails ON Posts.id = photodetails.id
      JOIN Accounts ON Accounts.username = Posts.user
      LEFT JOIN friendrequests ON friendrequests.userreceive = Accounts.username
      WHERE (Posts.privacy = 'public' OR (friendrequests.usersend = ? AND status = 2))
      AND (Posts.text LIKE ? OR Posts.descr LIKE ? OR Posts.user LIKE ? OR photodetails.model LIKE ? OR photodetails.make LIKE ? OR Posts.country LIKE ? OR Posts.town LIKE ? OR Posts.city LIKE ?)'''
    cursor.execute(sql, (
    username, '%' + search + '%', '%' + search + '%', '%' + search + '%', '%' + search + '%', '%' + search + '%',
    '%' + search + '%', '%' + search + '%', '%' + search + '%',))
    con.commit()
    rows = cursor.fetchall()
    newrows = []
    for row in rows:
        rowdict = dict(row)
        rowdict['type'] = 'post'
        newrows.append(rowdict)
    sql = '''
       SELECT username, pfp
       FROM Accounts
       WHERE username LIKE ?'''
    cursor.execute(sql, ('%' + search + '%',))
    con.commit()
    rows2 = cursor.fetchall()
    newrows2 = []
    for row in rows2:
        rowdict = dict(row)
        rowdict['type'] = 'user'
        newrows2.append(rowdict)

    newrows += newrows2

    if newrows == []:
        msg = "No results found"

    return render_template('ajaxsearchposts.html', rows=newrows, username=username, msg=msg)


web_site.run(host='0.0.0.0', port=8080)

#if __name__ == "__main__":
#    web_site.run()