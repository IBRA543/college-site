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
// ---------------------- التحكم في النوافذ (مودال الصور) ----------------------

// فتح النافذة المقترحة للصور
window.openModal = function () {
  if (modal) modal.style.display = "flex";
};

// إغلاق النافذة المقترحة للصور
window.closeModal = function () {
  if (modal) modal.style.display = "none";
};

// ---------------------- التنقل ----------------------

// الانتقال إلى صفحة الحساب الشخصي
window.goToPassword = function () {
  window.location.href = "/account";
};

window.goToAccount = function () {
  window.location.href = "/password";
};
// ---------------------- إدارة الملفات الخاصة بالأستاذ ----------------------
