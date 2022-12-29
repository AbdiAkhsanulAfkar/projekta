from flask import Flask, request, make_response, render_template, url_for,session, request, abort, jsonify, redirect, flash
from flaskext.mysql import MySQL
import os
import sys
from gevent.pywsgi import WSGIServer
from functools import wraps
from werkzeug.utils import secure_filename
import json
import cv2
import base64
import os
import numpy as np
import matplotlib.pyplot as plt
from tensorflow import keras
import tensorflow as tf
import csv
from pyfirmata import Arduino, SERVO, util
import glob
from datetime import datetime
from skimage import io

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = 'edomphbm_jundix'
app.config['MYSQL_DATABASE_PASSWORD'] = '!ey{Z,,3iMe^'
app.config['MYSQL_DATABASE_DB'] = 'edomphbm_db_projek_jundix'
app.config['SECRET_KEY'] = 'thisisasecret'

PHOTO_FOLDER = '/flask/static/upload'
UPLOAD_FOLDER = 'static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PHOTO_FOLDER'] = PHOTO_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

@app.errorhandler(500)
def internal_server_error(e):
    # note that we set the 500 status explicitly
    return render_template('ulangPlat.html'), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

mysql = MySQL()
mysql.init_app(app)

@app.after_request
def add_header(response):
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
@app.route('/login' ,methods=['POST','GET'])
def login():
    status = True
    if request.method == 'POST':
        user = request.form["user"]
        pwd = request.form["pwd"]
        cursor = mysql.get_db().cursor()
        cursor.execute("select * from user where username=%s and password=%s", (user, pwd))
        data = cursor.fetchone()
        if data:
           session['logged_in'] = True
           session['username'] = data[1]
           flash('Login Successfully', 'success')
           return redirect('home')
        else:
           flash('Invalid Login. Try Again', 'danger')
    return render_template('login.html')
    
