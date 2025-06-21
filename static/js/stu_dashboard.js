// --------------------------الجزء الخاص برفع الصور و عرض المعلومات الشخصية----------------------------------------

document.addEventListener("DOMContentLoaded", function () {
  const fileInput = document.getElementById("file-input");
  const uploadForm = document.getElementById("upload-form");
  const profileImage = document.getElementById("profile-image");
  const profileImageHeader = document.getElementById("profile-image-header");
  const loading = document.getElementById("loading");
  const modal = document.getElementById("suggestedModal");

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
            return response.json(); // رابط الصورة الجديد
          })
          .then((data) => {
            const newSrc = data.image_url + "?t=" + new Date().getTime(); // ⬅️ إلغاء الكاش
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

  window.selectSuggestedImage = function (src) {
    loading.classList.add("active");

    fetch("/save-suggested-image", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image_url: src }),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to save image.");
        const newSrc = src + "?t=" + new Date().getTime(); // ⬅️ إلغاء الكاش
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
  window.goToPassword = function () {
    window.location.href = "/password";
  };
  window.goToCommunication = function () {
    window.location.href = "/chat";
  };
});

function openFileInput() {
  document.getElementById("file-input").click();
}

function submitForm() {
  document.getElementById("loading").classList.add("active");
  document.getElementById("upload-form").submit();
}

function selectSuggestedImage(src) {
  document.getElementById("loading").classList.add("active");

  // حفظ الصورة المختارة في الجلسة
  fetch("/save-suggested-image", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image_url: src }),
  })
    .then((response) => {
      if (response.ok) {
        // تغيير صورة الملف الشخصي على الصفحة
        document.getElementById("profile-image").src = src;

        // إخفاء النافذة المنبثقة
        document.getElementById("suggestedModal").style.display = "none";

        // إخفاء رسالة "جاري التحميل"
        document.getElementById("loading").classList.remove("active");
      }
    })
    .catch(() => {
      // في حال حدوث خطأ، إخفاء رسالة "جاري التحميل"
      document.getElementById("loading").classList.remove("active");
    });
}

function openModal() {
  document.getElementById("suggestedModal").style.display = "flex";
}

function closeModal() {
  document.getElementById("suggestedModal").style.display = "none";
}
function goToAccount() {
  // توجيه المستخدم إلى صفحة الحساب
  window.location.href = "/account"; // قم بتغيير الرابط إلى صفحة الحساب الخاصة بك
}
function goToPassword() {
  // توجيه المستخدم إلى صفحة الحساب
  window.location.href = "/password"; // قم بتغيير الرابط إلى صفحة الحساب الخاصة بك
}
function goToCommunication() {
  // توجيه المستخدم إلى صفحة الحساب
  window.location.href = "/chat"; // قم بتغيير الرابط إلى صفحة الحساب الخاصة بك
}

function toggleProfileMenu() {
  const menu = document.getElementById("profile-container");
  menu.style.display = menu.style.display === "block" ? "none" : "block";
}

// إغلاق عند النقر خارج القائمة
// تفعيل إخفاء القائمة عند النقر خارجها
window.addEventListener("click", function (e) {
  const menu = document.getElementById("profile-container");
  const icon = document.getElementById("profile-image-header"); // أو يمكنك استخدام العنصر الذي يحتوي على الصورة (أي الأيقونة)

  // إذا كان النقر خارج القائمة والصورة
  if (!menu.contains(e.target) && !icon.contains(e.target)) {
    menu.style.display = "none";
  }
});

// -------------------------- الجزء الخاص بإعدادات و إعلاق النوافذ الخاصة بها----------------------------------------

document.getElementById("menu-btn").addEventListener("click", function () {
  document.getElementById("sidebar").classList.add("active");
});

document.getElementById("close-btn").addEventListener("click", function () {
  document.getElementById("sidebar").classList.remove("active");
});

document.getElementById("settings-btn").addEventListener("click", function () {
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
    document.getElementById("background-settings").classList.remove("active"); // إزالة الفئة النشطة لإغلاق النافذة
  });

document.getElementById("language-btn").addEventListener("click", function () {
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
        if (
          element.tagName === "INPUT" ||
          element.tagName === "TEXTAREA"
        ) {
          element.setAttribute("placeholder", translations[key]);
        } else if (element.tagName === "OPTION") {
          element.textContent = translations[key];
        } else {
          element.textContent = translations[key];
        }
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

document.getElementById("font-size-btn").addEventListener("click", function () {
  document.getElementById("font-size-settings").classList.add("active");
  document.getElementById("settings-menu").classList.remove("active");
});
document
  .getElementById("close-size-popup")
  .addEventListener("click", function () {
    document.getElementById("font-size-settings").classList.remove("active"); // إزالة الفئة النشطة لإغلاق النافذة
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
    document.getElementById("font-style-settings").classList.remove("active"); // إزالة الفئة النشطة لإغلاق النافذة
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

AOS.init({
  duration: 1000,
  easing: "ease-in-out",
  once: true,
});
