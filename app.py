import sqlite3
import hashlib
import pandas as pd
import os
import json
import traceback
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, jsonify, abort
from urllib.parse import quote, unquote
import uuid
from datetime import datetime
from flask import session
import csv
import urllib.parse
from flask import Response
from flask_babel import Babel
from werkzeug.utils import secure_filename
import time


app = Flask(__name__)

# ---------- الإعدادات العامة ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# مجلدات التحميل والبيانات
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'pdfs')
DATA_DIR = os.path.join(BASE_DIR, 'data')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['BABEL_DEFAULT_LOCALE'] = 'ar'
app.secret_key = 'مفتاح_سري_آمن'

students = []  # قائمة لتخزين الأسماء والنقاط

# ---------- المسارات إلى ملفات CSV ----------
STUDENTS_FILE = os.path.join(DATA_DIR, 'students.csv')
STUDENTS01_FILE = os.path.join(DATA_DIR, 'students01.csv')
STUDENTS02_FILE = os.path.join(DATA_DIR, 'students02.csv')
STUDENTS03_FILE = os.path.join(DATA_DIR, 'students03.csv')
STUDENTS04_FILE = os.path.join(DATA_DIR, 'students04.csv')
STUDENTS05_FILE = os.path.join(DATA_DIR, 'students05.csv')
STUDENTS06_FILE = os.path.join(DATA_DIR, 'students06.csv')

S1_FILE = os.path.join(DATA_DIR, 'S1.csv')
S2_FILE = os.path.join(DATA_DIR, 'S2.csv')
S3_FILE = os.path.join(DATA_DIR, 'S3.csv')
S4_FILE = os.path.join(DATA_DIR, 'S4.csv')
S5_FILE = os.path.join(DATA_DIR, 'S5.csv')
S6_FILE = os.path.join(DATA_DIR, 'S6.csv')

MESSAGE_FILE = os.path.join(DATA_DIR, 'message.csv')
ADS_FILE = os.path.join(DATA_DIR, 'ads.csv')

print("DATA_DIR:", DATA_DIR)
print("STUDENTS01_FILE:", STUDENTS01_FILE)
print("Does file exist?", os.path.exists(STUDENTS01_FILE))

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # حجم أقصى: 2MB

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}



# تأكد من وجود المجلد static/pdfs قبل تخزين الملف
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# تحميل ملف الترجمة
base_dir = os.path.dirname(os.path.abspath(__file__))
translations_path = os.path.join(base_dir, "translations.json")

with open(translations_path, "r", encoding="utf-8") as file:
    TRANSLATIONS = json.load(file)

LANGUAGES = ['en', 'ar', 'fr']

def get_locale():
    return session.get('language', 'ar')

@app.route('/get_translations/<lang>')
def get_translations(lang):
    return jsonify({'translations': TRANSLATIONS.get(lang, TRANSLATIONS['ar'])})

@app.route('/set_language/<lang>', methods=['POST'])
def set_language(lang):
    if lang in LANGUAGES:
        session['language'] = lang
        session.modified = True
    return jsonify({'success': True})

@app.route('/change_language/<lang>', methods=['POST'])
def change_language(lang):
    if lang in LANGUAGES:
        session['language'] = lang
        session.modified = True
        return jsonify({'success': True, 'translations': TRANSLATIONS.get(lang, TRANSLATIONS['ar'])})
    return jsonify({'success': False})


@app.route('/delete_file', methods=['POST'])
def delete_file():
    try:
        file_name = request.json.get('file_name')  # تأكد من استخدام json لتلقي البيانات
        if not file_name:
            return jsonify({'success': False, 'message': 'اسم الملف غير موجود'})

        # تحديد البريد الإلكتروني للأستاذ (يفترض أنه يمكن استخراجه من الجلسة أو الطلب)
        teacher_email = request.json.get('teacher_email')  # يجب إرسال البريد الإلكتروني مع الطلب

        if not teacher_email:
            return jsonify({'success': False, 'message': 'البريد الإلكتروني غير موجود'})

        # تحديد المسار الصحيح باستخدام البريد الإلكتروني
        file_path = os.path.join(app.root_path, 'static', 'pdfs', teacher_email, file_name)

        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'success': True, 'message': 'تم حذف الملف بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'الملف غير موجود'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


def load_teacher_subjects():
    subjects_dict = {}

    # المسار المطلق إلى ملف الطلاب
    file_path = STUDENTS_FILE

    if not os.path.exists(file_path):
        print(f"⚠️ ملف {file_path} غير موجود!")  # طباعة المسار للتحقق
        return subjects_dict  # إرجاع قاموس فارغ لمنع الأخطاء

    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)  # استخدام DictReader لسهولة التعامل مع الأعمدة

        for row in reader:
            teacher_email = row.get('email', '').strip()  # البريد الإلكتروني للأستاذ
            subject = row.get('subject', '').strip() if row.get('subject') else None  # المادة مع تحقق من عدم كونها None

            # التأكد من أن البريد الإلكتروني والمادة موجودة
            if teacher_email and subject:
                if teacher_email not in subjects_dict:
                    subjects_dict[teacher_email] = set()  # استخدمنا set لمنع التكرار
                subjects_dict[teacher_email].add(subject)

    # تحويل `set` إلى `list` حتى يمكن إرجاعه كـ JSON
    return {email: list(subjects) for email, subjects in subjects_dict.items()}

@app.route('/upload_file', methods=['POST'])
def upload_file():
    user_email = session.get('email', None)
    print(f"البريد الإلكتروني للمستخدم: {user_email}")  # طباعة البريد الإلكتروني للمستخدم

    if not user_email:
        return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً.'}), 401

    teacher_subjects = load_teacher_subjects()
    print(f"المواد المتاحة للأستاذ: {teacher_subjects}")  # طباعة المواد المتاحة

    if 'file' not in request.files or 'subject' not in request.form or 'filename' not in request.form:
        return jsonify({'success': False, 'message': 'يجب اختيار ملف وإدخال اسم المادة واسم الملف.'}), 400

    file = request.files['file']
    subject = request.form['subject'].strip().replace(" ", "_").lower()  # ⚡ تطبيع الاسم
    filename = request.form['filename'].strip().replace(" ", "_")

    print(f"اسم الملف: {filename}, المادة: {subject}")  # طباعة اسم الملف والمادة

    if file.filename == '' or filename == '':
        return jsonify({'success': False, 'message': 'لم يتم اختيار ملف أو إدخال اسم الملف.'}), 400

    allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png', 'docx', 'doc'}
    file_extension = file.filename.rsplit('.', 1)[-1].lower()

    print(f"الامتداد المسموح به: {file_extension}")  # طباعة الامتداد المسموح به

    if file_extension not in allowed_extensions:
        return jsonify({'success': False, 'message': 'الملف يجب أن يكون من نوع PDF أو صورة أو مستند Word.'}), 400

    if user_email not in teacher_subjects:
        return jsonify({'success': False, 'message': '⚠️ الأستاذ غير مسجل في النظام!'}), 400

    # ⚡ تطبيع جميع أسماء المواد الخاصة بالأستاذ قبل التحقق
    teacher_subjects[user_email] = [s.lower() for s in teacher_subjects[user_email]]

    # تطبيع أسماء المواد الخاصة بالأستاذ قبل التحقق
    

    if subject not in teacher_subjects[user_email]:
        return jsonify({'success': False, 'message': f'⚠️ يرجى إدخال مادة صحيحة من قائمة المواد المتاحة: {teacher_subjects[user_email]}'}), 400

    try:
        teacher_email_modified = user_email.replace("@", "_").replace(".", "_")
        unique_filename = f"{filename}.{file_extension}"
        print(f"اسم الملف الفريد: {unique_filename}")  # طباعة اسم الملف الفريد

        subject_folder = os.path.join(app.config['UPLOAD_FOLDER'], teacher_email_modified, subject)
        print(f"مسار المجلد: {subject_folder}")  # طباعة المسار الذي سيتم تخزين الملف فيه

        os.makedirs(subject_folder, exist_ok=True)
        file_path = os.path.join(subject_folder, unique_filename)

        if os.path.exists(file_path):
            return jsonify({'success': False, 'message': '⚠️ الملف موجود مسبقًا بنفس الاسم! يرجى اختيار اسم مختلف.'}), 400

        file.save(file_path)
        return jsonify({'success': True, 'message': '✅ تم رفع الملف بنجاح!', 'file_name': unique_filename})
    except Exception as e:
        print(f"حدث خطأ أثناء رفع الملف: {str(e)}")  # طباعة الخطأ عند حدوثه
        return jsonify({'success': False, 'message': f'❌ حدث خطأ أثناء رفع الملف: {str(e)}'}), 500

@app.route('/get_subjects', methods=['GET'])
def get_subjects():
    user_email = session.get('email', None)
    if not user_email:
        return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً.'}), 401

    teacher_subjects = load_teacher_subjects()  # إعادة تحميل البيانات لضمان التحديث المستمر
    subjects = teacher_subjects.get(user_email, [])

    return jsonify({'success': True, 'subjects': subjects})

@app.route('/check_file_exists', methods=['GET'])
def check_file_exists():
    user_email = session.get('email', None)
    if not user_email:
        return jsonify({'exists': False})

    subject = request.args.get('subject', '').strip().replace(" ", "_").lower()
    filename = request.args.get('filename', '').strip().replace(" ", "_")

    if not subject or not filename:
        return jsonify({'exists': False})

    subject_folder = os.path.join(app.config['UPLOAD_FOLDER'], user_email, subject)
    if not os.path.exists(subject_folder):
        return jsonify({'exists': False})

    for ext in ['pdf', 'jpg', 'jpeg', 'png', 'docx', 'doc']:
        file_path = os.path.join(subject_folder, f"{filename}.{ext}")
        if os.path.exists(file_path):
            return jsonify({'exists': True})

    return jsonify({'exists': False})


BASE_DIR = os.path.join(os.getcwd(), "site_college21", "static", "pdfs")

def email_to_folder(email):
    return email.replace('@', '_').replace('.', '_')