def is_logged_in(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return f(*args,**kwargs)
		else:
			flash('Unauthorized, Please Login','danger')
			return redirect(url_for('login'))
	return wrap

@app.route('/home')
@is_logged_in
def home():
    hasil = []
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT * FROM owner")
    result = cursor.fetchall()
    for data in result:
        hasil.append(data)
    cursor.close()
    return render_template('home.html', hasil=result)
    
@app.route("/logout")
def logout():
	session.clear()
	flash('You are now logged out','success')
	return redirect('login')
	
@app.route("/bypass")
def bypass():
	return render_template('bypass.html')
	
@app.route("/bypassbuka", methods=['POST', 'GET'])
def bypassbuka():
    cursor = mysql.get_db().cursor()
    cursor.execute('''UPDATE servo SET servo = 180 WHERE id=1''')
    mysql.get_db().commit()
    cursor.close()
    return render_template('bypasstutup.html')

@app.route("/bypasstutup", methods=['POST', 'GET'])
def bypasstutup():
    cursor = mysql.get_db().cursor()
    cursor.execute('''UPDATE servo SET servo = 0 WHERE id=1''')
    mysql.get_db().commit()
    cursor.close()
    return redirect('bypass')

@app.route('/add')
def add():
    return render_template('adddata.html')
    
@app.route('/db', methods=['POST', 'GET'])
def db():
    if request.method == 'POST':
        id = 0
        nama = request.form['nama']
        alamat = request.form['alamat']
        jabatan = request.form['jabatan']
        jenis = request.form['jenis']
        merk = request.form['merk']
        tipe = request.form['tipe']
        warna = request.form['warna']
        plat = request.form['plat']
        no = request.form['no']
        foto = 'foto'
        cursor = mysql.get_db().cursor()
        cursor.execute('''INSERT INTO owner (id, nama, alamat, jabatan, jenis, merk, tipe, warna, plat, no_telp, foto)  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', (id, nama, alamat, jabatan, jenis, merk, tipe, warna, plat, no,foto))
        #cursor.execute('''INSERT INTO db_coba (id, nama) VALUES(%s, %s)''',(id, nama))
        mysql.get_db().commit()
        cursor.close()
        return redirect('addphoto')

@app.route('/addphoto', methods=['POST', 'GET'])
def addphoto():
    return render_template("addphoto.html")
    
@app.route('/savedata', methods=['POST', 'GET'])
def savedata():
    if request.method == 'POST':
        image = request.form['mydata']
        img_binary = base64.b64decode(image)
        img_jpg = np.frombuffer(img_binary, dtype=np.uint8)
        img = cv2.imdecode(img_jpg, cv2.IMREAD_ANYCOLOR)
        #print(img)
        #image_file = "static/dataset/source/0002.jpg"
        now = datetime.now()
        current_time = now.strftime("%d_%m_%Y_%H_%M_%S")
        image_file = 'static/upload/img_%s.jpg' % current_time
        img_upload = 'img_%s.jpg' % current_time
        # image_file = "C:/Users/user/Videos/endend/app/static/dataset/img0000.jpg "
        cv2.imwrite(image_file, img)
        cursor = mysql.get_db().cursor()
        cursor.execute('''UPDATE owner SET foto=%s WHERE id=(SELECT max(id) FROM owner)''',(img_upload))
        mysql.get_db().commit()
        cursor.close()
    return redirect('home')
        
@app.route('/detail/<id>')
def detail(id):
    cur = mysql.get_db().cursor()
    cur2 = mysql.get_db().cursor()
    cur.execute('SELECT * FROM owner WHERE id=%s', (id,))
    cur2.execute('SELECT foto FROM owner WHERE id=%s', (id,))
    result = cur.fetchall()
    result2 = cur2.fetchall()
    s = json.dumps(result2)
    x = s.replace("(", "")
    x = x.replace(")", "")
    x = x.replace("[", "")
    x = x.replace("]", "")
    x = x.replace('"', '')
    fix = x.replace(",", "")

    fixfix = os.path.join(app.config['PHOTO_FOLDER'], fix)
    return render_template('detail.html', detail=result, foto=fixfix, result2=fix)
    
@app.route('/update/<id>',  methods=['POST', 'GET'])
def update(id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM owner WHERE id=%s', (id,))
    result = cursor.fetchall()
    return render_template('update.html', data=result)
    
@app.route('/updatedata', methods=['POST'])
def updatedata():
        id = request.form['id']
        alamat = request.form['alamat']
        jabatan = request.form['jabatan']
        jenis = request.form['jenis']
        merk = request.form['merk']
        tipe = request.form['tipe']
        warna = request.form['warna']
        plat = request.form['plat']
        no = request.form['no']
        cursor = mysql.get_db().cursor()
        cursor.execute('''UPDATE owner SET alamat=%s, jabatan=%s, jenis=%s,merk=%s,tipe=%s, warna=%s,plat=%s, no_telp=%s WHERE id=%s''',(alamat,jabatan,jenis,merk,tipe, warna,plat, no, id,))
        mysql.get_db().commit()
        cursor.close()
        return redirect('home')
        
@app.route('/delete/<id>')
def delete(id):
    cur = mysql.get_db().cursor()
    cur.execute('DELETE FROM owner WHERE id=%s', (id,))
    mysql.get_db().commit()
    cur.close()
    return redirect(url_for('home'))
    
@app.route('/identify')
def identify():
    return render_template('capture.html')
    
@app.route('/capture_img', methods=['POST'])
def capture_img():
    if request.method == 'POST':
        path = r"static/dataset/source//"
        for file_name in os.listdir(path):
            # construct full file path
            file = path + file_name
            if os.path.isfile(file):
                os.remove(file)
        image = request.form['mydata']
        img_binary = base64.b64decode(image)
        img_jpg = np.frombuffer(img_binary, dtype=np.uint8)
        img = cv2.imdecode(img_jpg, cv2.IMREAD_ANYCOLOR)
        up_widthh = 1776
        up_heightt = 1184
        up_pointss = (up_widthh, up_heightt)
        img = cv2.resize(img, up_pointss, interpolation=cv2.INTER_LINEAR)
        #print(img)
        #image_file = "static/dataset/source/0002.jpg"
        now = datetime.now()
        current_time = now.strftime("%d_%m_%Y_%H_%M_%S")
        image_file = 'static/dataset/source/img_%s.jpg' % current_time
        # image_file = "C:/Users/user/Videos/endend/app/static/dataset/img0000.jpg "
        cv2.imwrite(image_file, img)
        cv2.imwrite('static/dataset/source/000.jpg', img)
    return render_template('resultpic.html', img = image_file)
    
@app.route('/back_capture')
def back_capture():
    return redirect(url_for('identify'))

@app.route('/my-link/')
def my_link():
    # img = "static/dataset/source/"
    # data_path = os.path.join(img, '*g')
    # files = glob.glob(data_path)
    # for f1 in files:
    #     img = cv2.imread(f1)
    img = cv2.imread('static/dataset/source/000.jpg')
    haar_cascade = cv2.CascadeClassifier('newcascade.xml')
    
    plate_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plate_overlay = plate_img.copy()
        # plate_rects = []
    plate_rects = haar_cascade.detectMultiScale(plate_overlay, scaleFactor=1.1, minNeighbors=2)
    yo = all(map(lambda x: x is None, plate_rects))  
    if yo == True:
        print("plat tidak terdeteksi")
        return render_template('ulangPlat.html')
    else:
        x, y, w, h = plate_rects[0]
        cv2.putText(plate_overlay, 'Plat Nomer', (x, y), cv2.FONT_HERSHEY_PLAIN, 3, (0 , 0 , 255), 2)
        crop = cv2.rectangle(plate_overlay, (x, y), (x + w, y + h), (0, 0, 255),2)
        carplate_img = plate_overlay[y : y + h , x : x + w ]
        cv2.imwrite('static/dataset/sliced/crop.jpg', carplate_img)


    path_slice = "static/dataset/sliced"
    for file_name in sorted(os.listdir(path_slice)):
        image = cv2.imread(os.path.join(path_slice, file_name))
        down_width = 400
        down_height = 200
        down_points = (down_width, down_height)
        resized_down = cv2.resize(image, down_points, interpolation=cv2.INTER_LINEAR)
        # cv2.imshow(resized_down)
        now = datetime.now()
        current_time = now.strftime("%d_%m_%Y_%H_%M_%S")
        image_file = 'static/dataset/sliced/crop_%s.jpg' % current_time
        call_img = '/static/dataset/sliced/crop_%s.jpg' % current_time
        path = r"static/dataset/sliced//"
        for file_name in os.listdir(path):
            # construct full file path
            file = path + file_name
            if os.path.isfile(file):
                os.remove(file)
        cv2.imwrite(image_file, resized_down)
        path_plate = "static/dataset/sliced"

        # Looping file di direktori
        for name_file in sorted(os.listdir(path_plate)):
            src = cv2.imread(os.path.join(path_plate, name_file))
            blurred = src.copy()
            gray = blurred.copy()

            # Filtering
            for i in range(10):
                blurred = cv2.GaussianBlur(src, (5, 5), 0.5)

        # Ubah ke grayscale
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

        # Image binary
        ret, bw = cv2.threshold(gray.copy(), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        print(ret, bw.shape)
        cv2.imwrite("segmentasi-bw.jpg", bw)
        # cv2_imshow(erode)
        # cv2.waitKey()

        erode = cv2.erode(bw.copy(), cv2.getStructuringElement(cv2.MORPH_OPEN, (3, 6)))
        cv2.imwrite("segmentasi-erode.jpg", erode)
        # cv2.imshow("erode", erode)
        # cv2.waitKey()

        # Ekstraksi kontur
        contours, hierarchy = cv2.findContours(erode.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # Looping contours untuk mendapatkan kontur yang sesuai
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            ras = format(w / h, '.2f')
            # print("x={}, y={}, w={}, h={}, rasio={}".format(x, y, w, h, ras))
            if h >= 70 and w >= 10 and float(ras) <= 1:
                # Gambar segiempat hasil segmentasi warna merah
                cv2.rectangle(src, (x, y), (x + w, y + h), (0, 0, 255), thickness=1)
                print("+ x={}, y={}, w={}, h={}, rasio={}".format(x, y, w, h, ras))
        cv2.imwrite("segmentasi-result.jpg", src)
        Cropped_img = cv2.imread('segmentasi-result.jpg')
        cv2.waitKey()

        ret, bw = cv2.threshold(gray.copy(), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        contours_plate, hierarchy = cv2.findContours(bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # index contour yang berisi kandidat karakter
        index_chars_candidate = []  # index

        # index counter dari setiap contour di contours_plate
        index_counter_contour_plate = 0  # idx

        # duplikat dan ubah citra plat dari gray dan bw ke rgb untuk menampilkan kotak karakter
        img_plate_rgb = cv2.cvtColor(gray.copy(), cv2.COLOR_GRAY2BGR)
        img_plate_bw_rgb = cv2.cvtColor(bw, cv2.COLOR_GRAY2RGB)

        for contour_plate in contours_plate:

            # dapatkan lokasi x, y, nilai width, height dari setiap kontur plat
            x_char, y_char, w_char, h_char = cv2.boundingRect(contour_plate)

            # Dapatkan kandidat karakter jika:
            #   tinggi kontur dalam rentang 40 - 60 piksel
            #   dan lebarnya lebih dari atau sama dengan 10 piksel
            if h_char >= 58 and h_char <= 120 and w_char >= 10:
                # dapatkan index kandidat karakternya
                index_chars_candidate.append(index_counter_contour_plate)

                # gambar kotak untuk menandai kandidat karakter
                cv2.rectangle(img_plate_rgb, (x_char, y_char), (x_char + w_char, y_char + h_char), (0, 255, 0), 5)
                cv2.rectangle(img_plate_bw_rgb, (x_char, y_char), (x_char + w_char, y_char + h_char), (0, 255, 0), 5)

            index_counter_contour_plate += 1

        # tampilkan kandidat karakter
        cv2.imwrite("segmentasi-result.jpg", src)

        if index_chars_candidate == []:

            # tampilkan peringatan apabila tidak ada kandidat karakter
            print('Karakter tidak tersegmentasi')
        else:
            score_chars_candidate = np.zeros(len(index_chars_candidate))

            # untuk counter index karakter
            counter_index_chars_candidate = 0

            # bandingkan lokasi y setiap kandidat satu dengan kandidat lainnya
            for chars_candidateA in index_chars_candidate:

                # dapatkan nilai y dari kandidat A
                xA, yA, wA, hA = cv2.boundingRect(contours_plate[chars_candidateA])
                for chars_candidateB in index_chars_candidate:

                    # jika kandidat yang dibandikan sama maka lewati
                    if chars_candidateA == chars_candidateB:
                        continue
                    else:
                        # dapatkan nilai y dari kandidat B
                        xB, yB, wB, hB = cv2.boundingRect(contours_plate[chars_candidateB])

                        # cari selisih nilai y kandidat A dan kandidat B
                        y_difference = abs(yA - yB)

                        # jika perbedaannya kurang dari 11 piksel
                        if y_difference < 50:
                            # tambahkan nilai score pada kandidat tersebut
                            score_chars_candidate[counter_index_chars_candidate] = score_chars_candidate[
                                                                                       counter_index_chars_candidate] + 1

                            # lanjut ke kandidat lain
                counter_index_chars_candidate += 1

            print(score_chars_candidate)

            # untuk menyimpan karakter
            index_chars = []

            # counter karakter
            chars_counter = 0

            # dapatkan karakter, yaitu yang memiliki score tertinggi
            for score in score_chars_candidate:
                if score == max(score_chars_candidate):
                    # simpan yang benar-benar karakter
                    index_chars.append(index_chars_candidate[chars_counter])
                chars_counter += 1

                img_plate_rgb2 = cv2.cvtColor(gray.copy(), cv2.COLOR_GRAY2BGR)

                # tampilkan urutan karakter yang belum terurut
                for char in index_chars:
                    x, y, w, h = cv2.boundingRect(contours_plate[char])
                    cv2.rectangle(img_plate_rgb2, (x, y), (x + w, y + h), (0, 255, 0), 5)
                    cv2.putText(img_plate_rgb2, str(index_chars.index(char)), (x, y + h + 50), cv2.FONT_ITALIC, 2.0,
                                (0, 0, 255), 3)

                # tampilkan karakter yang belum terurut
                # cv.imshow('Karakter Belum Terurut', img_plate_rgb2)

                # Mulai mengurutkan

                # untuk menyimpan koordinat x setiap karakter
                x_coors = []

                for char in index_chars:
                    # dapatkan nilai x
                    x, y, w, h = cv2.boundingRect(contours_plate[char])

                    # dapatkan nilai sumbu x
                    x_coors.append(x)

                # urutkan sumbu x dari terkecil ke terbesar
                x_coors = sorted(x_coors)

                # untuk menyimpan karakter
                index_chars_sorted = []

                # urutkan karakternya berdasarkan koordinat x yang sudah diurutkan
                for x_coor in x_coors:
                    for char in index_chars:

                        # dapatkanx nilai koordinat x karakter
                        x, y, w, h = cv2.boundingRect(contours_plate[char])

                        # jika koordinat x terurut sama dengan koordinat x pada karakter
                        if x_coors[x_coors.index(x_coor)] == x:
                            # masukkan karakternya ke var baru agar mengurut dari kiri ke kanan
                            index_chars_sorted.append(char)
                            img_plate_rgb3 = cv2.cvtColor(gray.copy(), cv2.COLOR_GRAY2BGR)

                            # Gambar kotak untuk menandai karakter yang terurut dan tambahkan teks urutannya
                            for char_sorted in index_chars_sorted:
                                # dapatkan nilai x, y, w, h dari karakter terurut
                                x, y, w, h = cv2.boundingRect(contours_plate[char_sorted])

                                # gambar kotak yang menandai karakter terurut
                                cv2.rectangle(img_plate_rgb3, (x, y), (x + w, y + h), (0, 255, 0), 5)

                                # tambahkan teks urutan karakternya
                                cv2.putText(img_plate_rgb3, str(index_chars_sorted.index(char_sorted)), (x, y + h + 50),
                                            cv2.FONT_ITALIC, 2.0, (0, 0, 255), 3)

            img_height = 40
            img_width = 40
            # klas karakter
            class_names = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                           'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

            # load model yang sudah terlatih
            model = keras.models.load_model('my_model')

            # untuk menyimpan string karakter
            num_plate = []

            for char_sorted in index_chars_sorted:
                x, y, w, h = cv2.boundingRect(contours_plate[char_sorted])

                # potong citra karakter
                char_crop = cv2.cvtColor(bw[y:y + h, x:x + w], cv2.COLOR_GRAY2BGR)

                # resize citra karakternya
                char_crop = cv2.resize(char_crop, (img_width, img_height))

                # preprocessing citra ke numpy array
                img_array = keras.preprocessing.image.img_to_array(char_crop)

                # agar shape menjadi [1, h, w, channels]
                img_array = tf.expand_dims(img_array, 0)

                # buat prediksi
                predictions = model.predict(img_array)
                score = tf.nn.softmax(predictions[0])

                num_plate.append(class_names[np.argmax(score)])
                x = class_names[np.argmax(score)]
                print("platnya adalah @@@@@@@@@@@@@@@@")
                print(class_names[np.argmax(score)], end='')

        def listToString(s):
            # initialize an empty string
            str1 = ""
            # traverse in the string
            for ele in s:
                str1 += ele
                # return string
            return str1

        myplate = listToString(num_plate)
        len_myplate = len(myplate)

        file = glob.glob(r'static/dataset/sliced/*.*')
        file = json.dumps(file)
        file = file.replace("'", "")
        file = file.replace("[", "")
        file = file.replace("]", "")
        fix = file.replace('"', '')
        print(fix)
        return render_template('readPlat.html', plate=myplate, img=call_img)
            

@app.route('/servo')
def servo():
    hasil = []
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT * FROM servo")
    result = cursor.fetchall()
    for data in result:
        hasil.append(data)
    cursor.close()
    return render_template('servo.html', hasil=result)

@app.route('/cek', methods=['POST', 'GET'])
def cek():
    hasil = request.form['txt']
    cursor = mysql.get_db().cursor()
    cursor1 = mysql.get_db().cursor()
    cursor2 = mysql.get_db().cursor()
    cursor3 = mysql.get_db().cursor()
    query = ("SELECT * FROM `owner` WHERE plat=" + "'" + hasil + "'");
    query1 = ("SELECT foto FROM `owner` WHERE plat=" + "'" + hasil + "'");
    query2 = ("SELECT plat FROM `owner` WHERE plat=" + "'" + hasil + "'");
    cursor3.execute('''UPDATE plat SET plat=%s WHERE id=1''',(hasil))
    cursor.execute(query)
    cursor1.execute(query1)
    cursor2.execute(query2)
    result = cursor.fetchall()
    result1 = cursor1.fetchall()
    result2 = cursor2.fetchall()
    s = json.dumps(result2)
    x = s.replace("plat", "")
    x = x.replace("[", "")
    x = x.replace("{", "")
    x = x.replace(":", "")
    x = x.replace("]", "")
    x = x.replace("}", "")
    x = x.replace(" ", "")
    x = x.replace('""', '')
    fix = x.replace('"', '')
    if hasil == fix:
        s = json.dumps(result1)
        x = s.replace("foto", "")
        x = x.replace("[", "")
        x = x.replace("{", "")
        x = x.replace(":", "")
        x = x.replace("]", "")
        x = x.replace("}", "")
        x = x.replace(" ", "")
        x = x.replace('""', '')
        fix = x.replace('"', '')
        fixfix = os.path.join(app.config['PHOTO_FOLDER'], fix)
        cursor_buka = mysql.get_db().cursor()
        cursor_buka.execute('''UPDATE servo SET servo = 180 WHERE id=1''')
        mysql.get_db().commit()
        cursor_buka.close()
        return render_template('owner.html', value=result, fixfix=fixfix)
    else:
        # siku()
        cursor_buka1 = mysql.get_db().cursor()
        cursor_buka1.execute('''UPDATE servo SET servo = 180 WHERE id=1''')
        mysql.get_db().commit()
        cursor_buka1.close()
        return render_template('not_owner.html')

@app.route('/addnewdata', methods=['GET', 'POST'])
def addnewdata():
    cur = mysql.get_db().cursor()
    cur.execute('SELECT * FROM plat WHERE id=1')
    mysql.get_db().commit()
    result = cur.fetchall()
    cur.close()
    return render_template('addnewdata.html', plat=result)
        
@app.route('/close', methods=['GET', 'POST'])
def close():
    cursor_tutup = mysql.get_db().cursor()
    cursor_tutup.execute('''UPDATE servo SET servo = 0 WHERE id=1''')
    mysql.get_db().commit()
    cursor_tutup.close()
    return redirect(url_for('home'))
    
@app.route('/closenotowner', methods=['GET', 'POST'])
def closenotowner():
    cursor_tutup = mysql.get_db().cursor()
    cursor_tutup.execute('''UPDATE servo SET servo = 0 WHERE id=1''')
    mysql.get_db().commit()
    cursor_tutup.close()
    return redirect(url_for('addnewdata'))