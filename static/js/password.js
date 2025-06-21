window.onload = () => {
  const flashMessages = document.querySelectorAll(".flash-message");
  flashMessages.forEach((msg) => {
    setTimeout(() => {
      msg.style.transition = "opacity 1s ease";
      msg.style.opacity = 0;
      setTimeout(() => msg.remove(), 1000); // إزالة بعد التلاشي
    }, 5000); // 5 ثوانٍ
  });
};

const form = document.querySelector("form");
const messageBox = document.getElementById("form-message");

form.addEventListener("submit", function (e) {
  const currentPassword = form.current_password.value.trim();
  const newPassword = form.new_password.value.trim();
  const confirmPassword = form.confirm_password.value.trim();

  if (!currentPassword || !newPassword || !confirmPassword) {
    e.preventDefault();
    showMessage("يرجى ملء جميع الحقول.");
  } else if (newPassword !== confirmPassword) {
    e.preventDefault();
    showMessage("كلمة المرور الجديدة وتأكيدها غير متطابقين.");
  }
});
const signupForm = document.querySelector(".signup-form form");

signupForm.addEventListener("submit", function (e) {
  const username = signupForm.username.value.trim();
  const idCard = signupForm.id_card.value.trim();
  const newPassword = signupForm.new_password.value.trim();
  const confirmPassword = signupForm.confirm_password.value.trim();

  const usernameRegex = /^[A-Z]?\d{9}$/;
  const idCardRegex = /^[A-Z]{1,2}\d{4}(\d{2})?$/;

  if (!usernameRegex.test(username)) {
    e.preventDefault();
    showMessage(
      "كود مسار غير صالح. يجب أن يحتوي على حرف كبير اختياري متبوعًا بـ 9 أرقام."
    );
    return;
  }

  if (!idCardRegex.test(idCard)) {
    e.preventDefault();
    showMessage(
      "رقم البطاقة الوطنية غير صالح. يجب أن يبدأ بحرف أو حرفين كبيرين ويتبعه 4 أو 6 أرقام."
    );
    return;
  }

  if (newPassword.length < 8) {
    e.preventDefault();
    showMessage("كلمة المرور الجديدة يجب ألا تقل عن 8 أحرف.");
    return;
  }

  if (newPassword !== confirmPassword) {
    e.preventDefault();
    showMessage("كلمة المرور الجديدة وتأكيدها غير متطابقين.");
    return;
  }
});
const changePasswordForm = document.querySelector(".login-form form");

changePasswordForm.addEventListener("submit", function (e) {
  const currentPassword = changePasswordForm.current_password.value.trim();
  const newPassword = changePasswordForm.new_password.value.trim();
  const confirmPassword = changePasswordForm.confirm_password.value.trim();

  if (!currentPassword || !newPassword || !confirmPassword) {
    e.preventDefault();
    showMessage("يرجى ملء جميع الحقول.");
    return;
  }

  if (newPassword.length < 8) {
    e.preventDefault();
    showMessage("كلمة المرور الجديدة يجب ألا تقل عن 8 أحرف.");
    return;
  }

  if (newPassword !== confirmPassword) {
    e.preventDefault();
    showMessage("كلمة المرور الجديدة وتأكيدها غير متطابقين.");
    return;
  }
});

function showMessage(msg) {
  messageBox.innerText = msg;
  messageBox.style.display = "block";
  messageBox.style.backgroundColor = "#f8d7da"; // أحمر فاتح
  messageBox.style.color = "#721c24"; // أحمر غامق
  messageBox.style.border = "1px solid #f5c6cb";
}
function togglePassword(id) {
  var passwordField = document.getElementById(id);
  var icon = passwordField.nextElementSibling.querySelector("i");

  if (passwordField.type === "password") {
    passwordField.type = "text";
    icon.classList.remove("fa-eye");
    icon.classList.add("fa-eye-slash");
  } else {
    passwordField.type = "password";
    icon.classList.remove("fa-eye-slash");
    icon.classList.add("fa-eye");
  }
}