@app.route('/get_files', methods=['GET'])
def get_files():
    print("\n🚀🚀🚀 بدء تنفيذ دالة get_files 🚀🚀🚀")

    # الخطوة 1: استقبال البيانات
    print("1️⃣ استقبال البيانات من الطلب...")
    teacher_email = request.args.get('teacher_email')
    subject = request.args.get('subject')
    print(f"📩 البريد الإلكتروني المستلم: {teacher_email}")
    print(f"📚 اسم المادة المستلم: {subject}")

    # الخطوة 2: التحقق من صحة البيانات
    print("2️⃣ التحقق من وجود البريد الإلكتروني والمادة...")
    if not teacher_email or not subject:
        print("❌ لم يتم إرسال البريد الإلكتروني أو المادة")
        return jsonify({'success': False, 'message': '❌ يجب إرسال البريد الإلكتروني والمادة'}), 400

    # الخطوة 3: تجهيز أسماء المجلدات
    print("3️⃣ تجهيز أسماء المجلدات بعد فك التشفير والتحويل...")
    teacher_folder = email_to_folder(urllib.parse.unquote(teacher_email))
    subject_folder = urllib.parse.unquote(subject)
    print(f"📨 مجلد الأستاذ بعد التحويل: {teacher_folder}")
    print(f"📖 مجلد المادة بعد فك التشفير: {subject_folder}")

    # الخطوة 4: بناء المسار الكامل
    print("4️⃣ بناء المسار الكامل للمجلد...")
    subject_folder_path = os.path.join(BASE_DIR, teacher_folder, subject_folder)
    print(f"📂 المسار الكامل المتوقع: {subject_folder_path}")

    # الخطوة 5: التحقق من وجود المجلد
    print("5️⃣ التحقق مما إذا كان المجلد موجودًا على القرص...")
    if not os.path.exists(subject_folder_path):
        print("❌ لا يوجد هذا المجلد على القرص")
        return jsonify({'success': False, 'message': '📂 لا يوجد ملفات للمادة.'})

    # الخطوة 6: جلب الملفات داخل المجلد
    print("6️⃣ جلب قائمة الملفات داخل المجلد...")
    try:
        files = os.listdir(subject_folder_path)
        print(f"✅ تم العثور على {len(files)} ملف/ملفات: {files}")
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        print(f"❌ خطأ أثناء قراءة الملفات: {str(e)}")
        return jsonify({'success': False, 'message': '❌ خطأ أثناء قراءة الملفات'}), 500

print("\n🚀🚀🚀 بدء تنفيذ دالة delete_file 🚀🚀🚀")
@app.route('/delete_files', methods=['POST'])
def delete_files():
    print("\n🚀🚀🚀 بدء تنفيذ دالة delete_file 🚀🚀🚀")  # طباعة هنا للتأكد من الوصول إلى الدالة

    # استقبال البيانات من الطلب
    data = request.json
    teacher_email = data.get('teacher_email')
    subject = data.get('subject')
    file_name = data.get('file_name')

    print(f"📩 البريد الإلكتروني: {teacher_email}")
    print(f"📚 المادة: {subject}")
    print(f"📄 اسم الملف: {file_name}")
    


    # التحقق من صحة البيانات
    if not teacher_email or not subject or not file_name:
        print("❌ بيانات غير كاملة")
        return jsonify({'success': False, 'message': '❌ يجب إرسال البريد الإلكتروني، المادة، واسم الملف'}), 400

    try:
        # تجهيز المسار الكامل للملف
        teacher_folder = email_to_folder(urllib.parse.unquote(teacher_email))
        subject_folder = urllib.parse.unquote(subject)
        file_path = os.path.join(BASE_DIR, teacher_folder, subject_folder, file_name)
        print(f"🗂️ المسار الكامل للملف (الفعلي): {os.path.abspath(file_path)}")


        print(f"🗂️ المسار الكامل للملف: {file_path}")

        # التحقق من وجود الملف ثم حذفه
        if os.path.exists(file_path):
            os.remove(file_path)
            print("✅ تم حذف الملف بنجاح")
            return jsonify({'success': True, 'message': '✅ تم حذف الملف بنجاح'})
        else:
            print("❌ الملف غير موجود")
            return jsonify({'success': False, 'message': '❌ الملف غير موجود'}), 404
    except Exception as e:
        print(f"❌ خطأ أثناء الحذف: {str(e)}")
        return jsonify({'success': False, 'message': '❌ حدث خطأ أثناء حذف الملف'}), 500

@app.route("/retrieve_files")
def retrieve_files():
    print("\n🚀🚀🚀 بدء تنفيذ دالة retrieve_files 🚀🚀🚀")

    # استقبال البريد الإلكتروني والمادة من الطلب
    teacher_email = request.args.get("teacher_email")
    subject = request.args.get("subject")  # تأكد من أنك تستخدم "subject" هنا
    print(f"📩 البريد الإلكتروني للأستاذ: {teacher_email}")
    print(f"📚 المادة المطلوبة: {subject if subject else 'لا توجد مادة محددة'}")

    # التحقق من وجود البريد الإلكتروني
    if not teacher_email:
        print("❌ لم يتم تحديد البريد الإلكتروني")
        return jsonify({"success": False, "message": "لم يتم تحديد البريد الإلكتروني."})

    # تجهيز مسار مجلد الأستاذ
    teacher_folder = email_to_folder(teacher_email)
    folder_path = os.path.join(BASE_DIR, teacher_folder)
    print(f"📂 المسار الفعلي لمجلد الأستاذ: {folder_path}")

    if not os.path.exists(folder_path):
        print("❌ مجلد الأستاذ غير موجود")
        return jsonify({"success": False, "message": "مجلد الأستاذ غير موجود."})

    # إذا لم يتم تحديد مادة، نعرض المجلدات
    if not subject:
        try:
            items = os.listdir(folder_path)
            result = []
            for item in items:
                item_path = os.path.join(folder_path, item)
                if os.path.isdir(item_path):
                    result.append({"type": "folder", "name": item})
            print(f"✅ تم العثور على {len(result)} مادة/مجلد: {result}")
            return jsonify({"success": True, "type": "folders_and_files", "items": result})
        except Exception as e:
            print(f"❌ خطأ أثناء قراءة المجلدات: {e}")
            return jsonify({"success": False, "message": "خطأ أثناء قراءة المجلدات."})
    else:
        # إذا تم تحديد مادة
        safe_subject = urllib.parse.unquote(subject)
        subject_path = os.path.join(folder_path, safe_subject)
        print(f"📂 المسار الفعلي لمجلد المادة: {subject_path}")

        if not os.path.exists(subject_path):
            print("❌ مجلد المادة غير موجود")
            return jsonify({"success": False, "message": "مجلد المادة غير موجود."})

        try:
            files = os.listdir(subject_path)
            print(f"✅ تم العثور على {len(files)} ملف/ملفات: {files}")
            return jsonify({"success": True, "type": "files", "items": files})
        except Exception as e:
            print(f"❌ خطأ أثناء قراءة الملفات: {e}")
            return jsonify({"success": False, "message": "خطأ أثناء قراءة الملفات."})

@app.route('/lessonss')
def lessonss():
    teacher_email = request.args.get('teacher_email')
    subject = request.args.get('subject')

    if not teacher_email or not subject:
        return jsonify({"success": False, "message": "بيانات غير مكتملة"}), 400

    # الحصول على الملفات الخاصة بالأستاذ والمادة
    pdf_files = get_files_for_teacher(teacher_email, subject)

    return render_template("lessonss.html", pdf_files=pdf_files, subject=subject, teacher_email=teacher_email, language=get_locale())

def get_files_for_teacher(teacher_email, subject):
    base_folder = os.path.join("site_college21", "static", "pdfs", teacher_email, subject)

    print(f"🔍 البحث في: {os.path.abspath(base_folder)}")  # عرض المسار المطلق للتحقق

    if os.path.exists(base_folder) and os.path.isdir(base_folder):
        print(f"📁 المجلد موجود: {base_folder}")
        files = [file for file in os.listdir(base_folder) if file.endswith(".pdf")]
        return files
    else:
        print(f"⚠️ المجلد غير موجود: {base_folder}")

    return []

@app.route('/pdf_viewer')
def pdf_viewer():
    file = request.args.get('file')
    teacher_email = request.args.get('teacher_email')
    subject = request.args.get('subject')

    # توليد الرابط الصحيح للملف داخل static
    file_url = url_for('static', filename=f'pdfs/{teacher_email}/{subject}/{file}')

    return render_template("pdf_viewer.html", file_url=file_url, language=get_locale())

# عرض الدروس الخاصة بالأستاذ الأول
from urllib.parse import quote

@app.route('/lessons')
def lessons():
    try:
        teacher = request.args.get('teacher', None)
        if not teacher:
            return "لم يتم تحديد الأستاذ.", 400

        # تحديد البريد الإلكتروني للأستاذ بناءً على قيمة teacher
        teacher_email_mapping = {
            'teacher1': 'bansalem.rj@usmba.ac.ma',
            'teacher2': 'ali.al-baqali@usmba.ac.ma',
            'teacher3': 'ali.ch@usmba.ac.ma',
            'teacher4': 'abdulsalam.sa@usmba.ac.ma',
            'teacher5': 'ali.wh@usmba.ac.ma',
            'teacher6': 'bouzkraoui.drs@usmba.ac.ma',
            'teacher7': 'bushra.sb@usmba.ac.ma',
            'teacher8': 'fatima-zahra.ms@usmba.ac.ma',
            'teacher9': 'hassan.am@usmba.ac.ma',
            'teacher10': 'idris.zh@usmba.ac.ma',
            'teacher11': 'muhammed.hn@usmba.ac.ma',
            'teacher12': 'muhammed.am@usmba.ac.ma',
            'teacher13': 'muhammad.zr@usmba.ac.ma',
            'teacher14': 'muhammed.hm@usmba.ac.ma',
            'teacher15': 'magda.sb@usmba.ac.ma',
            'teacher16': 'nawar.af@usmba.ac.ma',
            'teacher17': 'raja.bh@usmba.ac.ma',
            'teacher18': 'sabah.sr@usmba.ac.ma', 
            'teacher19': 'souad.bn@usmba.ac.ma',
            'teacher20': 'tarek.mj@usmba.ac.ma',
            'teacher21': 'wasila.bnk@usmba.ac.ma',
        }

        email = teacher_email_mapping.get(teacher)
        if not email:
            return "الأستاذ غير موجود.", 404

        # تعيين المجلد الخاص بالأستاذ بناءً على بريده الإلكتروني
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], email)

        # التأكد من أن المجلد موجود
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
            print(f"✅ تم إنشاء المجلد بنجاح: {user_folder}")

        # جلب ملفات PDF و الصور
        pdf_files = [file for file in os.listdir(user_folder) if file.endswith('.pdf')]
        image_files = [file for file in os.listdir(user_folder) if file.lower().endswith(('.jpg', '.jpeg', '.png'))]

        # فك الترميز لتجنب أي مشاكل في عرض الأسماء
        pdf_files = [unquote(file) for file in pdf_files]
        image_files = [unquote(file) for file in image_files]

        # تمرير `role` و `teacher_email` من الجلسة
        role = session.get('role', 'guest')

        return render_template('lessons.html', pdf_files=pdf_files, image_files=image_files, quote=quote, teacher=teacher, role=role, teacher_email=email)
    except Exception as e:
        print(f"Error in /lessons: {e}")  # تسجيل الأخطاء
        return f"حدث خطأ أثناء تحميل الملفات: {str(e)}", 500

