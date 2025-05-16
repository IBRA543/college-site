// --------------------------الجزء الخاص برفع الصور و عرض المعلومات الشخصية----------------------------------------

document.addEventListener("DOMContentLoaded", function () {
  const fileInput = document.getElementById("file-input");
  const uploadForm = document.getElementById("upload-form");
  const profileImage = document.getElementById("profile-image");
  const profileImageHeader = document.getElementById("profile-image-header");
  const loading = document.getElementById("loading");
  const modal = document.getElementById("suggestedModal");

  // إخفاء النافذة عند بدء الصفحة
  if (modal) modal.style.display = "none";

  function fadeInImage(imgElement, newSrc) {
    imgElement.style.opacity = 0;
    setTimeout(() => {
      imgElement.src = newSrc;
      imgElement.onload = () => {
        imgElement.style.opacity = 1;
      };
    }, 100);
  }

  if (fileInput) {
    fileInput.addEventListener("change", function () {
      if (fileInput.files.length > 0) {
        loading.classList.add("active");
        const formData = new FormData(uploadForm);

        fetch("/upload", {
          method: "POST",
          body: formData,
        })
          .then((response) => {
            if (!response.ok) throw new Error("Upload failed");
            return response.json();
          })
          .then((data) => {
            const newSrc = data.image_url + "?t=" + new Date().getTime();
            fadeInImage(profileImage, newSrc);
            fadeInImage(profileImageHeader, newSrc);
            loading.classList.remove("active");
          })
          .catch((error) => {
            console.error("Upload Error:", error);
            loading.classList.remove("active");
          });
      }
    });
  }

  // ✅ النسخة الصحيحة لاختيار صورة مقترحة
  window.selectSuggestedImage = function (src) {
    loading.classList.add("active");

    fetch("/save-suggested-image", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image_url: src }),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to save image.");
        const newSrc = src + "?t=" + new Date().getTime();
        fadeInImage(profileImage, newSrc);
        fadeInImage(profileImageHeader, newSrc);
        loading.classList.remove("active");
        if (modal) modal.style.display = "none";
      })
      .catch((err) => {
        console.error("Error:", err);
        loading.classList.remove("active");
      });
  };

  window.openFileInput = function () {
    fileInput.click();
  };

  window.openModal = function () {
    if (modal) modal.style.display = "flex";
  };

  window.closeModal = function () {
    if (modal) modal.style.display = "none";
  };

  window.goToAccount = function () {
    window.location.href = "/account";
  };
});

function toggleProfileMenu() {
  const menu = document.getElementById("profile-container");
  menu.style.display = menu.style.display === "block" ? "none" : "block";
}

window.addEventListener("click", function (e) {
  const menu = document.getElementById("profile-container");
  const icon = document.getElementById("profile-image-header");

  if (!menu.contains(e.target) && !icon.contains(e.target)) {
    menu.style.display = "none";
  }
});

function handleProfileImageClick(event) {
  event.stopPropagation();
  openFileInput();
}

// ------------------------------------ الجزء الخاص بزر عرض الملفات و زر رفع الملفات-------------------------------

document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementById("viewFilesButton")
    .addEventListener("click", function () {
      console.log("✅ تم الضغط على زر عرض الملفات");
      const teacherEmail =
        document.querySelector(".main-section").dataset.email;
      fetchFolders(teacherEmail, true);
    });

  document
    .getElementById("uploadButton")
    .addEventListener("click", function (e) {
      e.preventDefault(); // لمنع الانتقال للرابط #
      document.getElementById("fileUploadModal").style.display = "block";
    });

  // لإغلاق نافذة مشاركة الدرس
  document
    .getElementById("closeModalButton")
    .addEventListener("click", function () {
      document.getElementById("fileUploadModal").style.display = "none";
    });
});

// جلب قائمة المواد المتاحة للأستاذ عند تحميل الصفحة
function fetchFolders(teacherEmail, showModal = true) {
  fetch(`/retrieve_files?teacher_email=${encodeURIComponent(teacherEmail)}`)
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      if (data.success && data.type === "folders_and_files") {
        let subjectList =
          "<div class='d-flex flex-wrap justify-content-center'>";
        data.items.forEach((item) => {
          if (item.type === "folder") {
            subjectList += `
                    <div class="folder-item" onclick="fetchFiles('${teacherEmail}', '${item.name}')">
                      <div class="file-icon folder"><i class="fas fa-folder"></i></div>
                      <div class="file-name">${item.name}</div>
                    </div>
                  `;
          }
        });
        subjectList += "</div>";
        document.getElementById("subjectList").innerHTML = subjectList;

        if (showModal) {
          document.getElementById("subjectModal").style.display = "block";
        }
      } else {
        alert(`❌ ${data.message}`);
      }
    })
    .catch((error) => console.error("❌ فشل في جلب البيانات:", error));
}

