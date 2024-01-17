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
    msg = ""
    usermsg = ""
    empty = ""
    filename = "1024px-Cross_red_circle.svg.png"
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        if username and password != "":
            con = sqlite3.connect('database.db')
            sql = "SELECT password FROM Accounts WHERE username = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            getpassword = cursor.fetchone()
            critera = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!?*%@$&]).{8,}$")
            if getpassword is None:
                if " " not in username and len(username) >= 3 and len(username) <= 15:
                    if bool(critera.match(password)):
                        password = hash(password)
                        sql = "INSERT INTO Accounts(username, password, description, dob) VALUES(?, ?, ?, ?)"
                        cursor = con.cursor()
                        cursor.execute(sql, (username, password, empty, empty))
                        con.commit()
                        return redirect("/login")
                    else:
                        msg = "Password does not meet criteria"
                else:
                    usermsg = "Username does not meet criteria"
        else:
            msg = "Do not leave blank"
    return render_template("Index.html", filename = filename, msg = msg, usermsg = usermsg)


def moderate(string):
    badworddict = {
        "shit": "shirt", #little reference to "the good place", probably remove for actual project...
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


def GetNamedLocation(lat,lng, id):
    try:
        geolocator = Nominatim(user_agent="web_site")
        latlng = str(lat) + ", " + str(lng)
        location = geolocator.reverse(latlng, language='en')
        try:
            country = location.raw['address']['country']
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


        if country == None:
            country = "N/A"
        if city == None:
            city = "N/A"
        if town == None:
            town = "N/A"
        con = sqlite3.connect('database.db')  #
        sql = "UPDATE Posts SET country = ?, city = ?, town = ? WHERE id = ?"
        cursor = con.cursor()
        cursor.execute(sql, (country, city, town,id,))
        con.commit()

        return
    except:
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
    con = sqlite3.connect('database.db')
    sql = "SELECT password FROM Accounts WHERE username = ?"
    cursor = con.cursor()
    cursor.execute(sql, (search,))
    getpassword = cursor.fetchone()
    if getpassword is None:
        unique = "Check_green_circle.svg.png"
    else:
        unique = "1024px-Cross_red_circle.svg.png"
    if len(search) >= 3 and len(search) <= 15:
        length = "Check_green_circle.svg.png"
    else:
        length = "1024px-Cross_red_circle.svg.png"

    if " " not in search and not search[0].isspace() and not search[-1].isspace():
        space = "Check_green_circle.svg.png"
    else:
        space = "1024px-Cross_red_circle.svg.png"

    if search == "empty":
        unique = "1024px-Cross_red_circle.svg.png"
        length = "1024px-Cross_red_circle.svg.png"

    return jsonify({'unique': unique, 'space': space, 'length': length })

@web_site.route('/ajaxpasswords/<search>')
def ajaxpasswords(search):
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
    if not uppercheck or search == "empty":
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

    return jsonify({'upper': upper,'length': length,'lower': lower,'digit': digit,'symb': symb,'matching': matching })

@web_site.route('/ajaxpasswordsindex/<search>')
def ajaxpasswordsindex(search):
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
    if not uppercheck or search == "empty":
        upper = "1024px-Cross_red_circle.svg.png"
    if not lowercheck or search == "empty":
        lower = "1024px-Cross_red_circle.svg.png"
    if not digitcheck or search == "empty":
        digit = "1024px-Cross_red_circle.svg.png"
    if not symbcheck or search == "empty":
        symb = "1024px-Cross_red_circle.svg.png"


    return jsonify({'upper': upper,'length': length,'lower': lower,'digit': digit,'symb': symb})

@web_site.route('/login', methods=['GET', 'POST'])
def login():
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username and password != "":
            con = sqlite3.connect('database.db')
            sql = "SELECT password FROM Accounts WHERE username = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            getpassword = cursor.fetchone()
            if getpassword is not None:
                getpassword = getpassword[0]
                password = hash(password)
                if password == getpassword:
                    session["username"] = username
                    return redirect(url_for('listmyposts'))

                else:
                    msg = "Incorrect Password"
            else:
                msg = "Username not found"
        else:
            msg = "Do not leave blank"
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
    image = Image.open(photo_path)
    exifdata = image._getexif()

    if exifdata is not None:#explain!
        for tag, value in exifdata.items():
            tagname = TAGS.get(tag, tag)#forgot what this line does
            metadata[tagname] = value
    return metadata


def convertGPS(gpsdata):  # converts DMS to lat and lng
    try:
        latdegrees = float((gpsdata[2][0]))
        latmin = float((gpsdata[2][1]))
        latsec = float((gpsdata[2][2]))

        lngdegrees = float((gpsdata[4][0]))
        lngmin = float((gpsdata[4][1]))
        lngsec = float((gpsdata[4][2]))

        lat = latdegrees + (latmin / 60) + (latsec / 3600)
        lng = lngdegrees + (lngmin / 60) + (lngsec / 3600)

        lat = round(lat, 8)
        lng = round(lng, 8)

        if gpsdata[1] == 'S':
            lat = -lat
        if gpsdata[3] == 'W':
            lng = -lng

        return lat, lng
    except:
        return None, None


def randomfilename(path):#calc the probability
    randstr = ""
    letters = string.ascii_letters
    for i in range(20):
        randstr += random.choice(letters)
    datetimenow = datetime.now()
    formattedtime = datetimenow.strftime("%d%m%y%H%M%S%f")[:-3]
    filename = (randstr + formattedtime)

    filepath = os.path.join(path, filename)

    if os.path.exists(filepath):
        return randomfilename(path)#recursive until you find a unique one, but probably unnecessary (guarantees unique anyway)
    else:
        return filename


@web_site.route('/uploadphoto', methods=['GET', 'POST'])
def uploadphoto():
    if "username" not in session:
        return redirect("/login")

    posted = False
    prevpostid = request.args.get('id')
    if prevpostid != None:
        posted = True
    msg = ""


    if request.method == 'POST':
        datetimenow = datetime.now()
        formattedtime = datetimenow.strftime("%d/%m/%y %H:%M")
        randfilename = randomfilename(os.path.join(web_site.root_path, 'static', 'UploadedPhotos'))
        username = session["username"]
        photo = request.files['photo']
        if photo.filename != "":
            filename = randfilename + "_" + photo.filename
            try:
                photo.save(os.path.join(web_site.root_path, 'static', 'UploadedPhotos', filename))
                con = sqlite3.connect('database.db')
                sql = "INSERT INTO tempphotos(filename, user) VALUES(?,?)"
                cursor = con.cursor()
                cursor.execute(sql, (filename,username))
                con.commit()

                sql = "SELECT id FROM tempphotos WHERE filename = ? AND user = ?"
                cursor = con.cursor()
                cursor.execute(sql, (filename,username))
                getid = cursor.fetchone()
                getid = getid[0]

                photo_path = os.path.join(web_site.root_path, 'static', 'UploadedPhotos', filename)

                metadata = get_metadata(photo_path)
                make = str(metadata.get('Make', 'N/A'))
                model = str(metadata.get('Model', 'N/A'))
                metadatadatetime = str(metadata.get('DateTime', 'N/A'))
                ISO = str(metadata.get('ISOSpeedRatings', 'N/A'))
                LensModel = str(metadata.get('LensModel', 'N/A'))
                FNumber = str(metadata.get('FNumber', 'N/A'))
                ExposureTime = str(metadata.get('ExposureTime', 'N/A'))
                if ExposureTime != "N/A":
                    ExposureTime = str(round(1 / float(ExposureTime)))
                if metadatadatetime == "N/A":
                    metadatadatetime = str(metadata.get('DateTimeOriginal', 'N/A'))  # try other tag if other is empty

                if metadatadatetime != "N/A":
                    metadatadatetime = metadatadatetime[:-3]
                    metadatadatetime = metadatadatetime.replace(":", "-", 2)

                gps_string = metadata.get('GPSInfo', 'N/A')
                if gps_string != "N/A":
                    output = convertGPS(gps_string)#converts it to lat lng
                    lat = output[0]
                    lng = output[1]
                else:
                    lat = None
                    lng = None


                sql = "UPDATE tempphotos SET make = ?, model = ?, timeposted = ?, datetime = ?, ISO = ?, lensmodel = ?, fstop = ?, shutterspeed = ?, lat = ?, lng = ? WHERE id = ?"
                cursor = con.cursor()
                cursor.execute(sql, (make, model, formattedtime, metadatadatetime, ISO, LensModel, FNumber, ExposureTime, lat, lng, getid,))
                con.commit()



                return redirect(url_for('addpost', id=getid))
            except:
                msg = "Image Error..."
                os.remove(os.path.join(web_site.root_path, 'static', 'UploadedPhotos', filename))
                con = sqlite3.connect('database.db')
                sql = "DELETE FROM tempphotos WHERE filename = ? and user = ?"
                cursor = con.cursor()
                cursor.execute(sql, (filename, username))
                con.commit()
        else:
            msg = "Please select an image"
    return render_template("uploadphoto.html",prevpostid = prevpostid, posted = posted, msg = msg)

@web_site.route('/addpost', methods=['GET', 'POST'])
def addpost():
    if "username" not in session:
        return redirect("/login")

    photoid = request.args.get('id')
    username = session["username"]

    con = sqlite3.connect('database.db')
    sql = "SELECT filename FROM tempphotos WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (photoid,))
    getfilename = cursor.fetchone()
    filename = getfilename[0]

    con = sqlite3.connect('database.db')
    sql = "SELECT user FROM tempphotos WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (photoid,))
    getuser = cursor.fetchone()
    getuser = getuser[0]
    if not getuser:
        return render_template('404.html')
    if getuser != username:
        return render_template('404.html')

    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT * FROM tempphotos WHERE id = ? AND user = ?"
    cursor.execute(sql, (photoid, username))
    con.commit()
    rows2 = cursor.fetchall()

    sql = "Select datetime FROM tempphotos WHERE id = ? AND user = ?"
    cursor = con.cursor()
    cursor.execute(sql, (photoid, username))
    datetimeup = cursor.fetchone()
    datetimeup = datetimeup[0]

    date = datetimeup[:10]
    time = datetimeup[11:]



    username = session["username"]
    msg = ""

    sql = "SELECT privacy FROM Accounts WHERE username = ?"
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    getprivacy = cursor.fetchone()
    getprivacy = getprivacy[0]

    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT * FROM Posts WHERE album = 'True' AND user = ?"
    cursor.execute(sql, (username,))
    rows = cursor.fetchall()

    if request.method == 'POST':
        datetimenow = datetime.now()
        formattedtime = datetimenow.strftime("%d/%m/%y %H:%M")
        sessionlat = session.get('lat')
        sessionlng = session.get('lng')


        text = request.form["text"]
        text = moderate(text)
        descr = request.form["descr"]
        descr = moderate(descr)
        selected_option = request.form['selected_option']
        make = request.form["make"]
        model = request.form["model"]
        date = request.form["date"]
        time = request.form["time"]
        if date != "" and time != "":
            metadatadatetime = str(date) + " " + str(time)
        elif date != "" and time == "":
            metadatadatetime = str(date) + " " + "12:00"
        else:
            metadatadatetime = "N/A"
        ISO = request.form["ISO"]
        LensModel = request.form["lensmodel"]
        FNumber = request.form["fstop"]
        ExposureTime = request.form["shutterspeed"]
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
        if "cancel" in request.form:
            con = sqlite3.connect('database.db')

            sql = "Select filename FROM tempphotos WHERE id = ?"
            cursor = con.cursor()
            cursor.execute(sql, (photoid,))
            getfilename = cursor.fetchone()
            filename = getfilename[0]
            os.remove(os.path.join(web_site.root_path, 'static', 'UploadedPhotos', filename))


            sql = "DELETE FROM tempphotos WHERE id = ? AND user = ?"
            cursor = con.cursor()
            cursor.execute(sql, (photoid, username))
            con.commit()
            session['lat'] = 0
            session['lng'] = 0
            return redirect(url_for('uploadphoto'))
        if "drafts" in request.form:
            if text == "":
                text = "Untitled"
            if descr == "":
                descr = "Untitled"
            con = sqlite3.connect('database.db')  #
            sql = "UPDATE tempphotos SET make = ?, model = ?, timeposted = ?, datetime = ?, ISO = ?, lensmodel = ?, fstop = ?, shutterspeed = ?, lng = ?, lat = ?, text = ?, descr = ? WHERE id = ?"
            cursor = con.cursor()
            cursor.execute(sql, (make, model, formattedtime, metadatadatetime, ISO, LensModel, FNumber, ExposureTime, sessionlng, sessionlat, text, descr,photoid))
            con.commit()
            session['lat'] = 0
            session['lng'] = 0
            return redirect(url_for('uploadphoto'))
        elif "submit" in request.form:
            if text != "" and descr != "":
                timeposted = formattedtime
                con = sqlite3.connect('database.db')
                sql = "INSERT INTO Posts(text,timeposted,user,filename, descr, privacy, lng, lat) VALUES(?,?,?,?,?,?,?,?)"
                cursor = con.cursor()
                cursor.execute(sql, (text, timeposted, username, filename, descr, getprivacy, sessionlng, sessionlat,))
                con.commit()
                sql = "SELECT id FROM Posts WHERE text = ? AND filename = ? AND user = ? AND timeposted = ? AND descr = ?" #THIS THIS filename is unique?
                cursor.execute(sql, (text, filename, username, timeposted, descr))
                postidtup = cursor.fetchone()
                postid = postidtup[0]


                sql = "INSERT INTO photodetails(make, model, datetime, ISO, lensmodel, fstop, shutterspeed,id) VALUES(?,?,?,?,?,?,?,?)"
                cursor = con.cursor()
                cursor.execute(sql, (make, model, metadatadatetime, ISO, LensModel, FNumber, ExposureTime, postid))
                con.commit()

                GetNamedLocation(sessionlat,sessionlng,postid)

                if selected_option != "none":
                    con = sqlite3.connect('database.db')
                    sql = "SELECT id FROM Posts WHERE text = ? AND user = ? AND album = 'True'"
                    cursor = con.cursor()
                    cursor.execute(sql, (selected_option, username,))
                    getalbumid = cursor.fetchone()
                    getalbumid = getalbumid[0]

                    sql = "INSERT INTO albums(albumid, postid, user) VALUES(?,?,?)"
                    cursor = con.cursor()
                    cursor.execute(sql, (getalbumid, postid, username,))#
                    con.commit()
                    updatealbumlocation(getalbumid)

                    #update the metadata

                con = sqlite3.connect('database.db')
                sql = "DELETE FROM tempphotos WHERE id = ? AND user = ?"
                cursor = con.cursor()
                cursor.execute(sql, (photoid, username))
                con.commit()
                session['lat'] = 0
                session['lng'] = 0
                return redirect(url_for('uploadphoto', id=postid))
            else:
                session['lat'] = 0
                session['lng'] = 0
                msg = "Do not leave blank"
    return render_template("addpost.html", msg=msg,rows=rows, filename = filename, rows2 =rows2, date = date, time = time)



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
            cursor.execute(sql, (newtext,row["id"]))
            con.commit()
        if descr == None:
            newdescr = "Untitled"
            sql = "UPDATE tempphotos SET descr = ? WHERE id = ?"  # gets every postid that the user has posted to drafts
            cursor.execute(sql, (newdescr,row["id"]))
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


    return render_template("drafts.html", rows = rows, msg = msg)


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
                cursor.execute(sql, (username,text,))
                getunid = cursor.fetchone()

                if getunid is None:
                    con = sqlite3.connect('database.db')
                    sql = "INSERT INTO Posts(text,user, descr, filename, privacy,album, timeposted) VALUES(?,?,?,?,?,?,?)"
                    cursor = con.cursor()
                    cursor.execute(sql, (text, username, descr, filename, getprivacy, "True",formattedtime,))
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


def updatealbumlocation(albumid): #also updates the average likes
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
        sql = "SELECT likes FROM Posts WHERE id = ?"  #avg likes of all posts (rounded up)
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
            datetimedict[i] = formatdattimetotal  # adds the seconds value to a dictionary with the key being the post id (i)
            sorteddatetime = sortdatetime(datetimedict)
            sorteddatetime = sorteddatetime[::-1]# sorts it
        else:
            unformatposts.append(i) #posts without a time
    sortedpostids = []
    for i in sorteddatetime:
        sortedpostids.append(i[0])  # once the dictinary is sorted in seconds ago then remove the seconds so just a list of postids in chronological order
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
    rows2 = cursor.fetchall() # rows 2 is for album info

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
            heightwidth.append(img.size[0])# get the width and height of the image
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
    return render_template("viewalbum.html", rows=postinfo, rows2=rows2,username=username, checksaved = checksaved, lnglatpoints = lnglatpoints, filenames = filenames,imagesize =imagesize)


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
    return render_template("editalbum.html", rows=rows, albumid=albumid, msg=msg,msg2=msg2)


def calcage(dob):
    try:
        dobtime = datetime.strptime(dob, "%Y-%m-%d")
        currentdate = datetime.now()
        age = currentdate.year - dobtime.year #find year dif
        if currentdate.month < dobtime.month: #if the month has not been then we take off a year
            age -= 1
        elif currentdate.month == dobtime.month and currentdate.day < dobtime.day: #if we are in the month, then if the day has not been we take away one
            age -= 1


    except:
        return dob
    return age



@web_site.route('/account', methods=['GET', 'POST'])
def listmyposts():
    if "username" not in session:
        return redirect("/login")


    username = session["username"]
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT * FROM Posts WHERE user = ?"
    cursor.execute(sql, (username,))
    con.commit()
    rows = cursor.fetchall()
    rows = rows[::-1]

    sql = "SELECT description, dob,gender,pfp FROM Accounts WHERE username = ?"  # spelt description wrong - will change later...
    cursor = con.cursor()
    cursor.execute(sql, (username,))

    row2 = cursor.fetchone()
    desc = row2[0]
    dobget = row2[1]
    ageget = calcage(dobget)
    genderget = row2[2]
    pfp = row2[3]

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

    return render_template("account.html", rows=rows, desc=desc, age=ageget,gender = genderget,pfp = pfp,
                           postcount=postcount, albumcount=albumcount,followercount=followercount,followingcount=followingcount, username=username)

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
        postlat = convertorads(postlat)#convert to rads
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
        baseids.append(row['id'])#adds all the posts youve Created so we can remove later
        if lat is not None and lng is not None:
            lnglatlist.append([lat,lng])#gets list of lists of longs and lats of each post you have posted

    #saved posts
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
    #liked posts end

    #location
    cursor = con.cursor()
    sql = "SELECT lat, lng FROM Accounts WHERE username = ?"  # go through every post and get lat lng of each
    cursor.execute(sql, (username,))
    lnglat4 = cursor.fetchone()
    if lnglat4 is not None:
        if lnglat4[0] is not None and lnglat4[1] is not None:
            lnglatlist.append([lnglat4[0],lnglat4[1]])
            geolocator = Nominatim(user_agent="web_site")
            latlng = str(lnglat4[0]) + ", " + str(lnglat4[1])
            location = geolocator.reverse(latlng, language='en') #gets the named location of your location from account settings
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
    cursor.execute(sql, (country,city, town, username ))
    for row in cursor.fetchall():
        inside.append(row[0])

    #end locaton


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



    #haversine formula to find posts close to ones we have positively interacted with
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
        for x in allpostsdict: # getting the lng lat of each post through a for loop
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
    #haversine end


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

    #inside is all the recommended posts
    #basids is all posts youve already seen
    #we obv want to remove ones youve already seen so we find them in "inside" and remove them

    #list of ids inside
    # pop
    allids = listofallpostids + listofallalbumids
    sortedpopids = sortpopularity(allids)
    sortedpopids = sortedpopids[:math.ceil(0.2 * len(sortedpopids))]  # gets top 20% most popular posts
    sucloop = 0
    totloop = 0
    while sucloop < 10 and totloop < 100:#10 times we select a random post from the top 20% of pop posts, (try 100 times to avoid infite loop)
        randnumber = random.randint(0, len(sortedpopids) - 1)
        if sortedpopids[randnumber] not in inside:
            inside.append(sortedpopids[randnumber])
            sucloop +=1
        else:
            totloop += 1
            pass
    # endpop

    #similar gender
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
    #finds accounts with similar age and gender
    cursor.execute(sql, (username,username,username,username))
    for row in cursor.fetchall():
        samegender.append(row[0])
    if len(samegender) < 5:
        inside += samegender
    else:
        for i in range(math.ceil(0.2 * len(samegender))):  #loops (20% of posts by users of same gender) times and gets random post
            randnumber = random.randint(0, len(samegender) - 1)
            if samegender[randnumber] not in inside:
                inside.append(samegender[randnumber])
    #gender stop

    # similar camera
    #get a list of all camera makes, and a list of all camera models
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
            if row[0] not in alluserpostids:#makes sure it isnt your post OBV hehe
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
    #similar camera stop

    #mutuals
    following = []
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT userreceive from friendrequests WHERE usersend = ? AND status = 2"#getting the people you follow
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
        AND Accounts.privacy = 'public'"""#getting the people they then follow privacy = 'public'
        cursor.execute(sql, (i,username))
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
    intersectfreq = sortdatetime(insidefreqmut)# able to use this func as not acc specifc to func, sorts it based on freq
    for i in intersectfreq:
        intersect.append(i[0])
    if len(intersect) > 5:
        intersect = intersect[:math.ceil(0.2 * len(intersect))]

    intersectposts = []
    for i in intersect:
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        sql = "SELECT id from posts WHERE user = ?"#get a few of their posts
        cursor.execute(sql, (i,))
        for row in cursor.fetchall():
            intersectposts.append(row[0])
    if len(intersectposts) > 2:
        intersectposts = intersectposts[:math.ceil(0.2 * len(intersectposts))]

    if len(intersectposts) < 5:
        inside += intersectposts
    else:
        for i in range(math.ceil(0.2 * len(intersectposts))):  #loops (20% of posts by users of same gender) times and gets random post
            randnumber = random.randint(0, len(intersectposts) - 1)
            if intersectposts[randnumber] not in inside:
                inside.append(intersectposts[randnumber])

    #mutuals stop
    #people loc
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
    #get your latlng ^
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

    for i in range(math.ceil(0.2 * len(closeaccountposts))):  #loops (20% of posts by users of same gender) times and gets random post
        randnumber = random.randint(0, len(closeaccountposts) - 1)
        if closeaccountposts[randnumber] not in inside:
            inside.append(closeaccountposts[randnumber])
    #people loc end
    insidetemp = inside
    for i in insidetemp:
        sql = "SELECT albumid FROM albums WHERE postid = ?"  # go through every post and get lat lng of each
        cursor.execute(sql, (i,))
        albumids = cursor.fetchone()
        try: #if it is not NULL
            inside.append(albumids[0])#get any albums the good posts are in
        except:
            pass
    intersect = []
    for i in inside:
        if i in baseids:
            intersect.append(i)#removes posts that shouldnt be shown (your own or already liked/saved)
    for i in intersect:
        inside.remove(i)


    insidefreq = {}
    for i in inside:#gets frequency of each post
        if i in insidefreq:
            insidefreq[i] += 1
        else:
            insidefreq[i] = 1
    insidefreq = sortdatetime(insidefreq)#able to use this func as not acc specifc to func, sorts it based on freq
    print(insidefreq) #things which are in the list multiple times means they are more relevant
    inside = []

    for i in insidefreq:
        inside.append(i[0])  # adds all the post ids (removing the datetime)
    inside = inside[::-1]#reverse to get the most relevant first (append adds to the end)
    listofall = listofallpostids + listofallalbumids
    if len(listofall) >= 1:#deals with if no posts
        minnum = math.ceil((len(listofall)*0.2))#gets the value that is 20% of all posts, this is how many we recommend (the min)
        totloop2 = 0
        while len(inside) < minnum and totloop2 < 100: #if the number of recommendation posts is < 20% of allposts (the min) then we add some random ones to fill it (#totloop < 100 to avoid infinte loop)
            for i in range(minnum - len(inside)):
                randnumber = random.randint(0, len(listofall) - 1)
                if listofall[randnumber] not in inside and listofall[randnumber] not in baseids:#make sure we dont dupe the random ones/add your ones
                    inside.append(listofall[randnumber])
            for i in inside:
                if i in listofdisids:#removes disliked post
                    inside.remove(i)
            totloop2 += 1
    else:
        inside = []

    return inside # a list of all post ids that are recommended, in order of how relevant they are

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
    return render_template("recommended.html", rows = postinfo, username = username, msg = msg)



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
                datetimedict[i] = formatdattimetotal  # adds the seconds value to a dictionary with the key being the post id (i)
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
        #only sort likes as if you have many likes and many dislikes, its got lots of interaction so must be popular

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
        if session['sortedpostids'] == []: #if filtered post is emptied than no filter is active so use all posts
            sortedpostids = sortdatetimefunc(listofpostids) # filtered set to false as default so no need to set again

        else:
            sortedpostids = session['sortedpostids']  # if there is a filter active then set filtered to true
            filtered = True

    else:
        sortedpostids = sortdatetimefunc(listofpostids) #else if it is there first time loggin on then use all posts
        session['sortedpostids'] = []




    if request.method == "POST":
        selected_option = request.form['selected_option']
        checkboxposts = request.form.get('posts')
        checkboxalbums = request.form.get('albums')
        if "unfilter" in request.form:
            session['sortedpostids'] = [] # so when the page is reloaded, it tells the bit above that no filter is set
            return redirect(url_for('listallposts'))

        if "filter" in request.form:
            filtered = True
            slidervalue = int(request.form['slidervalue'])
            insideposts = CheckWithinRadius(lnglatdict)

            for i in getallalbumids: #makes sure we incl albums (if a post is inside the circle and in an album, give the album too)
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



            if checkboxposts != None or checkboxalbums != None: # if at least one is clicked (slider could be)
                sortedpostids2 = []
                if checkboxalbums != None and checkboxposts == None: # if only albums is clicked (slider could be)
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


                elif checkboxposts != None and checkboxalbums == None: # if only posts is clicked (slider could be)
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

            elif checkboxposts == None and checkboxalbums == None: # if neither are clicked (slider could be)
                sortedpostids = insideposts
                session['sortedpostids'] = sortedpostids
                sortedpostids = sortdatetimefunc(sortedpostids)
            elif checkboxposts != None and checkboxalbums != None: # if both are clicked (slider could be)
                sortedpostids = insideposts
                session['sortedpostids'] = sortedpostids
                sortedpostids = sortdatetimefunc(sortedpostids)
            if checkboxposts == None and checkboxalbums == None and slidervalue == 0:# absolutely nothing selected
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


    return render_template("allposts.html", rows=postinfo, username=username,filtered = filtered, latlnglist=latlnglist, msg= msg)


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
    return render_template("friends.html", rows = rows, msg=msg)

@web_site.route('/account_settings', methods=['GET', 'POST'])
def account_settings():
    if "username" not in session:
        return redirect("/login")

    filename = "1024px-Cross_red_circle.svg.png"
    username = session["username"]

    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    sql = "SELECT * FROM Accounts WHERE username = ?"
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    con.commit()
    rows = cursor.fetchall()

    sql = "SELECT privacy FROM Accounts WHERE username = ?"
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    getprivacy = cursor.fetchone()
    getprivacy = getprivacy[0]

    genders = ["None","Male", "Female", "Other"]

    if request.method == "POST":
        lat = session.get('lat')
        lng = session.get('lng')
        clicked = session.get('clicked')
        if "cancel" in request.form:
            session['lat'] = 0
            session['lng'] = 0
            return redirect('account')

        description = request.form["description"]
        description = moderate(description)
        dob = request.form["dob"]
        username_update = request.form["Username"]
        checkbox_privacy = request.form.get('privacy')
        checkbox_resetpfp = request.form.get('resetpfp')
        gender = request.form['gender']
        oldpassword = request.form["oldpassword"]
        newpassword = request.form["newpassword"]
        con = sqlite3.connect('database.db')
        sql = "SELECT username FROM Accounts WHERE username = ?"
        cursor = con.cursor()
        cursor.execute(sql, (username_update,))
        getusername = cursor.fetchone()
        sql = "UPDATE Accounts SET description = ? WHERE username = ?"  # updates accounts
        cursor = con.cursor()
        cursor.execute(sql, (description, username))
        con.commit()

        sql = "UPDATE Accounts SET dob = ? WHERE username = ?"
        cursor = con.cursor()
        cursor.execute(sql, (dob, username))
        con.commit()

        sql = "UPDATE Accounts SET gender = ? WHERE username = ?"
        cursor = con.cursor()
        cursor.execute(sql, (gender, username))
        con.commit()

        if lat != 0 and lng != 0 and clicked:
            sql = "UPDATE Accounts SET lat = ?, lng = ? WHERE username = ?"
            cursor = con.cursor()
            cursor.execute(sql, (lat,lng, username,))
            con.commit()

        randfilename = randomfilename(os.path.join(web_site.root_path, 'static', 'ProfilePictures'))
        photo = request.files['photo']
        if photo.filename != "":
            filename = randfilename + "_" + photo.filename
            try:
                photo.save(os.path.join(web_site.root_path, 'static', 'ProfilePictures', filename))
                photo_path = os.path.join(web_site.root_path, 'static', 'ProfilePictures', filename)
                metadata = get_metadata(photo_path)#good way to test if it is acc a photo

                con = sqlite3.connect('database.db')
                sql = "SELECT pfp FROM Accounts WHERE username = ?"
                cursor = con.cursor()
                cursor.execute(sql, (username,))
                getoldfilename = cursor.fetchone()
                getoldfilename = getoldfilename[0]
                if getoldfilename != "blank-profile-picture-973460_960_720.jpg":
                    os.remove(os.path.join(web_site.root_path, 'static', 'ProfilePictures', getoldfilename))  # deletes the file


                sql = "UPDATE Accounts SET pfp = ? WHERE username = ?"
                cursor = con.cursor()
                cursor.execute(sql, (filename, username))
                con.commit()

            except:
                os.remove(os.path.join(web_site.root_path, 'static', 'ProfilePictures', filename))





        if username_update != username:
            if getusername is None:  # checks if the username is unique
                if username_update != "":
                    if " " not in username_update and len(username_update) >= 3 and len(username_update) <= 15:
                        con = sqlite3.connect('database.db')
                        sql = "UPDATE Accounts SET username = ? WHERE username = ?"  # updates accounts
                        cursor = con.cursor()
                        cursor.execute(sql, (username_update, username))
                        con.commit()
                        session["username"] = username_update
                        sql = "UPDATE Posts SET user = ? WHERE user = ?"
                        cursor = con.cursor()
                        cursor.execute(sql, (username_update, username))
                        con.commit()
                        username = username_update
        if checkbox_privacy == "on":
            con = sqlite3.connect('database.db')
            sql = "UPDATE Accounts SET privacy = 'private' WHERE username = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = "UPDATE Posts SET privacy = 'private' WHERE user = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()
        if checkbox_privacy is None:
            con = sqlite3.connect('database.db')
            sql = "UPDATE Accounts SET privacy = 'public' WHERE username = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = "UPDATE Posts SET privacy = 'public' WHERE user = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()
        if checkbox_resetpfp == "on":
            con = sqlite3.connect('database.db')
            sql = "UPDATE Accounts SET pfp = ? WHERE username = ?"
            cursor = con.cursor()
            cursor.execute(sql, ("blank-profile-picture-973460_960_720.jpg", username))
            con.commit()

        con = sqlite3.connect('database.db')
        sql = "SELECT password FROM Accounts WHERE username = ?"
        cursor = con.cursor()
        cursor.execute(sql, (username,))
        getpassword = cursor.fetchone()
        getpassword = getpassword[0]
        critera = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!?*%@$&]).{8,}$")



        if bool(critera.match(newpassword)):#fits critera add ticks if they match
            newpassword = hash(newpassword)
            oldpassword = hash(oldpassword)
            if oldpassword != "" and getpassword != "":
                if oldpassword == getpassword:
                    con = sqlite3.connect('database.db')
                    sql = "UPDATE Accounts SET password = ? WHERE username = ?"
                    cursor = con.cursor()
                    cursor.execute(sql, (newpassword,username))
                    con.commit()
        session['lat'] = 0
        session['lng'] = 0
        return redirect("account")

    return render_template("account_settings.html", rows=rows, getprivacy=getprivacy,filename = filename, genders=genders)


@web_site.route('/logout')
def logout():
    try:
        username = session["username"]
        session.pop('username', None)
    except:
        return redirect("/login")
    return render_template("logout.html", username=username)


@web_site.route('/viewpost', methods=['GET', 'POST'])
def viewpost():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    postid = request.args.get('id')
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    sql = "SELECT privacy,user FROM Posts WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
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




    con.row_factory = sqlite3.Row
    sql = "SELECT * FROM Posts WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    rows = cursor.fetchall()
    albumtitles = []
    try:
        con = sqlite3.connect('database.db') #get the album id if its in one
        con.row_factory = sqlite3.Row
        sql = """SELECT Posts.text, Posts.id
                FROM Posts
                JOIN albums ON Posts.id = albums.albumid
                WHERE albums.postid = ?"""
        cursor = con.cursor()
        cursor.execute(sql, (postid,))
        allalbums = cursor.fetchall()
        for album in allalbums:
            dict = {}
            dict["title"] = album[0]
            dict["id"] = album[1]
            albumtitles.append(dict)
    except:
        albumtitles = ""
        pass

    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    sql = "SELECT * FROM photodetails WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    rows2 = cursor.fetchall()

    sql = "Select datetime FROM photodetails WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    datetimeup = cursor.fetchone()
    datetimeup = datetimeup[0]
    date = datetimeup[:10]
    time = datetimeup[11:]

    con.row_factory = sqlite3.Row
    cursor3 = con.cursor()
    sql3 = "SELECT * FROM Posts WHERE album = 'True' AND user = ?"
    cursor3.execute(sql3, (username,))
    rows3 = cursor3.fetchall()

    sql = "SELECT savedpostid FROM savedposts WHERE savedpostid = ? and username = ?"
    cursor = con.cursor()
    cursor.execute(sql, (postid, username))
    getsavedid = cursor.fetchone()
    if getsavedid is not None:
        checksaved = True
    else:
        checksaved = False

    con = sqlite3.connect('database.db')
    sql = "SELECT user FROM Posts WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    postgetuser = cursor.fetchone()
    postuser = postgetuser[0]

    if request.method == "POST":
        if "add" in request.form:
            selected_option = request.form['selected_option']
            if selected_option != "none":
                con = sqlite3.connect('database.db')
                sql = "SELECT id FROM Posts WHERE text = ? AND user = ? AND album = 'True'"
                cursor = con.cursor()
                cursor.execute(sql, (selected_option, username,))
                con.commit()
                getalbumid = cursor.fetchone()
                getalbumid = getalbumid[0]

                sql = "SELECT albumid FROM albums WHERE postid = ?"
                cursor = con.cursor()
                cursor.execute(sql, (postid,))
                con.commit()
                postinalbumid = cursor.fetchone()
                if postinalbumid != None:
                    postinalbumid = postinalbumid[0]
                if postinalbumid != getalbumid or postinalbumid == None:
                    con = sqlite3.connect('database.db')

                    sql = "INSERT INTO albums(albumid, postid, user) VALUES(?,?,?)"
                    cursor = con.cursor()
                    cursor.execute(sql, (getalbumid, postid, username,))
                    con.commit()
                    updatealbumlocation(getalbumid)
                    return redirect(url_for('viewpost', id=postid))

        con = sqlite3.connect('database.db')
        sql = "SELECT usersliked FROM Likes WHERE usersliked = ? AND id = ?"
        cursor = con.cursor()
        cursor.execute(sql, (username, postid))
        getusersliked = cursor.fetchone()

        sql = "SELECT usersdisliked FROM Dislikes WHERE usersdisliked = ? AND id = ?"
        cursor = con.cursor()
        cursor.execute(sql, (username, postid))
        getusersdisliked = cursor.fetchone()

        # find it
        sql = "SELECT likes FROM Posts WHERE id = ?"
        cursor = con.cursor()
        cursor.execute(sql, (postid,))
        getlikecount = cursor.fetchone()
        likecount = int(getlikecount[0])

        sql = "SELECT dislikes FROM Posts WHERE id = ?"
        cursor = con.cursor()
        cursor.execute(sql, (postid,))
        getdislikecount = cursor.fetchone()
        dislikecount = int(getdislikecount[0])

        if "Like" in request.form:
            datetimenow = datetime.now()
            formattedtime = datetimenow.strftime("%d/%m/%y %H:%M:%S")
            if getusersliked is None:
                if getusersdisliked is None:

                    likecount += 1
                    # update it
                    sql = "UPDATE Posts SET likes = ? WHERE id = ?"
                    cursor = con.cursor()
                    cursor.execute(sql, (likecount, postid,))
                    con.commit()

                    con = sqlite3.connect('database.db')
                    sql = "INSERT INTO Likes(usersliked, id,timesent) VALUES(?,?,?)"
                    cursor = con.cursor()
                    cursor.execute(sql, (username, postid,formattedtime))
                    con.commit()
                    return redirect(url_for('viewpost', id=postid))
                elif getusersdisliked is not None:
                    dislikecount -= 1
                    likecount += 1
                    con = sqlite3.connect('database.db')
                    sql = "UPDATE Posts SET likes = ? WHERE id = ?"
                    cursor = con.cursor()
                    cursor.execute(sql, (likecount, postid,))
                    con.commit()

                    sql = "UPDATE Posts SET dislikes = ? WHERE id = ?"
                    cursor = con.cursor()
                    cursor.execute(sql, (dislikecount, postid,))
                    con.commit()

                    sql = "DELETE FROM Dislikes WHERE usersdisliked = ? and id = ?"
                    cursor = con.cursor()
                    cursor.execute(sql, (username, postid))
                    con.commit()

                    sql = "INSERT INTO Likes(usersliked, id,timesent) VALUES(?,?,?)"
                    cursor = con.cursor()
                    cursor.execute(sql, (username, postid,formattedtime))
                    con.commit()
                    return redirect(url_for('viewpost', id=postid))

            elif getusersliked is not None:
                likecount -= 1
                con = sqlite3.connect('database.db')
                sql = "UPDATE Posts SET likes = ? WHERE id = ?"
                cursor = con.cursor()
                cursor.execute(sql, (likecount, postid,))
                con.commit()
                sql = "DELETE FROM Likes WHERE usersliked = ? and id = ?"
                cursor = con.cursor()
                cursor.execute(sql, (username, postid))
                con.commit()
                return redirect(url_for('viewpost', id=postid))

        elif "Dislike" in request.form:
            if getusersliked is None:
                if getusersdisliked is None:

                    dislikecount += 1
                    # update it
                    sql = "UPDATE Posts SET dislikes = ? WHERE id = ?"
                    cursor = con.cursor()
                    cursor.execute(sql, (dislikecount, postid,))
                    con.commit()

                    con = sqlite3.connect('database.db')
                    sql = "INSERT INTO Dislikes(usersdisliked, id) VALUES(?,?)"
                    cursor = con.cursor()
                    cursor.execute(sql, (username, postid))
                    con.commit()
                    return redirect(url_for('viewpost', id=postid))
                elif getusersdisliked is not None:
                    dislikecount -= 1
                    con = sqlite3.connect('database.db')
                    sql = "UPDATE Posts SET dislikes = ? WHERE id = ?"
                    cursor = con.cursor()
                    cursor.execute(sql, (dislikecount, postid,))
                    con.commit()


                    sql = "DELETE FROM Dislikes WHERE usersdisliked = ? and id = ?"
                    cursor = con.cursor()
                    cursor.execute(sql, (username, postid))
                    con.commit()
                    return redirect(url_for('viewpost', id=postid))
            elif getusersliked is not None:
                dislikecount += 1
                likecount -= 1
                con = sqlite3.connect('database.db')
                sql = "UPDATE Posts SET likes = ? WHERE id = ?"
                cursor = con.cursor()
                cursor.execute(sql, (likecount, postid,))
                con.commit()

                sql = "UPDATE Posts SET dislikes = ? WHERE id = ?"
                cursor = con.cursor()
                cursor.execute(sql, (dislikecount, postid,))
                con.commit()

                sql = "DELETE FROM Likes WHERE usersliked = ? and id = ?"
                cursor = con.cursor()
                cursor.execute(sql, (username, postid))
                con.commit()

                sql = "INSERT INTO Dislikes(usersdisliked, id) VALUES(?,?)"
                cursor = con.cursor()
                cursor.execute(sql, (username, postid))
                con.commit()
                return redirect(url_for('viewpost', id=postid))
        if "save" in request.form:
            if checksaved == False:
                con = sqlite3.connect('database.db')
                sql = "INSERT INTO savedposts(savedpostid, username) VALUES(?, ?)"
                cursor = con.cursor()
                cursor.execute(sql, (postid, username))
                con.commit()
                return redirect(url_for('viewpost', id=postid))
        elif "unsave" in request.form:
            con = sqlite3.connect('database.db')
            sql = "DELETE FROM savedposts WHERE savedpostid = ? AND username = ?"
            cursor = con.cursor()
            cursor.execute(sql, (postid, username))
            con.commit()
            return redirect(url_for('viewpost', id=postid))

    return render_template("viewpost.html", postuser=postuser, rows=rows, username=username, checksaved=checksaved,rows2=rows2, rows3=rows3, albumtitles = albumtitles, date = date, time = time)


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
        desc = row2[0] #if this causes an error it means the user doesnt exist
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
                cursor.execute(sql, (usernamesend, username,formattedtime))
                con.commit()
                return redirect(url_for('viewaccount', id=username))
            else:
                con = sqlite3.connect('database.db')
                cursor = con.cursor()
                sql = "UPDATE friendrequests SET usersend = ?, userreceive = ?, status = 1, timesent = ? WHERE usersend = ? AND userreceive = ?"#update where
                cursor.execute(sql, (usernamesend, username,formattedtime,usernamesend, username))
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
            cursor.execute(sql, (formattedtime,username, usernamesend,))
            con.commit()

            return redirect(url_for('viewaccount', id=username))

    return render_template("viewaccount.html", rows=rows, username=username, desc=desc, age=ageget,
                           getstatusclean=getstatusclean, getprivacy=getprivacy,gender = gender, pfp = pfp,
                           postcount=postcount, albumcount=albumcount,followercount=followercount,followingcount=followingcount)



@web_site.route('/activity', methods=['GET', 'POST'])
def activity():
    if "username" not in session:
        return redirect("/login")

    msg = ""
    username = session["username"]
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = """SELECT Likes.usersliked, Likes.id, Likes.timesent
       FROM Likes
       JOIN Posts ON Likes.id = Posts.id
       WHERE Posts.user = ?"""
    cursor.execute(sql, (username,))
    rows = cursor.fetchall()
    newrows = []
    for row in rows:
        rowdict = dict(row)
        rowdict['type'] = 'like'
        newrows.append(rowdict)

    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = """SELECT friendrequests.usersend, friendrequests.timesent
           FROM friendrequests
           WHERE friendrequests.userreceive = ? AND status = 2"""
    cursor.execute(sql, (username,))
    rows2 = cursor.fetchall()
    newrows2 = []
    for row in rows2:
        rowdict = dict(row)
        rowdict['type'] = 'follower'
        newrows2.append(rowdict)

    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT * FROM friendrequests WHERE userreceive = ? AND status = 1"
    cursor.execute(sql, (username,))
    rows3 = cursor.fetchall()
    newrows3 = []
    for row in rows3:
        rowdict = dict(row)
        rowdict['type'] = 'request'
        newrows3.append(rowdict)

    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT * FROM friendrequests WHERE usersend = ? AND status = 2"
    cursor.execute(sql, (username,))
    rows4 = cursor.fetchall()
    newrows4 = []
    for row in rows4:
        rowdict = dict(row)
        rowdict['type'] = 'following'
        newrows4.append(rowdict)

    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = "SELECT * FROM friendrequests WHERE usersend = ? AND status = 1"
    cursor.execute(sql, (username,))
    rows5 = cursor.fetchall()
    newrows5 = []
    for row in rows5:
        rowdict = dict(row)
        rowdict['type'] = 'requestfollowing'
        newrows5.append(rowdict)


    newrows += newrows2
    newrows += newrows3
    newrows += newrows4
    newrows += newrows5

    rowsinsec = []
    for row in newrows:
        getdatetime = datetime.strptime(row["timesent"], "%d/%m/%y %H:%M:%S") #converts to known format
        datetimenow = datetime.now() #Gets time now
        datetimedif = datetimenow - getdatetime #finds dif
        timedif = datetimedif.total_seconds() #converts dif to s
        rowdict = dict(row) #sets var to old dict of row
        rowdict['timedif'] = timedif #adds sec dif to dict
        rowsinsec.append(rowdict) #appends to list

    sortedrows = sorted(rowsinsec, key=lambda x: x.get('timedif'))

    if sortedrows == []:
        msg = "No recent activity"
    return render_template("activity.html", rows=sortedrows, username=username,msg=msg)



@web_site.route('/acceptignore', methods=['GET', 'POST'])
def acceptignore():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    usernamesend = request.args.get('id')

    if request.method == "POST":
        if "accept" in request.form:
            datetimenow = datetime.now()
            formattedtime = datetimenow.strftime("%d/%m/%y %H:%M:%S")
            con = sqlite3.connect('database.db')
            cursor = con.cursor()
            sql = "UPDATE friendrequests SET status = 2,timesent = ? WHERE userreceive = ? AND usersend = ?"#set time here
            cursor.execute(sql, (formattedtime,username, usernamesend))
            con.commit()
            return redirect('/activity')
        elif "ignore" in request.form:
            con = sqlite3.connect('database.db')
            cursor = con.cursor()
            sql = "DELETE FROM friendrequests WHERE userreceive = ? AND usersend = ?"
            cursor.execute(sql, (username, usernamesend))
            con.commit()
            return redirect('/activity')
    return render_template("acceptignore.html")


@web_site.route('/followinglist')
def followinglist():
    if "username" not in session:
        return redirect("/login")

    msg = ""
    username = session["username"]
    viewusername = request.args.get('id')
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    sql = "SELECT * FROM friendrequests WHERE usersend = ? AND status = 2"
    cursor = con.cursor()
    cursor.execute(sql, (viewusername,))
    rows = cursor.fetchall()
    usernames = []

    for row in rows:
        usernames.append(row['userreceive'])
    usernames = mergesort(usernames)

    #sorts it based of the index of x.lower() in list "usernames"
    rows = sorted(rows, key=lambda x: usernames.index(x["userreceive"].lower()))

    if rows == []:
        msg = "No followers found"

    return render_template("followinglist.html", rows=rows,username=username, msg= msg)


def mergesort(usernames):
    username2 = []

    for i in usernames:
        newitem = ""
        for x in i:
            newitem += x.lower()#we need to convert to lower as it uses ascii so capitals can mess it up (s > T)
        username2.append(newitem)
    usernames = username2

    #if less than one then obv we cant sort
    if len(usernames) <= 1:
        return usernames
    #if greater than 1, all good so we split in two and sort each half
    middle = len(usernames) // 2
    halfone = usernames[:middle]
    halftwo = usernames[middle:]

    halfone = mergesort(halfone)#recursion
    halftwo = mergesort(halftwo)#recursion

    #merge the two halves together

    index1 = 0
    index2 = 0
    output = []
    while index1 < len(halfone) and index2 < len(halftwo):#while the end of each half has not been reached
        if halfone[index1] <= halftwo[index2]:#if half one is less than half two, half one gets added first
            output.append(halfone[index1])
            index1 += 1#halfone at that index has been added, so we move to the next one
        else:# else half two must be smaller, so half to gets added before
            output.append(halftwo[index2])
            index2 += 1#halftwo at that index has been added, so we move to the next one

    #add remaining stuff
    output += halfone[index1:]
    output += halftwo[index2:]

    return output


@web_site.route('/removefollowing', methods=['GET', 'POST'])
def removefollowing():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    follower = request.args.get('id')
    if "remove" in request.form:
        con = sqlite3.connect('database.db')
        cursor = con.cursor()
        sql = "DELETE FROM friendrequests WHERE usersend = ? AND userreceive = ?"
        cursor.execute(sql, (username, follower))
        con.commit()
        return redirect('/followinglist')
    return render_template("removefollowing.html", follower=follower)


@web_site.route('/followerlist')
def followerlist():
    if "username" not in session:
        return redirect("/login")

    msg = ""
    username = session["username"]
    viewusername = request.args.get('id')
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    sql = "SELECT * FROM friendrequests WHERE userreceive = ? AND status = 2"
    cursor = con.cursor()
    cursor.execute(sql, (viewusername,))
    rows = cursor.fetchall()

    usernames = []

    for row in rows:
        usernames.append(row['usersend'])
    usernames = mergesort(usernames)

    #sorts it based of the index of x.lower() in list "usernames"
    rows = sorted(rows, key=lambda x: usernames.index(x["usersend"].lower()))

    if rows == []:
        msg = "No followers...yet?"
    return render_template("followerlist.html", rows=rows,username=username, msg = msg)


@web_site.route('/removefollower', methods=['GET', 'POST'])
def removefollower():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    follower = request.args.get('id')
    if "remove" in request.form:
        con = sqlite3.connect('database.db')
        cursor = con.cursor()
        sql = "DELETE FROM friendrequests WHERE userreceive = ? AND usersend = ?"
        cursor.execute(sql, (username, follower))
        con.commit()
        return redirect('/followerlist')
    return render_template("removefollower.html", follower=follower)



@web_site.route('/editpost', methods=['GET', 'POST'])
def editpost():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    postid = request.args.get('id')
    con = sqlite3.connect('database.db')

    # get the album id if its in one

    sql = "SELECT user FROM Posts WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    getuser = cursor.fetchone()
    if not getuser:
        session['lat'] = 0
        session['lng'] = 0
        return render_template('404.html')
    if getuser[0] != username:
        session['lat'] = 0
        session['lng'] = 0
        return render_template('404.html')


    con.row_factory = sqlite3.Row
    sql = "SELECT * FROM Posts WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    rows = cursor.fetchall()

    con.row_factory = sqlite3.Row
    sql = "SELECT * FROM photodetails WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    rows2 = cursor.fetchall()

    sql = "Select datetime FROM photodetails WHERE id = ?"
    cursor = con.cursor()
    cursor.execute(sql, (postid,))
    datetimeup = cursor.fetchone()
    datetimeup = datetimeup[0]
    date = datetimeup[:10]
    time = datetimeup[11:]

    if request.method == "POST":
        lat = session.get('lat')
        lng = session.get('lng')
        if "cancel" in request.form:
            session['lat'] = 0
            session['lng'] = 0
            return redirect(url_for('viewpost', id=postid))
        con = sqlite3.connect('database.db')
        description = request.form["description"]
        description = moderate(description)
        text = request.form["text"]
        text = moderate(text)
        if text == "":
            text = "Untitled"
        if description == "":
            description = "Untitled"
        datetimenow = datetime.now()
        formattedtime = datetimenow.strftime("%d/%m/%y %H:%M")
        sql = "UPDATE Posts SET descr = ?, text = ?, timeposted = ?, lat = ?, lng = ? WHERE id = ?"
        cursor = con.cursor()
        cursor.execute(sql, (description, text, formattedtime, lat, lng, postid))
        con.commit()

        GetNamedLocation(lat, lng, postid)

        make = request.form["make"]
        model = request.form["model"]

        date = request.form["date"]
        time = request.form["time"]
        if date != "" and time != "":
            metadatadatetime = str(date) + " " + str(time)
        elif date != "" and time == "":
            metadatadatetime = str(date) + " " + "12:00"
        else:
            metadatadatetime = "N/A"
        ISO = request.form["ISO"]
        LensModel = request.form["lensmodel"]
        FNumber = request.form["fstop"]
        ExposureTime = request.form["shutterspeed"]
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

        con = sqlite3.connect('database.db')
        sql = "UPDATE photodetails SET make = ?, model = ?, datetime = ?, ISO = ?, lensmodel = ?, fstop = ?, shutterspeed = ? WHERE id = ?"
        cursor = con.cursor()
        cursor.execute(sql, (make, model, metadatadatetime, ISO, LensModel, FNumber, ExposureTime, postid,))
        con.commit()

        listofalbumids = []
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        sql = "SELECT albumid FROM albums WHERE postid = ?"  # upadtes all the albums this post is in
        cursor.execute(sql, (postid,))
        allids = cursor.fetchall()
        for row in allids:
            listofalbumids.append(row[0])

        for i in listofalbumids:
            updatealbumlocation(i)
        session['lat'] = 0
        session['lng'] = 0
        return redirect(url_for('viewpost', id=postid))
    return render_template("editpost.html", rows=rows, postid=postid, rows2=rows2, date = date, time = time)



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
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    msg = ""
    con = sqlite3.connect('database.db')
    sql = "Select password FROM Accounts WHERE username = ?"
    cursor = con.cursor()
    cursor.execute(sql, (username,))
    getpassword = cursor.fetchone()
    getpassword = getpassword[0]
    if request.method == "POST":
        password = request.form["password"]
        if getpassword == hash(password):
            sql = "Select pfp FROM Accounts WHERE username = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            getfilename = cursor.fetchone()
            getfilename = getfilename[0]
            if getfilename != "blank-profile-picture-973460_960_720.jpg":
                os.remove(os.path.join(web_site.root_path, 'static', 'ProfilePictures', getfilename))  # deletes the file

            con.row_factory = sqlite3.Row
            sql = "SELECT * FROM Posts WHERE user = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            rows = cursor.fetchall()
            for row in rows:
                filename = row["filename"]
                if filename != "7da6b012d99beac0c7eff0949b27b7e6.png":
                    os.remove(os.path.join(web_site.root_path, 'static', 'UploadedPhotos', filename))


            sql = "DELETE FROM tempphotos WHERE user = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = "DELETE FROM savedposts WHERE username = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            #update like and dislike counts of the stuff we have liked/disliked
            con.row_factory = sqlite3.Row
            sql = "Select id FROM Likes WHERE usersliked = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            rows = cursor.fetchall()
            for row in rows:
                sql = "Select likes FROM Posts WHERE id = ?"
                cursor = con.cursor()
                cursor.execute(sql, (row[0],))
                getlikes = cursor.fetchone()
                getlikes = getlikes[0]
                getlikes -= 1

                sql = "UPDATE Posts SET likes = ? WHERE id = ?"
                cursor = con.cursor()
                cursor.execute(sql, (getlikes, row[0],))
                con.commit()

            con.row_factory = sqlite3.Row
            sql = "Select id FROM Dislikes WHERE usersdisliked = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            rows = cursor.fetchall()
            for row in rows:
                sql = "Select dislikes FROM Posts WHERE id = ?"
                cursor = con.cursor()
                cursor.execute(sql, (row[0],))
                getdislikes = cursor.fetchone()
                getdislikes = getdislikes[0]
                getdislikes -= 1

                sql = "UPDATE Posts SET dislikes = ? WHERE id = ?"
                cursor = con.cursor()
                cursor.execute(sql, (getdislikes, row[0],))
                con.commit()
            # END OF update like and dislike counts of the stuff we have liked/disliked

            sql = "DELETE FROM Likes WHERE usersliked = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()
            #Leaves the like count of a post but i like it since it a post keeps its interaction and is further recommended (if it deserves)
            #just cuz you delete your account doesnt mean your opinion wasnt valid...
            #however it means you could create, like, delete

            sql = "DELETE FROM Dislikes WHERE usersdisliked = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()


            sql = "DELETE FROM friendrequests WHERE usersend = ? OR userreceive = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,username,))
            con.commit()

            sql = """DELETE FROM Likes
            WHERE id IN (SELECT id FROM Posts WHERE user = ?)"""
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = """DELETE FROM Dislikes
            WHERE id IN (SELECT id FROM Posts WHERE user = ?)"""
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = """DELETE FROM albums
            WHERE albumid IN (SELECT id FROM Posts WHERE user = ?)"""
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = """DELETE FROM savedposts
                        WHERE savedpostid IN (SELECT id FROM Posts WHERE user = ?)"""
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = """DELETE FROM photodetails
            WHERE id IN (SELECT id FROM Posts WHERE user = ?)"""
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = """DELETE FROM Posts
            where user = ?"""
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()

            sql = "DELETE FROM Accounts WHERE username = ?"
            cursor = con.cursor()
            cursor.execute(sql, (username,))
            con.commit()
            if "username" in session and session["username"] == username:
                del session["username"]
            return redirect("/Index")
        else:
            msg = "Incorrect Password"


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
    if "username" not in session:
        return redirect("/login")

    msg = ""
    username = session["username"]
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    sql = """SELECT Posts.*, Accounts.pfp
    FROM Posts
    JOIN Accounts ON Accounts.username = Posts.user
    LEFT JOIN savedposts ON savedposts.savedpostid = Posts.id
    WHERE savedposts.username = ?"""
    cursor.execute(sql, (username,))
    rows = cursor.fetchall()
    rows = rows[::-1]

    if rows == []:
        msg = "No saved posts found"
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



@web_site.route('/ajaxsearchposts/<search>')
def ajaxsearchposts(search):
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
    cursor.execute(sql, (username,'%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%','%'+search+'%','%'+search+'%','%'+search+'%',))
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
    cursor.execute(sql,('%'+search+'%',))
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

    return render_template('ajaxsearchposts.html', rows = newrows, username=username,msg=msg )

web_site.run(host='0.0.0.0', port=8080)
