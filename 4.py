
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 ميجابايت
@app.errorhandler(413)
def request_entity_too_large(error):
    flash('❌ حجم الملف كبير جداً! الرجاء رفع ملفات بحجم أقل من 16 ميغابايت.')
    return redirect(url_for('references'))  # بدون تحديد الكود هنا (يصبح 302 تلقائيًا)


from flask import make_response, render_template

@app.route('/references')
def references():
    response = make_response(render_template('references.html'))
    # تمنع المتصفح من إعادة استخدام نسخة قديمة وتطلب إعادة تحميل صحيحة
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

import re


def clean_filename(filename):
    # إزالة المسارات المحتملة
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # استبدال الفراغات بـ _
    filename = filename.replace(' ', '_')
    
    # إزالة أو استبدال الأحرف الغير مرغوبة (تبقي الأحرف العربية والإنجليزية والأرقام والـ _ و - فقط)
    # التعبير النظامي يسمح بالحروف العربية: \u0600-\u06FF
    filename = re.sub(r'[^\w\u0600-\u06FF\-\.]', '', filename)
    
    # منع أكثر من نقطة متتالية أو في بداية/نهاية الاسم
    filename = re.sub(r'\.+', '.', filename).strip('.')
    
    return filename


def unique_filename(directory, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1
    return new_filename


import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'mp4', 'avi', 'mov', 'wmv', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file1():
    if 'file' not in request.files:
        flash('❌ لم يتم اختيار أي ملف.')
        return redirect(url_for('references'))

    file = request.files['file']
    if file.filename == '':
        flash('❌ اسم الملف فارغ.')
        return redirect(url_for('references'))

    publish_type = request.form.get('publish_type')
    username = session.get('professor')

    if file and publish_type and username:
        if not allowed_file(file.filename):
            flash('❌ نوع الملف غير مدعوم. الرجاء رفع ملفات بصيغة PDF أو Word أو PowerPoint أو فيديو.')
            return redirect(url_for('references'))

        base_path = os.path.join(
            BASE_DIR, 'static', 'pdfs', username.replace("@", "_").replace(".", "_")
        )
        if publish_type == 'مراجع':
            base_path = os.path.join(base_path, 'references')
        elif publish_type == 'خرائط':
            base_path = os.path.join(base_path, 'maps')
        elif publish_type == 'نماذج الامتحانات':
            base_path = os.path.join(base_path, 'exam')
        elif publish_type == 'آخر':
            base_path = os.path.join(base_path, 'last')

        os.makedirs(base_path, exist_ok=True)

        filename = clean_filename(file.filename)
        filename = unique_filename(base_path, filename)
        save_path = os.path.join(base_path, filename)
        file.save(save_path)

        flash('✅ تم رفع الملف بنجاح.')
        return redirect(url_for('references'))

    flash('❌ حدث خطأ أثناء رفع الملف.')
    return redirect(url_for('references'))






















  <body>
    <div
      class="upload-container"
      role="main"
      aria-label="نموذج رفع ملفات المراجع والنماذج"
    >
      {% with messages = get_flashed_messages(with_categories=false) %} {% if
      messages %}
      <div
        style="
          background-color: #dff0d8;
          color: #3c763d;
          padding: 15px;
          margin-bottom: 20px;
          border-radius: 10px;
        "
      >
        {% for message in messages %}
        <div>{{ message|safe }}</div>
        {% endfor %}
      </div>
      {% endif %} {% endwith %}

      <h2><i class="fas fa-upload"></i> رفع ونشر المراجع والملفات</h2>
      <form
        id="upload-form"
        action="/upload"
        method="POST"
        enctype="multipart/form-data"
        aria-describedby="desc-upload"
      >
        <div id="desc-upload" class="sr-only">
          يمكنك رفع ملفات المراجع، نماذج الامتحانات، الخرائط، أو الصور. صيغة
          الملفات المقبولة: PDF، Word، صور JPG، PNG، إلخ.
        </div>

        <div class="select-wrapper">
          <select
            id="publish-type"
            name="publish_type"
            required
            aria-label="اختر نوع النشر"
          >
            <option value="" disabled selected>-- اختر نوع النشر --</option>
            <option value="مراجع">نشر مراجع</option>
            <option value="خرائط">نشر خرائط</option>
            <option value="نماذج الامتحانات">نشر نماذج الامتحانات</option>
            <option value="آخر">نشر آخر</option>
          </select>
        </div>

        <div class="file-input-wrapper">
          <input
            type="file"
            id="file-upload"
            name="file"
            accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
            required
            hidden
          />
          <label for="file-upload" class="custom-file-label">
            <i class="fas fa-file-upload"></i> اختر ملف للرفع
          </label>
          <div id="file-name" aria-live="polite"></div>
        </div>

        <div class="loading-bar" id="loading-bar" aria-hidden="true"></div>

        <button type="submit" class="submit-btn" aria-live="polite">
          <i class="fas fa-paper-plane"></i> رفع الملف
        </button>
      </form>

      <a
        href="{{ url_for('student') }}"
        class="btn-back"
        aria-label="العودة إلى إدخال النقط"
      >
        <i class="fas fa-arrow-left"></i> العودة
      </a>
    </div>

    <script>
      const fileInput = document.getElementById("file-upload");
      const fileNameDisplay = document.getElementById("file-name");
      const loadingBar = document.getElementById("loading-bar");
      const form = document.getElementById("upload-form");
      const submitBtn = form.querySelector("button.submit-btn");

      fileInput.addEventListener("change", () => {
        const fileName =
          fileInput.files.length > 0 ? fileInput.files[0].name : "";
        fileNameDisplay.textContent = fileName
          ? `📁 تم اختيار الملف: ${fileName}`
          : "";
      });

      form.addEventListener("submit", (e) => {
        if (!fileInput.files.length) return;
        loadingBar.style.display = "block";
        submitBtn.disabled = true;
        submitBtn.innerHTML =
          '<i class="fas fa-spinner fa-spin"></i> جاري الرفع...';
      });
    </script>
  </body>
</html>
