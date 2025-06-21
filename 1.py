from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import csv
import os
from flask import session  # تأكد أن لديك هذا السطر

app = Flask(__name__)
app.secret_key = 'super-secret-key-12345'  # يمكنك تغييره لأي قيمة سرية

def load_students():
    data_folder = r'C:\Users\DATA\OneDrive\Desktop\Python\Calcolator\site_college30\data'
    files = [os.path.join(data_folder, f'students0{i}.csv') for i in range(1, 7)]

    students = []
    for file in files:
        print(f"Checking file: {file}")
        if os.path.exists(file):
            print(f"Reading file: {file}")
            with open(file, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    print(f"Loaded student: {row}")
                    students.append(row)
        else:
            print(f"File not found: {file}")
    return students

@app.route('/')
def index():
    print("Rendering Quick_entry_points.html")
    return render_template('Quick_entry_points.html')

@app.route('/search', methods=['POST'])
def search_student():
    card_number = request.form['cardNumber'].strip()
    code_massar = request.form['misterCode'].strip()

    print(f"Searching for student: ID Card={card_number}, Code Massar={code_massar}")

    student_subjects = []

    data_folder = r'C:\Users\DATA\OneDrive\Desktop\Python\Calcolator\site_college30\data'
    files = [os.path.join(data_folder, f'students0{i}.csv') for i in range(1, 7)]

    for file in files:
        print(f"Checking file: {file}")
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['id_card'].strip() == card_number and row['code_massar'].strip() == code_massar:
                        print(f"Match found in {file}: {row}")
                        student_subjects.append({
                            'subject': row['subject'],
                            'points': row['points'],
                            'student_number': row['student_number'],
                            'name': row['name']
                        })
        else:
            print(f"File not found: {file}")

    if student_subjects:
        session['card_number'] = card_number
        session['mister_code'] = code_massar
        print(f"Student subjects found: {student_subjects}")
        return jsonify({"found": True, "name": student_subjects[0]['name'], "subjects": student_subjects})
    else:
        print("Student not found!")
        return jsonify({"found": False, "message": "الطالب غير موجود!"})

@app.route('/saved_students_table')
def saved_students_table():
    card_number = session.get('card_number')
    mister_code = session.get('mister_code')

    if not card_number or not mister_code:
        print("No session data found, redirecting to index.")
        return redirect(url_for('index'))

    data_folder = r'C:\Users\DATA\OneDrive\Desktop\Python\Calcolator\site_college30\data'
    files = [os.path.join(data_folder, f'students0{i}.csv') for i in range(1, 7)]


    def read_csv(file_path):
        print(f"Reading file: {file_path}")
        students = []
        if os.path.exists(file_path):
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get('id_card', '').strip() == card_number and row.get('code_massar', '').strip() == mister_code:
                        print(f"Matched student in file {file_path}: {row}")
                        students.append(row)
        else:
            print(f"File not found: {file_path}")
        return students

    all_students = [read_csv(file) for file in files]

    subject_lists = [
        ["قراءة و تحليل الخرائط الطبوغرافية", "مدخل إلى علم الإجتماع", "جغرافية السكان والديموغرافيا", "جيومورفولوجيا عامة", "مدخل لدراسة تاريخ المغرب الوسيط", "المهارات الحياتية والذاتية", "اللغة الفرنسية", "اللغة الإنجليزية"],
        ["المناخ", "الإتجاهات الكلاسيكية الحديثة في علم الإجتماع", "جغرافية المغرب العامة", "جغرافية الأرياف", "مدخل لدراسة تاريخ المغرب المعاصر والراهن", "المهارات الحياتية والرقمية", "اللغة الفرنسية", "اللغة الإنجليزية"],
        ["مناخ دينامي", "المهارات الفنية والثقافية", "جيومورفلوجيا البنيوية", "قراءة وتحليل الخرائط الجيولوجية والجيومرفوفوجية", "جغرافية المدن", "دينامية المجال الريفي", "اللغة الفرنسية", "اللغة الإنجليزية"],
        ["الخرائط والسيميولوجيا", "النظم البيئية والتربة والنبات", "جغرافية البحر المتوسط وإفريقيا جنوب الصحراء", "جغرافية الطاقة", "دينامية المجال الحضري", "المهارات الهياتية والذاتية", "اللغة الفرنسية", "اللغة الإنجليزية"],
        ["التاريخ الجيولوجي", "الفضاء", "الكون", "الأرض", "الصخور", "الأنهار"],
        ["التاريخ الجيولوجي", "الفضاء", "الكون", "الأرض", "الصخور", "الأنهار"]
    ]
    semester_names = ["الفصل الأول", "الفصل الثاني", "الفصل الثالث", "الفصل الرابع", "الفصل الخامس", "الفصل السادس"]

    def build_subjects_data(rows, subject_list, semester_name):
        data = []
        for subject in subject_list:
            match = next((r for r in rows if r.get('subject') == subject), None)
            print(f"Processing subject '{subject}' in {semester_name}")
            if match:
                points = match.get('points', '').strip()
                student_number = match.get('student_number', '').strip()
                try:
                    point_val = float(points)
                    note = "مستف" if point_val >= 10 else "مستدرك"
                    note_color = "green" if point_val >= 10 else "red"
                except:
                    note = ""
                    note_color = ""
            else:
                points = "-"
                student_number = "-"
                note = "-"
                note_color = "black"

            print(f"Subject: {subject}, Points: {points}, Note: {note}")
            data.append({
                'subject': subject,
                'points': points,
                'note': note,
                'note_color': note_color,
                'semester': semester_name,
                'student_number': student_number
            })
        return data

    all_data = [build_subjects_data(rows, subjects, semester)
                for rows, subjects, semester in zip(all_students, subject_lists, semester_names)]

    return render_template('saved_students_table.html',
                           main_data=all_data[0] if any(d['points'] != '-' for d in all_data[0]) else None,
                           extra_data=all_data[1] if any(d['points'] != '-' for d in all_data[1]) else None,
                           third_data=all_data[2] if any(d['points'] != '-' for d in all_data[2]) else None,
                           fourth_data=all_data[3] if any(d['points'] != '-' for d in all_data[3]) else None,
                           fifth_data=all_data[4] if any(d['points'] != '-' for d in all_data[4]) else None,
                           sixth_data=all_data[5] if any(d['points'] != '-' for d in all_data[5]) else None)

@app.route("/stats")
def stats():
    card_number = session.get('card_number')
    mister_code = session.get('mister_code')

    if not card_number or not mister_code:
        print("No session data found for stats, redirecting to index.")
        return redirect(url_for('index'))

    print(f"Generating stats for card_number={card_number} and mister_code={mister_code}")

    data_folder = r'C:\Users\DATA\OneDrive\Desktop\Python\Calcolator\site_college30\data'
    file_paths = [os.path.join(data_folder, f'students0{i}.csv') for i in range(1, 7)]

    subjects_by_file = [
        (["قراءة و تحليل الخرائط الطبوغرافية", "مدخل إلى علم الإجتماع", "جغرافية السكان والديموغرافيا",
          "جيومورفولوجيا عامة", "مدخل لدراسة تاريخ المغرب الوسيط", "المهارات الحياتية والذاتية",
          "اللغة الفرنسية", "اللغة الإنجليزية"], "الفصل الأول"),
        (["المناخ", "الإتجاهات الكلاسيكية الحديثة في علم الإجتماع", "جغرافية المغرب العامة",
          "جغرافية الأرياف", "مدخل لدراسة تاريخ المغرب المعاصر والراهن", "المهارات الحياتية والرقمية",
          "اللغة الفرنسية", "اللغة الإنجليزية"], "الفصل الثاني"),
        (["مناخ دينامي", "المهارات الفنية والثقافية", "جيومورفلوجيا البنيوية",
          "قراءة وتحليل الخرائط الجيولوجية والجيومرفوفوجية", "جغرافية المدن", "دينامية المجال الريفي",
          "اللغة الفرنسية", "اللغة الإنجليزية"], "الفصل الثالث"),
        (["الخرائط والسيميولوجيا", "النظم البيئية والتربة والنبات", "جغرافية البحر المتوسط وإفريقيا جنوب الصحراء",
          "جغرافية الطاقة", "دينامية المجال الحضري", "المهارات الهياتية والذاتية",
          "اللغة الفرنسية", "اللغة الإنجليزية"], "الفصل الرابع"),
        (["التاريخ الجيولوجي", "الفضاء", "الكون", "الأرض", "الصخور", "الأنهار"], "الفصل الخامس"),
        (["التاريخ الجيولوجي", "الفضاء", "الكون", "الأرض", "الصخور", "الأنهار"], "الفصل السادس"),
    ]

    matched_file = None
    for file in file_paths:
        print(f"Searching student in file: {file}")
        if os.path.exists(file):
            with open(file, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('id_card', '').strip() == card_number and row.get('code_massar', '').strip() == mister_code:
                        matched_file = file
                        print(f"Student found in file: {file}")
                        break
        if matched_file:
            break

    if not matched_file:
        print("Student data not found in any file for stats.")
        return "بيانات الطالب غير موجودة في الملفات."


    idx = file_paths.index(matched_file)
    subject_list, semester = subjects_by_file[idx]

    print(f"Processing stats for semester: {semester}")

    # قراءة كل النقاط من الملف لحساب max و min
    with open(matched_file, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        points = [float(row['points']) for row in reader if row.get('points', '').replace('.', '', 1).isdigit()]
    max_point = max(points) if points else 0
    min_point = min(points) if points else 0
    print(f"Max point: {max_point}, Min point: {min_point}")

    # استخراج نقاط الطالب نفسه
    student_points = []
    data = []
    with open(matched_file, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('id_card', '').strip() == card_number and row.get('code_massar', '').strip() == mister_code:
                point_str = row.get('points', '').strip()
                subject = row.get('subject', '').strip()
                if point_str.replace('.', '', 1).isdigit():
                    point = float(point_str)
                    student_points.append(point)
                    data.append({"subject": subject, "points": point})

    student_max = max(student_points) if student_points else 0
    student_min = min(student_points) if student_points else 0
    print(f"Student max point: {student_max}, Student min point: {student_min}")

        # إحصائيات الطالب
    total_subjects = len(data)
    scores = [item["points"] for item in data if isinstance(item["points"], (int, float))]
    average_score = round(sum(scores) / len(scores), 2) if scores else 0
    top_score = max(scores) if scores else 0
    lowest_score = min(scores) if scores else 0


    return render_template('stats.html',
                        max_point=max_point,
                        min_point=min_point,
                        student_max=student_max,
                        student_min=student_min,
                        semester=semester,
                        data=data,
                        total_subjects=total_subjects,
                        average_score=average_score,
                        top_score=top_score,
                        lowest_score=lowest_score)


if __name__ == "__main__":
    app.run(debug=True)