# عرض الدروس الخاصة بالأستاذ الثاني
# عرض الدروس الخاصة بالأستاذ الثاني
@app.route('/lessons1')
def lessons1():
    try:
        role = session.get('role', 'guest')
        email = session.get('email', None)

        print(f"Session Role: {role}, Session Email: {email}")  # لتصحيح الأخطاء

        # التحقق من الجلسة
        if not email or role != 'student':
            return redirect(url_for('signup'))

        # تخصيص مجلد الملفات حسب البريد الإلكتروني للأستاذ الثاني
        teacher_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'teacher2')
        if not os.path.exists(teacher_folder):
            os.makedirs(teacher_folder)

        # عرض ملفات PDF فقط
        pdf_files = [file for file in os.listdir(teacher_folder) if file.endswith('.pdf')]
        pdf_files = [unquote(file) for file in pdf_files]

        return render_template('lessons1.html', pdf_files=pdf_files, quote=quote, role=role)
    except Exception as e:
        print(f"Error in lessons1 route: {e}")
        return f"حدث خطأ أثناء تحميل الملفات: {str(e)}", 500
    
@app.route('/lessons2')
def lessons2():
    try:
        role = session.get('role', 'guest')
        email = session.get('email', None)

        # التحقق من الجلسة
        if not email or role != 'student':
            return redirect(url_for('signup'))

        # تخصيص مجلد الملفات حسب البريد الإلكتروني للأستاذ الثالث
        teacher_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'teacher3')
        if not os.path.exists(teacher_folder):
            os.makedirs(teacher_folder)

        # عرض ملفات PDF فقط
        pdf_files = [file for file in os.listdir(teacher_folder) if file.endswith('.pdf')]
        pdf_files = [unquote(file) for file in pdf_files]

        return render_template('lessons2.html', pdf_files=pdf_files, quote=quote, role=role)
    except Exception as e:
        print(f"Error in lessons2 route: {e}")
        return f"حدث خطأ أثناء تحميل الملفات: {str(e)}", 500