// جلب المواد الخاصة بالأستاذ
function fetchFiles(teacherEmail, folderName) {
  // ✅ عند الضغط على مجلد نخفي نافذة المجلدات
  document.getElementById("subjectModal").style.display = "none";

  fetch(
    `/retrieve_files?teacher_email=${encodeURIComponent(
      teacherEmail
    )}&subject=${encodeURIComponent(folderName)}`
  )
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      if (data.success && data.type === "files") {
        let fileList =
          "<h3>📄 الملفات الموجودة داخل المجلد</h3><div class='d-flex flex-wrap justify-content-center'>";
        data.items.forEach((file) => {
          fileList += `
                  <div class="file-item">
                    <button class="options-button" onclick="toggleOptionsMenu(this)">
                      <i class="fas fa-ellipsis-v"></i>
                    </button>
                    <div class="options-menu">
                      <button onclick="deleteFile('${teacherEmail}', '${folderName}', '${file}', this)">🗑️ حذف</button>
                    </div>
                    <div class="file-icon pdf"><i class="fas fa-file-pdf"></i></div>
                    <div class="file-name">${file}</div>
                    <div class="file-actions">
                      <button onclick="viewFile('${teacherEmail}', '${folderName}', '${file}')"><i class="fas fa-eye"></i></button>
                    </div>
                  </div>
                `;
        });
        fileList += "</div>";
        document.getElementById("fileList").innerHTML = fileList;
        document.getElementById("fileModal").style.display = "block";
      } else {
        alert(`❌ ${data.message}`);
      }
    })
    .catch((error) => console.error("❌ فشل في جلب الملفات:", error));
}

function deleteFile(teacherEmail, folderName, fileName, buttonElement) {
  console.log(`إرسال طلب حذف الملف: ${fileName}`);
  if (confirm(`❓ هل أنت متأكد أنك تريد حذف الملف "${fileName}"؟`)) {
    fetch("/delete_files", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        teacher_email: teacherEmail,
        subject: folderName,
        file_name: fileName,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data); // طباعة الرد من السيرفر
        if (data.success) {
          alert(`✅ ${data.message}`);
          const fileItem = buttonElement.closest(".file-item");
          if (fileItem) fileItem.remove();
        } else {
          alert(`❌ ${data.message}`);
        }
      })
      .catch((error) => {
        console.error("❌ فشل في حذف الملف:", error);
        alert("❌ حدث خطأ أثناء حذف الملف.");
      });
  }
}

