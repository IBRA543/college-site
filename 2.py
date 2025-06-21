def get_student_data_account(student_number):
    import csv
    import math
    from collections import defaultdict

    files = [
        STUDENTS01_FILE,
        STUDENTS02_FILE,
        STUDENTS03_FILE,
        STUDENTS04_FILE,
        STUDENTS05_FILE,
        STUDENTS06_FILE,
    ]

    # دالة افتراضية تُعيد نتيجة فارغة (تحتاج لتعريفها خارج الدالة حسب مشروعك)
    def default_result():
        return {}

    # دوال مساعدة لحساب اللون (تحتاج لتعريفها في مكان آخر ضمن مشروعك)
    def get_gradient_color(value):
        # مثال: ارجع لون بناءً على القيمة (0-100)
        return f"hsl({(100 - value) * 1.2}, 70%, 50%)"

    def get_gradient_color_max(value):
        # مثال: لون تدرج مخصص للقيم العليا
        return f"hsl({value * 1.2}, 80%, 60%)"

    # تخزين بيانات الطالب
    student_data = {
        'all_scores': [],
        'scores_by_file': {},
        'max': {'point': -1, 'file': None},
        'min': {'point': 21, 'file': None}
    }

    file_data = {}

    averages_by_file = {}

    # قراءة البيانات من الملفات
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

            if len(scores) == 7:
                averages_by_file[file_path] = sum(scores) / 7

        except Exception as e:
            print(f"❌ خطأ في قراءة {file_path}:", e)

    if not student_data['all_scores']:
        return default_result()

    # دالة لحساب النسبة والoffset للدائرة بناءً على القيمة
    def circle_offset(percent):
        circumference = 2 * math.pi * 36
        return circumference - (circumference * percent / 100)

    # حساب النسب المئوية للmax و min
    def calculate_metrics(score_type):
        file_path = student_data[score_type]['file']
        student_score = student_data[score_type]['point']
        points = list(file_data[file_path]['max_points' if score_type == 'max' else 'min_points'].values())

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

        return percentile, circle_offset(percentile)

    # حساب المتوسط الأفضل (max أو min) بناءً على ملفات الطالب
    def calculate_average(is_max=True):
        best_value = -1 if is_max else 21
        best_file = None

        for file_path, scores in student_data['scores_by_file'].items():
            if len(scores) == 7:
                avg = sum(scores) / 7
                if (is_max and avg > best_value) or (not is_max and avg < best_value):
                    best_value = avg
                    best_file = file_path

        if not best_file:
            return 0, 0, circle_offset(0), None, []

        all_averages = [
            file_data[best_file]['total_points'][sn] / 7
            for sn in file_data[best_file]['total_points']
            if file_data[best_file]['count_points'][sn] == 7
        ]
        ref_avg = max(all_averages) if is_max else min(all_averages)
        percentage = (best_value / ref_avg) * 100 if ref_avg != 0 else 100
        percentage = max(0, min(100, percentage))
        return best_value, percentage, circle_offset(percentage), best_file, all_averages

    # حساب البيانات الرئيسية
    percentile_max, offset_max = calculate_metrics('max')
    percentile_min, offset_min = calculate_metrics('min')

    avg, percentage_avg, offset_avg, avg_file, all_avg_list = calculate_average(True)
    min_avg, percentage_min_avg, offset_min_avg, min_avg_file, all_min_list = calculate_average(False)

    # حساب معدل النجاح (متوسط متوسطات الملفات)
    if len(averages_by_file) == 2:
        success_average = sum(averages_by_file.values()) / 2
    elif len(averages_by_file) == 1:
        success_average = list(averages_by_file.values())[0]
    else:
        success_average = 0

    success_percentage = (success_average / 20) * 100 if success_average > 0 else 0
    success_offset = circle_offset(success_percentage)

    # حساب بيانات كل فصل دراسي (7 نقاط لكل ملف)
    def semester_stats(file_key):
        scores = student_data['scores_by_file'].get(file_key, [])
        if not scores:
            return 0, 0

        avg_score = sum(scores) / len(scores)

        total = sum(scores)
        under_5_count = sum(1 for p in scores if p < 5)

        if total > 70:
            if under_5_count == 0:
                fulfillment = 100
            else:
                fulfillment = max(0, 100 - (under_5_count * 14))
        else:
            fulfillment = (total / 140) * 100

        return round(avg_score, 2), round(fulfillment, 2)

    semesters = [
        STUDENTS01_FILE,
        STUDENTS02_FILE,
        STUDENTS03_FILE,
        STUDENTS04_FILE,
        STUDENTS05_FILE,
        STUDENTS06_FILE,
    ]

    semester_scores = {}
    semester_fulfillments = {}

    for i, sem_file in enumerate(semesters, 1):
        avg_sem, fulfill_sem = semester_stats(sem_file)
        semester_scores[f'semester_{i}'] = avg_sem
        semester_fulfillments[f'{i}'] = fulfill_sem

    # تحديد إن تم استيفاء الفصل الأول (مثال)
    semester_fulfilled = semester_fulfillments['1'] == 100

    # حساب إزاحة الاستيفاء للفصل الأول
    fulfillment_offset = circle_offset(semester_fulfillments['1'])

    return {
        'min_point': round(student_data['min']['point'], 1),
        'max_point': round(student_data['max']['point'], 1),

        'average': round(avg, 1),
        'percentage_avg': round(percentage_avg, 1),
        'circle_offset_avg': round(offset_avg, 1),
        'color_avg': get_gradient_color_max(percentage_avg),

        'higher_than_max': sorted(
            [p for p in file_data[student_data['max']['file']]['max_points'].values() if p > student_data['max']['point']],
            reverse=True
        )[:5],

        'percentage_max': round(percentile_max, 1),
        'circle_offset_max': round(offset_max, 1),

        'percentage_min': round(percentile_min, 1),
        'circle_offset_min': round(offset_min, 1),
        'color_min': get_gradient_color(percentile_min),

        'all_scores': student_data['all_scores'],

        'semester_scores': {
        key: {
            'avg': val,
            'percent': 0 if val == 0 else (100 if val >= 10 else 60)  # 0 تعني لا توجد بيانات
        } for key, val in semester_scores.items()
    },


        'min_average': round(min_avg, 1),
        'percentage_min_avg': round(percentage_min_avg, 1),
        'circle_offset_min_avg': round(offset_min_avg, 1),
        'color_min_avg': get_gradient_color(percentage_min_avg),
        'lower_than_min_avg': sorted([a for a in all_min_list if a < min_avg])[:5],

        'success_average': round(success_average, 1),
        'success_percentage': round(success_percentage, 1),
        'success_offset': round(success_offset, 1),
        'success_color': get_gradient_color_max(success_percentage),

        'semester_fulfilled': semester_fulfilled,
        'fulfillment_percentage': round(semester_fulfillments['1'], 1),
        'fulfillment_offset': round(fulfillment_offset, 1),
        'fulfillment_color': get_gradient_color_max(semester_fulfillments['1']),

        # إضافة نسب الاستيفاء لكل فصل دراسي بشكل منفصل
        'fulfillment_percentages_by_semester': semester_fulfillments,
    }