@app.route('/image_viewer/<filename>')
def image_viewer(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# عرض ملف PDF
# عرض ملف PDF



# الصفحة الرئيسية

@app.route('/student_dashboard')
def student_dashboard():
    # عرض صفحة المواضيع
    return render_template('student_dashboard.html', language=get_locale())

@app.route('/AAAAA')
def AAAAA():
    # عرض صفحة المواضيع
    return render_template('AAAAA.html', language=get_locale())


@app.route('/announcement_list')
def announcement_list():
    return render_template('announcement_list.html', language=get_locale())

@app.route('/saved_students_table')
def saved_students_table():
    return render_template('saved_students_table.html', language=get_locale())  # تأكد من أن هذا الملف موجود

@app.route('/Quick_entry_points')
def Quick_entry_points():
    return render_template('Quick_entry_points.html', language=get_locale())  # تأكد من أن هذا الملف موجود

@app.route('/control')
def control():
    return render_template('control.html', language=get_locale())  # تأكد من أن هذا الملف موجود

@app.route('/control_teacher')
def control_teacher():
    return render_template('control_teacher.html', language=get_locale())  # تأكد من أن هذا الملف موجود


@app.route('/news')
def news():
    return render_template('news.html', language=get_locale())  # تأكد من أن هذا الملف موجود

@app.route('/student')
def student():
    return render_template('student.html', language=get_locale())  # تأكد من أن هذا الملف موجود



@app.route('/coun')
def coun():
    email = session.get('email', None)
    student = get_student_by_email(email)
    profile_image = student['profile_image'] if student and student.get('profile_image') else '/static/images/user.png'
    if 'email' not in session:
        print("🔴 لم يتم تسجيل الدخول - لا توجد جلسة email")
        return redirect(url_for('login'))

    print("🟢 الجلسة الحالية:", session)

    student_number = str(session.get("student_number", ""))
    result = get_student_data(student_number)

    # استخراج جميع النقاط لجميع الطلاب
    all_scores = []
    try:
        with open(STUDENTS01_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    point = float(row['points'])
                    all_scores.append(point)
                except ValueError:
                    continue
    except Exception as e:
        print(f"❌ خطأ أثناء قراءة النقاط: {e}")
    
    student_data = {
        "name": session.get("name", ""),
        "email": session.get("email", ""),
        "dob": session.get("dob", ""),
        "contact": session.get("contact", ""),
        "address": session.get("address", ""),
        "course": session.get("course", ""),
        "student_number": student_number,
        "max_point": result.get("max_point", 0),
        "min_point": result.get("min_point", 0),
        "percentage_max": result.get("percentage_max", 0),
        "percentage_min": result.get("percentage_min", 0),
        "circle_offset_max": result.get("circle_offset_max", 226.2),
        "circle_offset_min": result.get("circle_offset_min", 226.2),
        "color_min": result.get("color_min", "rgb(0,255,0)"),
        "all_scores": all_scores,

        # ✅ القيم الجديدة الخاصة بالمعدل
        "average_score": result.get("average", 0),
        "average_percentage": result.get("percentage_avg", 0),
        "circle_offset_avg": result.get("circle_offset_avg", 226.2),
        "color_avg": result.get("color_avg", "rgb(0,255,0)"),

        # ✅ بيانات أدنى معدل
        "min_average_score": result.get("min_average", 0),
        "percentage_min_avg": result.get("percentage_min_avg", 0),
        "circle_offset_min_avg": result.get("circle_offset_min_avg", 226.2),
        "color_min_avg": result.get("color_min_avg", "rgb(0,255,0)"),

        "success_average": result.get("success_average", 0),
        "success_percentage": result.get("success_percentage", 0),
        "success_offset": result.get("success_offset", 226.2),
        "success_color": result.get("success_color", "rgb(0,255,0)")

    }

    print("📦 بيانات الطالب المرسلة إلى القالب:", student_data)

    return render_template('coun.html', language=get_locale(), student=student_data, profile_image=profile_image)

@app.route('/timetable')
def timetable():
    return render_template('timetable.html', language=get_locale())  # تأكد من أن هذا الملف موجود

@app.route('/exam')
def exam():
    return render_template('exam.html', language=get_locale())  # تأكد من أن هذا الملف موجود

@app.route('/password_recovery')
def password_recovery():
    return render_template('password_recovery.html')  
# صفحة إنشاء الحساب
from flask import session

# دالة لتحميل بيانات الطلاب من ملف CSV
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# دالة لتحميل بيانات الطلاب من ملف CSV
def load_students_from_csv(file_path):
    students = []
    print(f"📂 تحميل البيانات من الملف: {file_path}")
    
    if os.path.exists(file_path):  # التحقق من وجود الملف
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print("📄 البيانات التي تم قراءتها من الصف:")
                print(row)  # طباعة البيانات التي تم قراءتها من هذا الصف
                
                # إضافة البيانات إلى قائمة الطلاب
                student_data = {
                    "id_card": row.get("id_card", "NONE"),
                    "code_massar": row.get("code_massar", "NONE"),
                    "name": row.get("name", "NONE"),
                    "email": row.get("email", "NONE"),
                    "password": row.get("password", "NONE"),
                    "role": row.get("role", "student"),
                    "subject": row.get("subject", "NONE"),  # تعيين القيمة الافتراضية لـ subject
                    "class": row.get("class", "NONE"),
                    "year": row.get("year", "NONE"),
                    "student_number": row.get("student_number", "NONE"),
                    "contact": row.get("contact", "NONE"),
                    "dob": row.get("dob", "NONE"),
                    "address": row.get("address", "NONE"),
                    "course": row.get("course", "NONE")
                }
                
                print("💾 البيانات التي سيتم إضافتها للقائمة:")
                print(student_data)  # طباعة البيانات التي سيتم إضافتها
                
                students.append(student_data)
        
        # طباعة عدد الطلاب الذين تم تحميل بياناتهم
        print(f"✅ تم تحميل {len(students)} طالب/ة من الملف.")
    
    else:
        print(f"❌ الملف {file_path} غير موجود.")
    
    return students


# دالة لإضافة الطالب إلى ملف students.csv
students_file_path = STUDENTS_FILE
def add_student_to_csv(student):
    # تحقق من وجود ملف students.csv
    if not os.path.exists(students_file_path):
        # إذا كان الملف غير موجود، أنشئه
        with open(students_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["email", "subject", "role", "name", "password", "class", "year", "id_card", "code_massar", "student_number", "contact", "dob", "address", "course"]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()  # كتابة رأس الجدول
    
    # تحميل البيانات من students.csv
    students = load_students_from_csv(students_file_path)

    # التحقق مما إذا كان الطالب مضافًا مسبقًا
    existing_student = next((s for s in students if s["id_card"] == student["id_card"] and s["code_massar"] == student["code_massar"]), None)

    if not existing_student:
        # إضافة الطالب الجديد إلى students.csv
        with open(students_file_path, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["email", "subject", "role", "name", "password", "class", "year", "id_card", "code_massar", "student_number", "contact", "dob", "address", "course"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # ترتيب القيم بالشكل الصحيح بناءً على الأعمدة
            writer.writerow({
                "email": student.get("email", "NONE"),
                "subject": student.get("subject", "NONE"),
                "role": student.get("role", "student"),
                "name": student.get("name", "NONE"),
                "password": student.get("password", "NONE"),
                "class": student.get("class", "NONE"),
                "year": student.get("year", "NONE"),
                "id_card": student.get("id_card", "NONE"),
                "code_massar": student.get("code_massar", "NONE")
            })

# دالة لتنظيف المدخلات وإزالة المسافات أو الأحرف غير المرئية
def clean_string(s):
    # التحقق إذا كانت القيمة None أو فارغة
    if s is None:
        return ""
    cleaned = s.strip().replace("ً", "")  # إزالة أي أحرف غير مرئية مثل ً في المثال
    print(f"تنظيف المدخل: {s} -> {cleaned}")
    return cleaned

@app.route('/login', methods=['GET', 'POST'])
def login():
    email_prefill = session.pop('email_prefill', '')  # جلب البريد وحذفه من الجلسة بعد الاستخدام

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        email_clean = clean_string(email)
        password_clean = clean_string(password)

        students = load_students_from_csv(students_file_path)
        student = next((s for s in students if clean_string(s["email"]) == email_clean), None)

        if student:
            if student["password"] == hash_password(password_clean):
                # تخزين جميع بيانات الطالب في الجلسة
                for key, value in student.items():
                    session[key] = value

                session['role'] = student.get('role', 'student')  # تأكيد وجود الدور

                # ✅✅ إضافة طباعة لتأكيد البيانات
                print("🔐 تسجيل دخول ناجح")
                print(f"📧 البريد: {session.get('email')}")
                print(f"🧑‍🎓 الإسم: {session.get('name')}")
                print(f"🎓 الرقم: {session.get('student_number')}")
                print(f"📅 تاريخ الميلاد: {session.get('dob')}")
                print(f"☎️ الهاتف: {session.get('contact')}")
                print(f"🏠 العنوان: {session.get('address')}")
                print(f"📘 التخصص: {session.get('course')}")
                print(f"🟢 الدور: {session.get('role')}")
                print(f"📦 الجلسة الكاملة: {dict(session)}")

                if session['role'] == 'student':
                    return redirect(url_for('dashboard'))
                elif session['role'] == 'teacher':
                    return redirect(url_for('teacher_dashboard'))
                else:
                    return redirect(url_for('home'))
            else:
                print("❌ كلمة المرور غير صحيحة.")
                return "❌ كلمة المرور غير صحيحة."
        else:
            print("❌ البريد الإلكتروني غير موجود.")
            return "❌ البريد الإلكتروني غير موجود."

    return render_template('signup.html', email_prefill=email_prefill, language=get_locale())

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html', language=get_locale())


@app.route('/', methods=['GET', 'POST'])
def homes():
    if request.method == 'POST':
        if 'buttons' in request.form:
            return redirect(url_for('buttons'))
        if 'next_step' in request.form:
            return "تم الانتقال إلى الخطوة التالية"
    
    return render_template('student.html', language=get_locale())



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # جلب البيانات من النموذج
        username = request.form.get('username')
        id_card = request.form.get('id_card')
        code_massar = request.form.get('code_massar')
        password = request.form.get('password')

        # تنظيف المدخلات
        id_card_clean = clean_string(id_card)
        code_massar_clean = clean_string(code_massar)

        # تحميل بيانات الطلاب من ملف S1.csv
        s_students = load_students_from_csv('site_college21/S1.csv')

        # البحث عن الطالب باستخدام رقم البطاقة وكود المسار
        student = next((s for s in s_students if clean_string(s["id_card"]) == id_card_clean and clean_string(s["code_massar"]) == code_massar_clean), None)

        if student:
            # الطالب موجود في S1.csv، نقوم بإضافته إلى students.csv
            student_data = {
                "id_card": id_card_clean,
                "code_massar": code_massar_clean,
                "name": student.get("name", "NONE"),  # إضافة الاسم أو تعيين "NONE" في حالة عدم وجود الاسم
                "email": student.get("email", "NONE"),  # إضافة البريد الإلكتروني أو تعيين "NONE" في حالة عدم وجوده
                "password": hash_password(password),  # تشفير كلمة المرور
                "role": "student",  # تحديد الدور كـ "student"
                "subject": "NONE",  # تعيين قيمة "NONE" للحقل subject
                "class": "S1",  # تعيين الفصل S1 كقيمة افتراضية
                "year": "2023/2024",  # تعيين السنة الدراسية كقيمة افتراضية
            }
            add_student_to_csv(student_data)  # إضافة الطالب إلى students.csv

            # حفظ بيانات المستخدم في الجلسة
            session['role'] = 'student'
            session['email'] = student_data["email"]  # تخصيص البريد الإلكتروني
            session['student_name'] = student_data["name"]  # حفظ اسم الطالب في الجلسة
            

            # إعادة التوجيه إلى صفحة تسجيل الدخول مع البريد الإلكتروني الذي تم إضافته
            session['email_prefill'] = student_data["email"]  # تخزين البريد الإلكتروني في الجلسة
            return redirect(url_for('login'))  # إعادة التوجيه بدون تمرير البريد عبر URL
        else:
            # الطالب غير موجود
            return "❌ الطالب غير موجود في سجل S1.csv."

    return render_template('signup.html', language=get_locale())



@app.route('/teacher_dashboard')
def teacher_dashboard():
    email = session.get('email', None)
    role = session.get('role', 'guest')
    print(f"Current Role: {role}, Email: {email}")  # طباعة الدور والبريد الإلكتروني لتصحيح الأخطاء

    if role != 'teacher' or not email:
        return redirect(url_for('signup'))

    # إضافة رابط خاص لكل أستاذ
    special_lessons_link = None
    teacher_subjects = {}  # معجم لتخزين المواد لكل أستاذ

    if email == 'bansalem.rj@usmba.ac.ma':
        special_lessons_link = url_for('lessons', teacher='teacher1')
        teacher_subjects = {
            email: ["topographiques", "géographie_maroc", "الاقتصاد"]
        }

    elif email == 'ali.al-baqali@usmba.ac.ma':
        special_lessons_link = url_for('lessons', teacher='teacher2')
        teacher_subjects = {
            email: ["الرياضيات", "الإحصاء", "الفيزياء"]
        }
    elif email == 'ali.ch@usmba.ac.ma':  # إضافة أستاذ ثالث
        special_lessons_link = url_for('lessons', teacher='teacher3')
        teacher_subjects = {
            email: ["اللغة الفرنسية", "الأدب", "الفلسفة"]
        }
    elif email == 'abdulsalam.sa@usmba.ac.ma':  # إضافة أستاذ رابع
        special_lessons_link = url_for('lessons', teacher='teacher4')
        teacher_subjects = {
            email: ["الكيمياء", "الأحياء", "الفيزياء"]
        }

    # احصل على المواد الخاصة بالأستاذ الحالي
    teacher_name = session.get('teacher_name', 'غير معروف')
    
    teacher_subject = teacher_subjects.get(email, [])
    readable_subjects = [subject.replace("_", " ").capitalize() for subject in teacher_subject]

    return render_template('teacher_dashboard.html', email=email, teacher_name=teacher_name, teacher_subject=teacher_subject, special_lessons_link=special_lessons_link,available_subjects=teacher_subject, language=get_locale())
# صفحة الطالب


# صفحة الدخول - يمكن أن تكون صفحة فارغة أو تحتوي على تحقق من البيانات
@app.route('/login11', methods=['GET', 'POST'])
def login11():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # تحميل بيانات الطلاب من الملف CSV
        allowed_emails = load_students_from_csv()

        user = next((u for u in allowed_emails if u['email'] == email and u['password'] == hash_password(password)), None)

        if user:
            session['email'] = user['email']
            session['role'] = user['role']
            if user['role'] == 'teacher':
                session['teacher_name'] = user.get('name', 'غير معروف')  # تخزين اسم الأستاذ
            return redirect(url_for('students_table'))
        else:
            error_message = "البريد الإلكتروني أو كلمة المرور غير صحيحة."
            return render_template('login11.html', error_message=error_message)

    return render_template('login11.html', language=get_locale())

@app.route('/submit_announcement', methods=['POST'])
def submit_announcement():
    # تحميل بيانات الطلاب من الملف CSV
    allowed_emails = load_students_from_csv(STUDENTS_FILE)

    try:
        print("🚀 بدء إضافة إعلان جديد...")

        if 'email' not in session:
            print("❌ المستخدم غير مسجل الدخول.")
            return jsonify({"success": False, "message": "يجب تسجيل الدخول"}), 401

        email = session['email']
        announcement_type = request.form['announcement-type']
        announcement_content = request.form['announcement-content']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        announcement_id = str(uuid.uuid4())

        # تحميل الإعلانات القديمة مع معالجة الأخطاء
        try:
            with open('announcements.json', 'r', encoding='utf-8') as file:
                data = file.read().strip()
                announcements = json.loads(data) if data else []
        except (FileNotFoundError, json.JSONDecodeError):
            announcements = []

       
        # إضافة الإعلان الجديد
        new_announcement = {
            "id": announcement_id,
            "type": announcement_type,
            "content": announcement_content,
            "timestamp": timestamp,
            "email": email,
            "teacher_name": next((user["name"] for user in allowed_emails if user["email"] == email), "غير متوفر")
        }
        announcements.append(new_announcement)
        print(f"✅ إعلان مضاف: {new_announcement}")

        # حفظ البيانات بطريقة آمنة
        temp_file = 'announcements_temp.json'
        with open(temp_file, 'w', encoding='utf-8') as file:
            json.dump(announcements, file, ensure_ascii=False, indent=4)

        os.replace(temp_file, 'announcements.json')

        # طباعة المحتوى بعد الحفظ لمراقبة المشكلة
        with open('announcements.json', 'r', encoding='utf-8') as file:
            print("📄 محتوى announcements.json بعد الحفظ:", file.read())

        return jsonify({"success": True})

    except Exception as e:
        print(f"⚠️ خطأ أثناء إضافة الإعلان: {e}")
        return jsonify({"success": False}), 500
    
@app.route('/get_announcements')
def get_announcements():
    allowed_users = load_students_from_csv(STUDENTS_FILE)

    try:
        print("🚀 بدء جلب الإعلانات...")

        if 'email' not in session:
            print("❌ المستخدم غير مسجل الدخول.")
            return jsonify({"success": False, "message": "يجب تسجيل الدخول"}), 401

        current_email = session['email']

        try:
            with open('announcements.json', 'r', encoding='utf-8') as file:
                announcements = json.load(file)
                if not isinstance(announcements, list):
                    announcements = []
        except (FileNotFoundError, json.JSONDecodeError):
            announcements = []

        # جلب معلومات المستخدم الحالي
        user_info = next((user for user in allowed_users if user["email"] == current_email), None)
        role = user_info.get("role", "student") if user_info else "student"

        if role == "teacher":
            # عرض فقط الإعلانات التي نشرها الأستاذ
            announcements = [ann for ann in announcements if ann.get("email") == current_email]

        # إضافة اسم الأستاذ لكل إعلان
        for ann in announcements:
            ann.setdefault("teacher_name", next(
                (user["name"] for user in allowed_users if user["email"] == ann.get("email")), "غير متوفر"
            ))

        print(f"✅ تم تحميل {len(announcements)} إعلانًا.")
        return jsonify(announcements)

    except Exception as e:
        print(f"⚠️ خطأ أثناء جلب الإعلانات: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/view_announcements')
def view_announcements():
    try:
        print("Loading announcements for view_announcements route...")
        with open('announcements.json', 'r', encoding='utf-8') as file:
            announcements = json.load(file)
            print(f"Loaded {len(announcements)} announcements.")
    except (FileNotFoundError, json.JSONDecodeError):
        announcements = []
        print("No announcements found or invalid file format.")

    return render_template('announcement_list.html', announcements=announcements, language=get_locale())

@app.route('/delete_announcement/<string:id>', methods=['DELETE'])
def delete_announcement(id):
    try:
        print(f"Deleting announcement with ID: {id}")
        with open('announcements.json', 'r', encoding='utf-8') as file:
            announcements = json.load(file)
            print(f"Loaded {len(announcements)} announcements.")

        announcements = [announcement for announcement in announcements if announcement['id'] != id]
        print(f"Remaining announcements after deletion: {len(announcements)}")

        with open('announcements.json', 'w', encoding='utf-8') as file:
            json.dump(announcements, file, ensure_ascii=False, indent=4)
            print("Updated announcements saved to file.")

        return jsonify({"success": True})

    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        return jsonify({"success": False}), 500
    

@app.route('/buttons')
def buttons():
    return render_template('buttons.html', language=get_locale())  # تأكد من أن هذا الملف موجود

@app.route('/Student_space')
def Student_space():
    return render_template('Student_space.html', language=get_locale())  # تأكد من أن هذا الملف موجود

     
def load_students(file_path, teacher_subject=None, student_number=None):
    """ تحميل بيانات الطلاب من ملف CSV مع تصفية حسب المادة أو رقم الطالب """
    temp_students = []
    
    if os.path.exists(os.path.join(BASE_DIR, file_path)):
        with open(os.path.join(BASE_DIR, file_path), newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row = {key.strip(): (value.strip() if value else '') for key, value in row.items()}

                if 'student_number' not in row or not row['student_number']:
                    continue

                # إذا كان هناك رقم طالب، يجب مطابقته
                if student_number and row['student_number'].strip() != student_number.strip():
                    continue

                # إذا كان الملف الأساسي، يجب مطابقة المادة
                if teacher_subject and file_path.startswith("students") and row.get('subject', '').strip() != teacher_subject.strip():
                    continue

                temp_students.append(row)

    return temp_students
# ------------------------- تغيير كلمة المرور بصفحة password ----------------------------
@app.route('/password')
def password():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('password.html')

from flask import Flask, render_template, request, redirect, url_for, session, flash

CSV_FILE = STUDENTS_FILE
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'email' not in session:
        return redirect(url_for('login'))

    email = session['email']
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if new_password != confirm_password:
        flash('كلمة المرور الجديدة وتأكيدها غير متطابقين.', 'danger')
        return render_template('password.html', active_form="login")

    updated = False
    rows = []

    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['email'] == email:
                if row['password'] == hash_password(current_password):
                    row['password'] = hash_password(new_password)
                    updated = True
                else:
                    flash('كلمة المرور الحالية غير صحيحة.', 'danger')
                    return render_template('password.html', active_form="login")
            rows.append(row)

    if updated:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        flash('تم تغيير كلمة المرور بنجاح.', 'success')
    else:
        flash('لم يتم العثور على المستخدم أو حدث خطأ.', 'danger')

    return render_template('password.html', active_form="login")


@app.route('/reset_password', methods=['POST'])
def reset_password():
    code_massar = request.form['username']
    id_card = request.form['id_card']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if new_password != confirm_password:
        flash('كلمة المرور الجديدة وتأكيدها غير متطابقين.', 'danger')
        return render_template('password.html', active_form="signup")

    updated = False
    rows = []

    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['id_card'] == id_card and row['code_massar'] == code_massar:
                row['password'] = hash_password(new_password)
                updated = True
            rows.append(row)

    if updated:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        flash('تم إعادة تعيين كلمة المرور بنجاح.', 'success')
    else:
        flash('لم يتم العثور على بيانات مطابقة.', 'danger')

    return render_template('password.html', active_form="signup")

@app.route('/forgot_password')
def forgot_password():
    return render_template('password.html')


# -------------------------
# ------------------------- الجزء الخاص بالرسائل و حفضها و تحميلها في صفحة الطالب ----------------
MESSAGE_FILE = MESSAGE_FILE
# تأكد من أن المجلد الذي يحتوي على الملف موجود
if not os.path.exists(os.path.dirname(MESSAGE_FILE)):
    os.makedirs(os.path.dirname(MESSAGE_FILE))

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        # التحقق من البيانات المرسلة
        data = request.get_json()
        name = data.get("name")
        message = data.get("message")
        email = data.get("email", "")  # إذا لم يكن البريد موجودًا سيأخذ قيمة فارغة
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # الوقت الحالي

        # طباعة البيانات المستلمة للتحقق منها
        print(f"Received data: name={name}, message={message}, email={email}, timestamp={timestamp}")

        # تأكد من أن الرسالة والبريد ليست فارغة
        if not message or not name:
            return jsonify({"status": "error", "message": "البيانات غير مكتملة"}), 400
        
        # محاولة حفظ الرسالة في ملف CSV مع الوقت والبريد الشخصي
        with open(MESSAGE_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([name, email, message, timestamp])  # إضافة البريد والوقت (البريد قد يكون فارغًا)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Error saving message: {e}")
        return jsonify({"status": "error", "message": f"حدث خطأ أثناء حفظ الرسالة: {str(e)}"}), 500

@app.route('/messages')
def get_messages():
    messages = []
    try:
        with open(MESSAGE_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 4:
                    name, email, message, timestamp = row
                    messages.append({
                        'name': name,
                        'email': email,
                        'message': message,
                        'timestamp': timestamp
                    })
    except FileNotFoundError:
        pass

    return jsonify(messages)


@app.route('/delete_message', methods=['POST'])
def delete_message():
    try:
        data = request.get_json()
        message_text = data.get("messageText").strip()  # إزالة الفراغات من النص
        timestamp = data.get("timestamp").strip()  # إزالة الفراغات من التوقيت

        # طباعة البيانات التي وصلتنا
        print(f"Received data for deletion: messageText={message_text}, timestamp={timestamp}")

        updated_rows = []
        deleted = False

        # فتح الملف وقراءة البيانات
        with open(MESSAGE_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 4:
                    continue  # تخطي الصفوف غير المكتملة
                name, email, message, time = row
                # بناء الرسالة بدون البريد الإلكتروني
                full_message = f"{name}: {message}".strip()  # تأكد من إزالة الفراغات

                # طباعة الرسائل للتحقق من المطابقة
                print(f"Full message: {full_message} vs messageText: {message_text}")
                print(f"Checking time: {time} vs timestamp: {timestamp}")

                # إزالة الفراغات من الوقت أيضًا
                time = time.strip()

                # تحقق إذا كانت الرسالة والتوقيت مطابقين
                if full_message == message_text and time == timestamp:
                    print(f"Message matched and will be deleted: {full_message}")
                    deleted = True
                    continue
                updated_rows.append(row)

        if deleted:
            with open(MESSAGE_FILE, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(updated_rows)

            print("Message deleted successfully.")
            return jsonify({"status": "success"}), 200
        else:
            print("Message not found for deletion.")
            return jsonify({"status": "error", "message": "لم يتم العثور على الرسالة"}), 404

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------------------------------- الجزء المخصص لنشر إعلانات من طرف الاستاذ و حفضها في الملف ---------------------------------------------
@app.route('/ads', methods=['GET', 'POST'])
def ads():
    if request.method == 'POST':
        # تحويل start_time إلى نفس صيغة CSV
        raw_time = request.form.get("start_time")
        try:
            formatted_time = datetime.strptime(raw_time, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M")
        except Exception as e:
            formatted_time = ""  # في حال حدوث خطأ، نتركها فارغة أو نرسل إشعار
        
        ad = {
            "title": request.form.get("title"),
            "content": request.form.get("content"),
            "start_time": formatted_time,
            "priority": request.form.get("priority")
        }

        if not ad_already_exists(ad, ADS_FILE):
            save_ad_to_csv(ad)
            flash("✅ تم إضافة الإعلان بنجاح!", "success")
        else:
            flash("⚠️ هذا الإعلان موجود مسبقًا!", "warning")
        
        return redirect(url_for("ads"))

    return render_template("ads.html", language=get_locale())

def ad_already_exists(new_ad, file_path):
    """تفحص إذا كان الإعلان موجود مسبقًا في الملف"""
    if not os.path.exists(file_path):
        return False

    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if (row["title"] == new_ad["title"] and
                row["content"] == new_ad["content"] and
                row["start_time"] == new_ad["start_time"]):
                return True
    return False



def save_ad_to_csv(ad_data, file_path=ADS_FILE):
    # تحديد الحقول التي سيتم تخزينها في الإعلان
    fieldnames = ["title", "content", "start_time", "priority", "created_at"]

    # فتح الملف بطريقة كتابة (أو الإنشاء إذا لم يكن موجودًا)
    try:
        with open(file_path, mode="a", newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            # إذا كان الملف فارغًا، نقوم بكتابة العناوين
            if file.tell() == 0:
                writer.writeheader()

            # إضافة البيانات الخاصة بالإعلان
            ad_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # إضافة الوقت الحالي
            writer.writerow(ad_data)
            print("تم حفظ الإعلان بنجاح!")
    except Exception as e:
        print(f"خطأ في حفظ الإعلان: {e}")

# مثال على كيفية استدعاء الدالة:
ad = {
    "title": "إعلان جديد",
    "content": "هذا هو محتوى الإعلان الجديد",
    "start_time": "2025-04-20 09:00",
    "priority": "عالي"
}

save_ad_to_csv(ad)


# ---------------------------------------- الجزء الخاص بتحميل أعلى و أدنى نقطة للطلاب في صفحة coun ---------------------------------------------


def get_gradient_color(percent):
    # من 0 إلى 100 => أخضر إلى أحمر
    r = int((percent / 100) * 255)
    g = int((1 - (percent / 100)) * 255)
    return f'rgb({r},{g},0)'

def get_gradient_color_max(percent):
    # من 0 إلى 100 => أحمر إلى أخضر (اللون يتحول من الأحمر إلى الأخضر)
    r = int((1 - (percent / 100)) * 255)  # الأحمر يتناقص مع زيادة النسبة
    g = int((percent / 100) * 255)        # الأخضر يزيد مع زيادة النسبة
    return f'rgb({r},{g},0)'



def get_student_data(student_number):
    import csv
    import math
    from collections import defaultdict

    files = [
        STUDENTS01_FILE,
        STUDENTS02_FILE
    ]

    student_data = {
        'all_scores': [],
        'scores_by_file': {},
        'max': {'point': -1, 'file': None},
        'min': {'point': 21, 'file': None}
    }

    file_data = {}
    averages_by_file = {}

    for file_path in files:
        max_points = {}
        min_points = {}
        total_points = defaultdict(float)
        count_points = defaultdict(int)
        scores = []

        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        sn = row['student_number'].strip()
                        point = float(row['points'])

                        total_points[sn] += point
                        count_points[sn] += 1

                        max_points[sn] = max(max_points.get(sn, point), point)
                        min_points[sn] = min(min_points.get(sn, point), point)

                        if sn == student_number.strip():
                            scores.append(point)
                            if point > student_data['max']['point']:
                                student_data['max']['point'] = point
                                student_data['max']['file'] = file_path
                            if point < student_data['min']['point']:
                                student_data['min']['point'] = point
                                student_data['min']['file'] = file_path
                    except ValueError:
                        continue

            file_data[file_path] = {
                'max_points': max_points,
                'min_points': min_points,
                'total_points': total_points,
                'count_points': count_points
            }

            if scores:
                student_data['scores_by_file'][file_path] = scores
                student_data['all_scores'].extend(scores)

            # ✅ نحسب المعدل لهذا الملف إذا الطالب له 7 مواد
            if len(scores) == 7:
                avg = sum(scores) / 7
                averages_by_file[file_path] = avg

        except Exception as e:
            print(f"❌ خطأ في قراءة {file_path}:", e)

    if not student_data['all_scores']:
        return default_result()

    def calculate_metrics(score_type):
        file_path = student_data[score_type]['file']
        student_score = student_data[score_type]['point']
        points = file_data[file_path][
            'max_points' if score_type == 'max' else 'min_points'
        ].values()

        if score_type == 'max':
            rank = sum(1 for p in points if p < student_score)
            total = len(points)
            percentile = (rank / (total - 1)) * 100 if total > 1 else 100
        else:
            min_all = min(points)
            max_all = max(points)
            if max_all - min_all == 0:
                percentile = 100
            else:
                percentile = 100 - ((student_score - min_all) / (max_all - min_all) * 100)

        circle_circumference = 2 * math.pi * 36
        offset = circle_circumference - (circle_circumference * percentile / 100)
        return percentile, offset

    def calculate_average(is_max=True):
        best_value = -1 if is_max else 21
        best_file = None
        best_avg = 0

        for file_path, scores in student_data['scores_by_file'].items():
            if len(scores) == 7:
                avg = sum(scores) / 7
                if (is_max and avg > best_value) or (not is_max and avg < best_value):
                    best_value = avg
                    best_file = file_path

        if best_file:
            all_averages = [
                file_data[best_file]['total_points'][sn] / 7
                for sn in file_data[best_file]['total_points']
                if file_data[best_file]['count_points'][sn] == 7
            ]
            ref_avg = max(all_averages) if is_max else min(all_averages)
            percentage = (best_value / ref_avg) * 100 if ref_avg != 0 else 100
            percentage = max(0, min(100, percentage))
            circle_circumference = 2 * math.pi * 36
            offset = circle_circumference - (circle_circumference * percentage / 100)
            return best_value, percentage, offset, best_file, all_averages
        return 0, 0, 226.2, None, []

    student_max = student_data['max']['point']
    student_min = student_data['min']['point']

    percentile_max, offset_max = calculate_metrics('max')
    percentile_min, offset_min = calculate_metrics('min')

    avg, percentage_avg, offset_avg, avg_file, all_avg_list = calculate_average(is_max=True)
    min_avg, percentage_min_avg, offset_min_avg, min_avg_file, all_min_list = calculate_average(is_max=False)

    # ✅ حساب معدل النجاح العام
    success_average = 0
    if len(averages_by_file) == 2:
        success_average = (list(averages_by_file.values())[0] + list(averages_by_file.values())[1]) / 2
    elif len(averages_by_file) == 1:
        success_average = list(averages_by_file.values())[0]

    success_percentage = (success_average / 20) * 100 if success_average > 0 else 0
    success_circle = 2 * math.pi * 36
    success_offset = success_circle - (success_circle * success_percentage / 100)

    return {
        'min_point': round(student_min, 1),
        'max_point': round(student_max, 1),
        'average': round(avg, 1),
        'percentage_avg': round(percentage_avg, 1),
        'circle_offset_avg': round(offset_avg, 1),
        'color_avg': get_gradient_color_max(percentage_avg),
        'higher_than_max': sorted(
            [p for p in file_data[student_data['max']['file']]['max_points'].values() if p > student_max],
            reverse=True
        )[:5],
        'percentage_max': round(percentile_max, 1),
        'circle_offset_max': round(offset_max, 1),
        'percentage_min': round(percentile_min, 1),
        'circle_offset_min': round(offset_min, 1),
        'color_min': get_gradient_color(percentile_min),
        'all_scores': student_data['all_scores'],
        'min_average': round(min_avg, 1),
        'percentage_min_avg': round(percentage_min_avg, 1),
        'circle_offset_min_avg': round(offset_min_avg, 1),
        'color_min_avg': get_gradient_color(percentage_min_avg),
        'lower_than_min_avg': sorted(
            [a for a in all_min_list if a < min_avg]
        )[:5],

        # ✅ بيانات نسبة النجاح
        'success_average': round(success_average, 1),
        'success_percentage': round(success_percentage, 1),
        'success_offset': round(success_offset, 1),
        'success_color': get_gradient_color_max(success_percentage),
    }

def default_result():
    return {
        'min_point': 0,
        'max_point': 0,
        'higher_than_max': [],
        'percentage_max': 0,
        'circle_offset_max': 226.2,
        'percentage_min': 0,
        'circle_offset_min': 226.2,
        'all_scores': []
    }


# -----------------------------------------------------------------------------------------------------------

print("المسار الكامل لملف الطلاب:", STUDENTS_FILE)
print("هل الملف موجود؟", os.path.exists(STUDENTS_FILE))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_student_by_email(email):
    with open(STUDENTS_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['email'] == email:
                return row
    return None

def update_student_image(email, image_url):
    students = []
    updated = False
    with open(STUDENTS_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row['email'] == email:
                row['profile_image'] = image_url
                updated = True
            students.append(row)
    if updated:
        with open(STUDENTS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(students)

@app.route('/dashboard')
def dashboard():
    email = session.get('email', None)
    role = session.get('role', 'guest')

    if not email or role != 'student':
        return redirect(url_for('signup'))

    student = get_student_by_email(email)
    
    # التأكد من أن الصورة موجودة في بيانات الطالب في الـ CSV
    profile_image = student['profile_image'] if student and student.get('profile_image') and student['profile_image'].strip() else '/static/images/user.png'

    
    # تخزين الصورة في الجلسة ليتم استخدامها لاحقًا
    session['profile_image'] = profile_image

    return render_template('dashboard.html', profile_image=profile_image, email=email, language='ar')

@app.route('/upload', methods=['POST'])
def upload_image():
    email = session.get('email')
    if not email:
        return 'Unauthorized', 401

    if 'image' not in request.files:
        return 'No file part', 400
    file = request.files['image']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        # 🟢 نحفظ الصورة باسم البريد بدون الرموز (لكل مستخدم صورة خاصة)
        safe_email = email.replace('@', '_').replace('.', '_')
        filename = f"{safe_email}.{ext}"
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Saving file to: {full_path}")
        file.save(full_path)

        timestamp = int(time.time())
        image_url = f'/static/uploads/{filename}?t={timestamp}'
        session['profile_image'] = image_url  # تخزين مؤقت
        update_student_image(email, f'/static/uploads/{filename}')  # تخزين دائم في CSV بدون timestamp

        return jsonify({"image_url": image_url}), 200
    return 'File not allowed', 400

@app.route('/save-suggested-image', methods=['POST'])
def save_suggested_image():
    email = session.get('email')
    if not email:
        return 'Unauthorized', 401

    data = request.get_json()
    image_url = data.get('image_url')

    session['profile_image'] = image_url
    update_student_image(email, image_url)  # نحفظ في CSV أيضاً

    return jsonify({"message": "Image saved successfully"}), 200

@app.route('/account')
def account():
    email = session.get('email', None)
    student = get_student_by_email(email)
    profile_image = student['profile_image'] if student and student.get('profile_image') else '/static/images/user.png'
    return render_template('account.html', profile_image=profile_image)






@app.route('/get-profile-image')
def get_profile_image():
    email = session.get('email', None)
    student = get_student_by_email(email)
    profile_image = student['profile_image'] if student and student.get('profile_image') else '/static/images/user.png'
    return jsonify({'profile_image': profile_image})


# -----------------------------------------------------------------------------------------------------------

@app.route('/get_students', methods=['GET'])
def get_students():
    """إرجاع الطلاب بناءً على الزر الذي تم الضغط عليه، مع إعطاء أولوية للملف الأساسي ثم الثانوي"""
    selected_section = request.args.get('selected_file', 'S1')  # جلب القسم المحدد
    
    file_map = {
        'S1': ('students01.csv', 'S1.csv'),
        'S2': ('students02.csv', 'S2.csv'),
        'S3': ('students03.csv', 'S3.csv'),
        'S4': ('students04.csv', 'S4.csv'),
        'S5': ('students05.csv', 'S5.csv'),
        'S6': ('students06.csv', 'S6.csv'),
    }

    primary_file, secondary_file = file_map.get(selected_section, ('students01.csv', 'S1.csv'))
    students = load_students(primary_file, secondary_file)  # تحميل البيانات مع الأولوية
    return jsonify(students)

def find_student_in_classes(student_number, teacher_subject, selected_file):
    """ البحث عن طالب معين في الملفات الخاصة بالقسم المحدد """
    
    file_map = {
        'S1': ('students01.csv', 'S1.csv'),
        'S2': ('students02.csv', 'S2.csv'),
        'S3': ('students03.csv', 'S3.csv'),
        'S4': ('students04.csv', 'S4.csv'),
        'S5': ('students05.csv', 'S5.csv'),
        'S6': ('students06.csv', 'S6.csv'),
    }

    primary_file, secondary_file = file_map.get(selected_file, ('students01.csv', 'S1.csv'))

    print(f"🔎 البحث عن الطالب {student_number} في الملفات: {primary_file}, {secondary_file}")

    # البحث في الملف الأساسي مع شرط المادة
    student_data = load_students(primary_file, teacher_subject=teacher_subject, student_number=student_number)
    
    if student_data:
        print(f"✅ الطالب {student_number} موجود في {primary_file}.")
        return student_data[0], primary_file

    # البحث في الملف الثانوي بدون شرط المادة
    student_data = load_students(secondary_file, student_number=student_number)

    if student_data:
        print(f"✅ الطالب {student_number} موجود في {secondary_file}.")
        return student_data[0], secondary_file

    print(f"❌ الطالب {student_number} غير موجود في {primary_file} أو {secondary_file}.")
    return None, None


@app.route('/get_student_info', methods=['GET'])
def get_student_info():
    """ البحث عن بيانات الطالب في الملف الأساسي والاحتياطي وفقًا للزر المختار """
    student_number = request.args.get('number')
    selected_file = session.get('selected_file', 'S1')
    teacher_subject = session.get('teacher_subject', '')

    print(f"📥 استعلام عن الطالب: {student_number}, الملف المحدد: {selected_file}, المادة: {teacher_subject}")

    if not student_number:
        return jsonify({"error": "❌ رقم الطالب غير محدد!"})

    if not teacher_subject:
        return jsonify({"error": "❌ اسم المادة غير محدد!"})

    # البحث عن الطالب في الملفات الخاصة بالقسم المحدد
    student_data, source_file = find_student_in_classes(student_number, teacher_subject, selected_file)

    if student_data:
        print(f"✅ الطالب {student_number} موجود في {source_file}.")
        return jsonify(student_data)

    return jsonify({"error": f"⚠️ الطالب {student_number} غير موجود في {source_file}!"})

@app.route('/set_selected_file', methods=['POST'])
def set_selected_file():
    data = request.get_json()
    selected_file = data.get('file_name')

    if selected_file:
        session['selected_file'] = selected_file
        print(f"تم تحديد الملف: {selected_file}")  # تتبع الملف الذي تم تحديده
        return jsonify({'message': f'تم تحديد الملف {selected_file} بنجاح'}), 200

    print("⚠️ لم يتم إرسال اسم الملف")  # تتبع حالة عدم إرسال اسم الملف
    return jsonify({'error': '⚠️ لم يتم إرسال اسم الملف'}), 400


def save_student_to_file(student, file_name):
    """تحديث بيانات الطالب في الملف أو إضافته إذا لم يكن موجودًا، مع التأكد من حفظ جميع الحقول."""
    file_path = os.path.join(BASE_DIR, file_name)

    required_columns = ['student_number', 'name', 'name_ar', 'id_card', 'code_massar', 'points', 'subject']

    # التأكد من أن الملف موجود، وإذا لم يكن كذلك، إنشاؤه مع الحقول المطلوبة
    if not os.path.exists(file_path):
        print(f"⚠️ الملف {file_name} غير موجود، سيتم إنشاؤه.")
        pd.DataFrame([student]).to_csv(file_path, index=False, encoding='utf-8', columns=required_columns)
        return

    try:
        students_df = pd.read_csv(file_path, dtype=str)

        # التأكد من أن جميع الأعمدة المطلوبة موجودة
        for col in required_columns:
            if col not in students_df.columns:
                students_df[col] = ''

        student_index = students_df[
            (students_df['student_number'] == student['student_number']) & 
            (students_df['subject'] == student['subject'])
        ].index

        if not student_index.empty:
            # تحديث جميع بيانات الطالب وليس فقط النقاط
            for key in required_columns:
                students_df.loc[student_index, key] = student.get(key, '')
            print(f"✅ تم تحديث بيانات الطالب {student['student_number']} في {file_name}.")
        else:
            # إضافة الطالب إذا لم يكن موجودًا
            print(f"⚠️ الطالب {student['student_number']} غير موجود في {file_name}، سيتم إضافته.")
            new_student = {col: student.get(col, '') for col in required_columns}
            students_df = pd.concat([students_df, pd.DataFrame([new_student])], ignore_index=True)

        # حفظ التغييرات إلى الملف
        students_df.to_csv(file_path, index=False, encoding='utf-8')

        # **التحقق من أن البيانات حُفظت فعلًا**
        print(f"📁 تم حفظ البيانات في {file_path}")
        print(students_df.to_string())

    except Exception as e:
        print(f"❌ خطأ أثناء تحديث {file_name}: {e}")



@app.route('/update_student', methods=['POST'])
def update_student():
    try:
        student_data = request.get_json()
        student_number = student_data['student_number']
        points = student_data['points']
        teacher_subject = session.get('teacher_subject', '')
        selected_file = session.get('selected_file', 'S1')  # إضافة هذا السطر لجلب الملف المحدد

        print(f"🔄 تحديث نقاط الطالب {student_number} إلى {points} في المادة {teacher_subject}")

        # تمرير selected_file عند استدعاء الدالة
        student, found_file = find_student_in_classes(student_number, teacher_subject, selected_file)

        if student and found_file:
            student['points'] = points  # تحديث النقاط
            save_student_to_file(student, found_file)  # حفظ التحديث
            return jsonify({'success': True, 'message': 'تم تحديث النقاط بنجاح'}), 200
        else:
            print(f"❌ الطالب {student_number} غير موجود في مادة الأستاذ.")
            return jsonify({'success': False, 'error': 'الطالب غير مسجل في مادة الأستاذ'}), 404

    except Exception as e:
        print(f"❌ خطأ أثناء التحديث: {e}")
        return jsonify({'error': 'حدث خطأ أثناء التحديث'}), 500


@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.get_json()
    student_number = data.get('student_number')
    points = data.get('points')

    if not student_number or not points:
        return jsonify({'success': False, 'error': 'بيانات غير مكتملة'}), 400

    selected_file = session.get('selected_file', 'S1')
    print(f"تم استخدام الملف: {selected_file}")  

    file_map = {
        'S1': 'students01.csv',
        'S2': 'students02.csv',
        'S3': 'students03.csv',
        'S4': 'students04.csv',
        'S5': 'students05.csv',
        'S6': 'students06.csv',
    }

    file_name = file_map.get(selected_file, 'students01.csv')

    # 🔍 البحث عن بيانات الطالب الحقيقية في الملف
    existing_students = load_students(file_name)
    student_in_file = next((s for s in existing_students if s['student_number'] == student_number), None)

    if student_in_file:
        student_in_file['points'] = points
        student_in_file['subject'] = session.get('teacher_subject', '')
        save_student_to_file(student_in_file, file_name)
        return jsonify({'success': True, 'message': f'تم تحديث الطالب {student_number} في {file_name}'}), 200
    else:
        # 🔄 جلب بيانات الطالب من `S2.csv` أو الملف الثانوي
        secondary_file = f"S{selected_file[-1]}.csv"
        students_secondary = load_students(secondary_file)

        found_student = next((s for s in students_secondary if s['student_number'] == student_number), None)

        new_student = {
            'student_number': student_number,
            'points': points,
            'subject': session.get('teacher_subject', ''),
            'name': found_student['name'] if found_student else 'N/A',
            'name_ar': found_student['name_ar'] if found_student else 'غير معروف',
            'id_card': found_student['id_card'] if found_student else 'غير متوفر',
            'code_massar': found_student['code_massar'] if found_student else 'غير متوفر',
        }

        save_student_to_file(new_student, file_name)
        return jsonify({'success': True, 'message': f'تم إضافة الطالب {student_number} إلى {file_name}'}), 200


@app.route('/save_students_table', methods=['POST'])
def save_students_table():
    students_data = request.form.get('students_data')
    session['saved_students'] = students_data
    return '', 204  # لا نحتاج لإعادة توجيه، فقط نحفظ البيانات

@app.route('/view_saved_students_table')
def view_saved_students_table():
    students_data = session.get('saved_students')
    if not students_data:
        return "لا توجد بيانات محفوظة.", 404
    students = eval(students_data)  # أو json.loads(students_data)
    return render_template('saved_students_table.html', students=students, language=get_locale())

@app.route('/manual_input')
def manual_input():
    number = request.args.get('number')
    name = request.args.get('name')
    name_ar = request.args.get('nameAr')
    id_card = request.args.get('id_card')
    code_massar = request.args.get('code_massar')
    points = request.args.get('points')

    # تحقق من القيم المرسلة
    print(f"استلام البيانات - رقم الطالب: {number}, الاسم: {name}, النقاط: {points}")

    # إرسال القيم إلى النموذج
    return render_template("manual_input.html", number=number, name=name, name_ar=name_ar, id_card=id_card, code_massar=code_massar, points=points, language=get_locale())

@app.route('/students_table/<filename>')
def get_student_file(filename):
    file_path = os.path.join(BASE_DIR, filename)
    print(f"محاولة فتح الملف: {file_path}")  # تتبع مسار الملف
    
    if not os.path.exists(file_path):
        print(f"الملف {filename} غير موجود.")  # تتبع حالة الملف غير موجود
        return jsonify({"error": "الملف غير موجود"}), 404
    
    return send_from_directory(BASE_DIR, filename)



@app.route('/students_table')
def students_table():
    class_name = request.args.get('class', 'S1')

    # 🔹 جلب بيانات الأستاذ من الجلسة
    teacher_name = session.get('teacher_name', 'غير معروف')
    teacher_subject = session.get('teacher_subject', 'غير معروف')

    print(f"👨‍🏫 استرجاع بيانات المعلم من الجلسة: {teacher_name} - {teacher_subject}")  # تتبع

    file_name = f"students{class_name[-1]}.csv"

    if len(class_name) > 1 and class_name[1] != '0':
        file_name = f"students0{class_name[-1]}.csv"

    file_path = os.path.join(BASE_DIR, file_name)

    if not os.path.exists(file_path):
        return jsonify({"error": "الملف غير موجود"}), 404

    students = []
    with open(file_path, "r", encoding="utf-8") as file:
        header = file.readline().strip().split(",")
        for line in file:
            values = line.strip().split(",")
            student = dict(zip(header, values))
            students.append(student)

    # ✅ تصفية الطلاب بناءً على المادة
    if teacher_subject != "غير معروف":
        students = [s for s in students if s.get('subject') == teacher_subject]

    print(f"📊 عدد الطلاب بعد التصفية: {len(students)}")  # تتبع عدد الطلاب بعد التصفية

    return render_template('students_table.html', students=students, teacher_name=teacher_name, teacher_subject=teacher_subject, language=get_locale())




@app.route('/get_students_by_class', methods=['GET'])
def get_students_by_class():
    """إرجاع الطلاب بناءً على المادة الخاصة بالأستاذ."""
    teacher_subject = session.get('teacher_subject', '')  # الحصول على مادة الأستاذ من الجلسة
    if not teacher_subject:
        return jsonify({"error": "لم يتم تحديد مادة الأستاذ"}), 400  # التأكد من وجود مادة للأستاذ
    
    class_name = request.args.get('class')  # الحصول على الفصل المطلوب من المستخدم
    print(f"استلام طلب الطلاب لفصل: {class_name} لمادة {teacher_subject}")  # تتبع الطلب
    
    file_map = {
        'S1': 'students01.csv',
        'S2': 'students02.csv',
        'S3': 'students03.csv',
        'S4': 'students04.csv',
        'S5': 'students05.csv',
        'S6': 'students06.csv',
    }
    
    file_name = file_map.get(class_name)
    if not file_name:
        print(f"الفصل {class_name} غير موجود في الخريطة.")  # تتبع حالة الفصل غير الموجود
        return jsonify([])  # أو رسالة خطأ مناسبة
    
    print(f"تم العثور على الملف: {file_name}")  # تتبع الملف الذي تم العثور عليه
    students = load_students(file_name, teacher_subject=teacher_subject)  # تحميل الطلاب بناءً على المادة
    return jsonify(students)  # إرجاع البيانات في شكل JSON

# ----------------------------------- فضاء الطالب -----------------------------------

@app.route('/Login_tudent_space')
def Login_tudent_space():
    return render_template('Login_tudent_space.html', language=get_locale())  # تأكد من أن هذا الملف موجود

files = [os.path.join(BASE_DIR, f'students0{i}.csv') for i in range(1, 7)]

# تعيين المستوى بناءً على اسم الملف
def determine_level(file_name):
    if "students01.csv" in file_name or "S1.csv" in file_name:
        return "الفصل الأول"
    elif "students02.csv" in file_name or "S2.csv" in file_name:
        return "الفصل الثاني"
    elif "students03.csv" in file_name or "S3.csv" in file_name:
        return "الفصل الثالث"
    elif "students04.csv" in file_name or "S4.csv" in file_name:
        return "الفصل الرابع"
    elif "students05.csv" in file_name or "S5.csv" in file_name:
        return "الفصل الخامس"
    elif "students06.csv" in file_name or "S6.csv" in file_name:
        return "الفصل السادس"
    return "غير معروف"

# تعيين الملاحظات بناءً على النقطة
def determine_notes(average):
    if average.lower() == "absent":
        return '<span style="color: red;">غائب</span>'
    try:
        avg = float(average)
        if avg >= 10:
            return '<span style="color: green;">مستوف</span>'
        else:
            return '<span style="color: orange;">مستدرك</span>'
    except ValueError:
        return "-"

# البحث عن الطالب في ملفات CSV

def search_student(id_card, code_massar):
    student_data = []

    # ترتيب الملفات من الأحدث إلى الأقدم
    files = [
        os.path.join(DATA_DIR, 'students06.csv'),
        os.path.join(DATA_DIR, 'S6.csv'),
        os.path.join(DATA_DIR, 'students05.csv'),
        os.path.join(DATA_DIR, 'S5.csv'),
        os.path.join(DATA_DIR, 'students04.csv'),
        os.path.join(DATA_DIR, 'S4.csv'),
        os.path.join(DATA_DIR, 'students03.csv'),
        os.path.join(DATA_DIR, 'S3.csv'),
        os.path.join(DATA_DIR, 'students02.csv'),
        os.path.join(DATA_DIR, 'S2.csv'),
        os.path.join(DATA_DIR, 'students01.csv'),
        os.path.join(DATA_DIR, 'S1.csv')
    ]

    for file in files:
        print(f"فحص الملف: {file}")  # طباعة اسم الملف الذي يتم فحصه
        if not os.path.exists(file):
            print(f"الملف {file} غير موجود.")
            continue

        level = determine_level(file)  # تعيين المستوى من اسم الملف
        print(f"المستوى المعين: {level}")

        with open(file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_cne = clean_text(row.get('id_card', ''))
                csv_code_m = clean_text(row.get('code_massar', ''))
                points = row.get('points', '').strip()
                student_number = row.get('student_number', '').strip()

                # طباعة القيم التي تم استخراجها من الصف
                print(f"البيانات المستخلصة - id_card: {csv_cne}, code_massar: {csv_code_m}, points: {points}, student_number: {student_number}")

                # التحقق من تطابق id_card و code_massar
                if csv_cne == id_card and csv_code_m == code_massar:
                    print(f"تم العثور على الطالب: {student_number}, {csv_cne}")  # طباعة الطالب الذي تم العثور عليه
                    # إضافة جميع المواد الخاصة بالطالب في هذا الملف
                    student_data.append({
                        'student_number': student_number if student_number else "غير متوفر",
                        'id_card': csv_cne,
                        'first_name': row.get('name', ''),
                        'last_name': row.get('name_ar', ''),
                        'subject': row.get('subject', ''),
                        'average': points,
                        'notes': determine_notes(points),
                        'level': level  # إضافة المستوى تلقائيًا
                    })

        # إذا تم العثور على الطالب في الملف، نوقف البحث في باقي الملفات
        if student_data:
            break

    print(f"الطلاب الذين تم العثور عليهم: {len(student_data)}")  # طباعة عدد الطلاب الذين تم العثور عليهم
    return student_data if student_data else None

def clean_text(text):
    return text.strip().replace('\u200f', '').replace('\u200e', '').replace('\u061C', '')

@app.route('/Student_space', methods=['POST'])
def student_space():
    if request.is_json:
        data = request.get_json()
        print(f"Received data: {data}")  # طباعة البيانات المستلمة للتحقق

        id_card = data.get('id_card', '').strip()
        code_massar = data.get('major', '').strip()

        if not id_card or not code_massar:
            print("الحقول غير مكتملة")  # طباعة إذا كانت الحقول فارغة
            return jsonify({
                "success": False,
                "error": "❌ يجب أن تكون الحقول id_card و major مملوءة."
            }), 400

        print(f"Searching for student with ID card: {id_card} and Major: {code_massar}")  # طباعة القيم المتلقاة للبحث

        student_records = search_student(id_card, code_massar)

        if student_records:
            print(f"تم العثور على الطلاب: {student_records}")  # طباعة الطلاب الذين تم العثور عليهم
            return jsonify({
                "success": True,
                "students": student_records
            })
        else:
            print("لم يتم العثور على أي طالب.")  # طباعة عندما لا يتم العثور على طالب
            return jsonify({
                "success": False,
                "error": "❌ المعلومات غير صحيحة."
            }), 400
    else:
        print("نوع البيانات غير مدعوم.")  # طباعة إذا كانت البيانات المرسلة ليست JSON
        return jsonify({
            "success": False,
            "error": "❌ نوع البيانات غير مدعوم. يجب إرسال البيانات بتنسيق JSON."
        }), 415


@app.route('/show_names')
def show_names():
    return render_template('show_names.html', language=get_locale(), names=[])

# صفحة خطأ
@app.route('/error')
def error():
    return render_template('error.html', language=get_locale())




# إعداد قاعدة البيانات
def init_db():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS teacher_folders (
                email TEXT PRIMARY KEY,
                folder_path TEXT NOT NULL,
                FOREIGN KEY(email) REFERENCES users(email)
            )
        ''')
        conn.commit()

# دالة لتشفير كلمة المرور
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# إضافة مستخدم إلى قاعدة البيانات
def add_user(email, password):
    hashed_password = hash_password(password)  # تشفير كلمة المرور
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed_password))
            conn.commit()
            print(f"تمت إضافة المستخدم: {email}")
        except sqlite3.IntegrityError:
            print(f"المستخدم {email} موجود بالفعل.")


# إضافة أو تحديث مسار مجلد أستاذ
def add_teacher_folder(email, folder_path):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO teacher_folders (email, folder_path) VALUES (?, ?)', (email, folder_path))
        conn.commit()
        print(f"تم إضافة مسار المجلد للأستاذ: {email} -> {folder_path}")

# استرجاع مسار مجلد أستاذ
def add_teacher_folder(email):
    teacher_email_modified = email.replace("@", "_").replace(".", "_")
    folder_path = os.path.abspath(os.path.join("static", "pdfs", teacher_email_modified))

    # ✅ التحقق مما إذا كان المجلد غير موجود وإنشاؤه
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"✅ تم إنشاء المجaلد للأستاذ: {folder_path}")
    else:
        print(f"📂 المجلد موجود بالفعل: {folder_path}")

    # ✅ إضافة المسار إلى قاعدة البيانات
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO teacher_folders (email, folder_path) VALUES (?, ?)', (email, folder_path))
        conn.commit()
        print(f"✅ تم تخزين مسار المجلد في قاعدة البيانات: {email} -> {folder_path}")






# دالة لاسترجاع مسار مجلد الأستاذ بناءً على البريد الإلكتروني
def get_teacher_folder(email):
    # استبدال الرموز في البريد الإلكتروني
    teacher_email_modified = email.replace("@", "_").replace(".", "_")
    
    # تحديد المسار بناءً على البريد الإلكتروني المعدل
    teacher_folder = os.path.abspath(os.path.join("static", "pdfs", teacher_email_modified))
    
    # تحقق من وجود المجلد
    if os.path.exists(teacher_folder):
        return teacher_folder
    else:
        print(f"❌ 📂 مجلد الأستاذ {email} غير موجود في المسار: {teacher_folder}")
        return None


# تحديث كلمات المرور المخزنة لتكون مشفرة (مرة واحدة)
def update_passwords_to_hashed():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT email, password FROM users')
        users = cursor.fetchall()
        for email, password in users:
            # إذا لم تكن كلمة المرور مشفرة، نقوم بتشفيرها
            if len(password) != 64:  # طول كلمة المرور المشفرة بـ SHA-256 هو 64
                hashed_password = hash_password(password)
                cursor.execute('UPDATE users SET password = ? WHERE email = ?', (hashed_password, email))
        conn.commit()

# جلب المستخدمين من قاعدة البيانات
def get_users():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT email, password FROM users')
        users = dict(cursor.fetchall())
        print(f"المستخدمون في قاعدة البيانات: {users}")  # طباعة للتأكد من البيانات
        return users

if __name__ == '__main__':
    init_db()
    update_passwords_to_hashed()
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