document
  .getElementById("uploadForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    const fileInput = document.getElementById("fileInput");
    const subjectInput = document.getElementById("subjectInput");
    const filenameInput = document.getElementById("filenameInput");

    if (!fileInput.files.length) {
      alert("❌ يرجى اختيار ملف للرفع.");
      return;
    }

    // وعند التحقق من المادة:
    if (
      !subjectInput.value.trim() ||
      !availableSubjects.includes(subjectInput.value.trim())
    ) {
      alert(
        "❌ يرجى إدخال مادة صحيحة من قائمة المواد المتاحة: " +
          availableSubjects.join(", ")
      );
      return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("subject", subjectInput.value.trim());
    formData.append("filename", filenameInput.value.trim());

    fetch("/upload_file", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          document.getElementById("confirmationMessage").style.display =
            "block";

          // تفريغ الحقول بعد الرفع الناجح
          subjectInput.value = "";
          filenameInput.value = "";
          fileInput.value = "";

          setTimeout(function () {
            document.getElementById("confirmationMessage").style.display =
              "none";
            document.getElementById("fileUploadModal").style.display = "none";
          }, 3000);
        } else {
          alert(`❌ ${data.message}`);
        }
      })
      .catch((error) => {
        console.error("❌ خطأ أثناء رفع الملف:", error);
        alert("❌ حدث خطأ أثناء رفع الملف.");
      });

    // -------------------------- الجزء الخاص بإعدادات و إعلاق النوافذ الخاصة بها----------------------------------------

    document.getElementById("menu-btn").addEventListener("click", function () {
      document.getElementById("sidebar").classList.add("active");
    });

    document.getElementById("close-btn").addEventListener("click", function () {
      document.getElementById("sidebar").classList.remove("active");
    });

    document
      .getElementById("settings-btn")
      .addEventListener("click", function () {
        document.getElementById("sidebar").classList.remove("active");
        document.getElementById("settings-menu").classList.add("active");
      });

    document.getElementById("back-btn").addEventListener("click", function () {
      document.getElementById("settings-menu").classList.remove("active");
      document.getElementById("sidebar").classList.add("active");
    });

    document
      .getElementById("background-btn")
      .addEventListener("click", function () {
        document.getElementById("background-settings").classList.add("active");
        document.getElementById("settings-menu").classList.remove("active");
      });
    document
      .getElementById("close-background-popup")
      .addEventListener("click", function () {
        document
          .getElementById("background-settings")
          .classList.remove("active"); // إزالة الفئة النشطة لإغلاق النافذة
      });

    document
      .getElementById("language-btn")
      .addEventListener("click", function () {
        document.getElementById("language-settings").classList.add("active");
        document.getElementById("settings-menu").classList.remove("active");
      });
    document
      .getElementById("close-language-popup")
      .addEventListener("click", function () {
        document.getElementById("language-settings").classList.remove("active"); // إزالة الفئة النشطة لإغلاق النافذة
      });

    function changeMainBackground(color) {
      document.body.style.backgroundColor = color;
    }

    function changeSecondaryBackground(newColor) {
      let secondaryElements = document.querySelectorAll(".secondary");
      secondaryElements.forEach((element) => {
        let currentColor = window.getComputedStyle(element).backgroundColor;

        // قائمة الألوان التي سيتم استبدالها باللون الجديد
        let colorsToReplace = [
          "rgb(255, 39, 112)", // وردي ()
          "rgb(173, 216, 230)", // أزرق مفتوح (lightblue)
          "rgb(144, 238, 144)",
        ]; // أخضر مفتوح (lightgreen)

        if (colorsToReplace.includes(currentColor)) {
          element.style.backgroundColor = newColor;
        }
      });
    }

    document.addEventListener("DOMContentLoaded", function () {
      let pageGroup = document.body.getAttribute("data-page-group"); // تحديد مجموعة الصفحة
      let savedLang = localStorage.getItem(`language_${pageGroup}`) || "ar"; // استرجاع اللغة المحفوظة أو الافتراضية

      // ضبط اللغة عند تحميل الصفحة
      fetch(`/set_language/${savedLang}`, { method: "POST" }).then(() =>
        loadTranslations(savedLang)
      );

      function loadTranslations(lang) {
        fetch(`/get_translations/${lang}`)
          .then((response) => response.json())
          .then((data) => updateTranslations(data.translations));
      }

      window.changeLanguage = function (lang) {
        localStorage.setItem(`language_${pageGroup}`, lang); // حفظ اللغة الخاصة بالمجموعة فقط

        fetch(`/change_language/${lang}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.success) {
              updateTranslations(data.translations);
            }
          });

        // تحديث الجلسة لضمان حفظ اللغة عند إعادة تشغيل الموقع
        fetch(`/set_language/${lang}`, { method: "POST" });

        // 🔥 إعلام الصفحات الأخرى داخل نفس المجموعة بتحديث الترجمة
        localStorage.setItem(
          "language_update",
          JSON.stringify({ group: pageGroup, lang: lang })
        );
      };

      function updateTranslations(translations) {
        document.querySelectorAll("[data-translate]").forEach((element) => {
          let key = element.getAttribute("data-translate");
          if (translations[key]) {
            element.textContent = translations[key];
          }
        });
      }

      // 🔥 الاستماع لتحديث اللغة من الصفحات الأخرى داخل نفس المجموعة فقط
      window.addEventListener("storage", function (event) {
        if (event.key === "language_update") {
          let data = JSON.parse(event.newValue);
          if (data.group === pageGroup) {
            loadTranslations(data.lang);
          }
        }
      });
    });

    document
      .getElementById("font-size-btn")
      .addEventListener("click", function () {
        document.getElementById("font-size-settings").classList.add("active");
        document.getElementById("settings-menu").classList.remove("active");
      });
    document
      .getElementById("close-size-popup")
      .addEventListener("click", function () {
        document
          .getElementById("font-size-settings")
          .classList.remove("active"); // إزالة الفئة النشطة لإغلاق النافذة
      });

    document
      .getElementById("font-style-btn")
      .addEventListener("click", function () {
        document.getElementById("font-style-settings").classList.add("active");
        document.getElementById("settings-menu").classList.remove("active");
      });
    document
      .getElementById("close-style-popup")
      .addEventListener("click", function () {
        document
          .getElementById("font-style-settings")
          .classList.remove("active"); // إزالة الفئة النشطة لإغلاق النافذة
      });

    // تغيير حجم الخط
    function changeFontSize(size) {
      if (size === "small") {
        document.body.style.fontSize = "12px";
      } else if (size === "medium") {
        document.body.style.fontSize = "16px";
      } else if (size === "large") {
        document.body.style.fontSize = "20px";
      }
    }

    // تغيير تنسيق الخط
    function changeFontStyle(style) {
      document.body.style.fontFamily = style;
    }

    document.getElementById("about-btn").addEventListener("click", function () {
      document.getElementById("about-popup").classList.add("active"); // إضافة الفئة النشطة لعرض النافذة
    });

    document
      .getElementById("close-about-popup")
      .addEventListener("click", function () {
        document.getElementById("about-popup").classList.remove("active"); // إزالة الفئة النشطة لإغلاق النافذة
      });

    document
      .getElementById("report-issue-btn")
      .addEventListener("click", function () {
        document.getElementById("report-popup").style.display = "flex";
      });

    document
      .getElementById("close-about-popup")
      .addEventListener("click", function () {
        document.getElementById("about-popup").style.display = "none";
      });

    document
      .getElementById("close-report-popup")
      .addEventListener("click", function () {
        document.getElementById("report-popup").style.display = "none";
      });

    document
      .getElementById("report-issue-btn")
      .addEventListener("click", function () {
        document.getElementById("report-popup").classList.add("active"); // إضافة الفئة النشطة لعرض النافذة
      });

    document
      .getElementById("close-report-popup")
      .addEventListener("click", function () {
        document.getElementById("report-popup").classList.remove("active"); // إزالة الفئة النشطة لإغلاق النافذة
      });

    document
      .querySelector("#report-popup button")
      .addEventListener("click", function () {
        let issueText = document.querySelector("#report-popup textarea").value;
        if (issueText.trim() !== "") {
          // إرسال البيانات عبر API أو حفظها حسب الحاجة
          console.log("تم الإبلاغ عن مشكلة: " + issueText);
          document.getElementById("report-popup").classList.remove("active");
        } else {
          alert("يرجى كتابة المشكلة قبل الإرسال.");
        }
      });

    // عند الضغط على زر "إرسال" في نافذة الإبلاغ عن مشكلة
    document
      .getElementById("send-issue-btn")
      .addEventListener("click", function () {
        let issueText = document.querySelector("#report-popup textarea").value;
        if (issueText.trim() !== "") {
          // يمكنك إضافة كود لإرسال البيانات عبر API هنا (إن لزم الأمر)
          console.log("تم الإبلاغ عن مشكلة: " + issueText);
          // إغلاق نافذة "الإبلاغ عن مشكلة"
          document.getElementById("report-popup").classList.remove("active");
          // عرض نافذة التواصل
          document.getElementById("contact-popup").classList.add("active");
        } else {
          alert("يرجى كتابة المشكلة قبل الإرسال.");
        }
      });

    // عند الضغط على زر الإغلاق في نافذة التواصل
    document
      .getElementById("close-contact-popup")
      .addEventListener("click", function () {
        document.getElementById("contact-popup").classList.remove("active");
      });

    function viewFile(teacherEmail, folderName, fileName) {
      const fileUrl = `/static/pdfs/${teacherEmail.replace(
        /[@.]/g,
        "_"
      )}/${folderName}/${fileName}`;
      window.open(fileUrl, "_blank");
    }

    function showOptions(fileName) {
      alert(`🚀 خيارات إضافية للملف: ${fileName}`);
    }

    // ✅ دالة إظهار أو إخفاء قائمة الخيارات عند الضغط على زر الثلاث نقاط
    function toggleOptionsMenu(button) {
      // إغلاق جميع القوائم أولاً
      document
        .querySelectorAll(".options-menu")
        .forEach((menu) => (menu.style.display = "none"));
      // ثم إظهار القائمة الخاصة بالعنصر المضغوط
      const menu = button.nextElementSibling;
      menu.style.display = menu.style.display === "flex" ? "none" : "flex";
    }

    // ✅ دالة الحذف (تظهر فقط تنبيه الآن، يمكن ربطها بحذف حقيقي)
    function deleteFile(teacherEmail, folderName, fileName, btn) {
      if (confirm(`هل تريد حذف الملف: ${fileName}؟`)) {
        // هنا يمكنك إرسال طلب حذف حقيقي للخادم
        console.log(`🚮 جاري حذف الملف: ${fileName}`);

        // نحذف البطاقة من الواجهة مباشرة
        const fileCard = btn.closest(".file-item");
        fileCard.remove();
      }
    }
    document
      .getElementById("subjectSelect")
      .addEventListener("change", function () {
        const selected = this.value;
        document.getElementById("subjectInput").value = selected;
      });
  });