# -----------------------------------saved_students_table فضاء الطالب -----------------------------------

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





def read_messages():
    print("بدأت قراءة الرسائل...")
    messages = []
    try:
        with open(MESSAGES_FILE, encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                print("سطر مقروء من ملف الرسائل:", row)
                if len(row) == 3:
                    messages.append({'student_name': row[0], 'text': row[1], 'time': row[2]})
                else:
                    print("❌ سطر غير صالح (ليس 3 عناصر):", row)
    except FileNotFoundError:
        print("❌ ملف الرسائل غير موجود:", MESSAGES_FILE)
    return messages



@app.route('/chat1')
def chat1():
    print("🚀 دخل إلى مسار /chat1")
    students = []
    filepath = STUDENTS_FILE
    current_student_session = session.get('current_student')
    print("🧠 جلسة الطالب:", current_student_session)
    current_student = None

    with open(filepath, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            print("🔍 سطر طالب:", row)
            if row['role'].lower() == 'student' and row['class'] == 'S1':
                profile_img = row['profile_image'].strip()
                print("🖼️ صورة الملف الشخصي الأصلية:", profile_img)
                if not profile_img:
                    profile_img = '/static/images/default-avatar.png'
                else:
                    if not profile_img.startswith('http'):
                        if not profile_img.startswith('/static'):
                            profile_img = '/static/' + profile_img.lstrip('/')

                student_data = {
                    'name': row['name'],
                    'second_name': row['second_name'],
                    'class': row['class'],
                    'contact': row['contact'],
                    'address': row['address'],
                    'profile_image': profile_img
                }
                print("✅ طالب مضاف:", student_data)
                students.append(student_data)

                if (current_student_session and
                    row['name'] == current_student_session.get('name') and
                    row['second_name'] == current_student_session.get('second_name')):
                    current_student = student_data
                    print("🎯 الطالب الحالي تم التعرف عليه:", current_student)

    if not current_student and current_student_session:
        print("⚠️ لم يتم العثور على الطالب، استخدام بيانات الجلسة الاحتياطية")
        current_student = {
            'name': current_student_session.get('name'),
            'second_name': current_student_session.get('second_name'),
            'profile_image': '/static/images/user.png'
        }

    current_student_name = None
    if current_student:
        current_student_name = f"{current_student['name']} {current_student['second_name']}"
        print("📛 اسم الطالب الكامل:", current_student_name)

    messages = read_messages()
    print("📨 عدد الرسائل:", len(messages))
    return render_template('chat1.html',
                           students=students,
                           current_student=current_student,
                           current_student_name=current_student_name,
                           messages=messages)


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    print("📥 بيانات مستلمة من POST:", data)

    student_name = data.get('student_name')
    message_text = data.get('message')

    if not student_name or not message_text:
        print("❌ بيانات ناقصة:", student_name, message_text)
        return jsonify({'status': 'error', 'message': 'Missing data'}), 400

    from datetime import datetime
    time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(f"✍️ حفظ الرسالة: [{student_name}] - {message_text} في {time_str}")

    with open(MESSAGES_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([student_name, message_text, time_str])

    print("✅ تم حفظ الرسالة بنجاح.")
    return jsonify({'status': 'success'})

MESSAGES_FILE = r"C:\Users\DATA\OneDrive\Desktop\Python\Calcolator\site_college30\data\message.csv"






























































































































































































































































































































































































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
    print("Start upload_image()")
    email = session.get('email')
    print(f"Session email: {email}")
    if not email:
        print("Unauthorized: no email in session")
        return 'Unauthorized', 401

    if 'image' not in request.files:
        print("No file part in request")
        return 'No file part', 400

    file = request.files['image']
    print(f"Uploaded file: {file.filename}")
    if file.filename == '':
        print("No selected file")
        return 'No selected file', 400

    if file and allowed_file(file.filename):
        print("File allowed")
        ext = file.filename.rsplit('.', 1)[1].lower()
        safe_email = email.replace('@', '_').replace('.', '_')
        filename = f"{safe_email}.{ext}"
        full_path = os.path.join(app.config['UPLOAD_IMAGES_FOLDER'], filename)
        print(f"Saving file to: {full_path}")

        try:
            file.save(full_path)
            print("File saved successfully")
        except Exception as e:
            print(f"Error saving file: {e}")
            return f"Error saving file: {e}", 500

        timestamp = int(time.time())
        image_url = f'/static/uploads/{filename}?t={timestamp}'
        session['profile_image'] = image_url
        print(f"Session profile_image set to: {image_url}")

        try:
            update_student_image(email, f'/static/uploads/{filename}')
            print("Updated student image in CSV successfully")
        except Exception as e:
            print(f"Error updating student image in CSV: {e}")
            return f"Error updating student image: {e}", 500

        print("Returning success response")
        return jsonify({"image_url": image_url}), 200

    print("File not allowed")
    return 'File not allowed', 400


@app.route('/save-suggested-image', methods=['POST'])
def save_suggested_image():
    print("Start save_suggested_image()")
    email = session.get('email')
    print(f"Session email: {email}")
    if not email:
        print("Unauthorized: no email in session")
        return 'Unauthorized', 401

    data = request.get_json()
    image_url = data.get('image_url')
    print(f"Received image_url: {image_url}")

    session['profile_image'] = image_url
    print("Session profile_image updated")

    try:
        update_student_image(email, image_url)
        print("Updated student image in CSV successfully")
    except Exception as e:
        print(f"Error updating student image in CSV: {e}")
        return f"Error updating student image: {e}", 500

    return jsonify({"message": "Image saved successfully"}), 200


@app.route('/account')
def account():
    email = session.get('email', None)
    print(f"Account page requested by: {email}")
    student = get_student_by_email(email)
    profile_image = student['profile_image'] if student and student.get('profile_image') else '/static/images/user.png'
    print(f"Using profile_image: {profile_image}")
    return render_template('account.html', profile_image=profile_image)




@app.route('/get-profile-image')
def get_profile_image():
    email = session.get('email', None)
    student = get_student_by_email(email)
    profile_image = student['profile_image'] if student and student.get('profile_image') else '/static/images/user.png'
    return jsonify({'profile_image': profile_image})








DATA_DIR = "student_chats"
os.makedirs(DATA_DIR, exist_ok=True)


@app.route("/students1")
def get_students1():
    students = []
    file_path = r"C:\Users\DATA\OneDrive\Desktop\Python\Calcolator\site_college21\data\students.csv"
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get("role") != "student":
                continue  # تجاهل الأساتذة أو أي دور آخر

            avatar = row.get("profile_image") or "/static/images/user.png"
            students.append({
                "name": row.get("name"),
                "email": row.get("email", "student@example.com"),
                "department": row.get("course"),
                "avatar": avatar,
                "major": row.get("class"),
                "status": "نشط",  # أو يمكن أخذها من ملف إن وُجد عمود مخصص
                "dateOfEnrollment": row.get("year"),
                "location": row.get("address"),
            })
    return jsonify(students)




def get_student_file_path(student_id):
    return os.path.join(DATA_DIR, f"student_{student_id}.json")

@app.route('/student_chat_data/<student_id>', methods=['GET'])
def get_student_chat_data(student_id):
    path = get_student_file_path(student_id)
    if not os.path.exists(path):
        # لو الملف مش موجود نرجع بيانات فارغة
        return jsonify({"messages": [], "friends": []})
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/student_chat_data/<student_id>', methods=['POST'])
def save_student_chat_data(student_id):
    data = request.get_json()
    path = get_student_file_path(student_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return jsonify({"status": "success"})

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
    init_db()  # إنشاء قاعدة البيانات إذا لم تكن موجودة
    update_passwords_to_hashed()  # تحديث كلمات المرور غير المشفرة
    app.run(debug=True)

