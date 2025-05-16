const addBtn = document.getElementById("addAnnouncementBtn");
const modal = document.getElementById("announcementModal");
const cancelBtn = document.getElementById("cancelBtn");
const form = document.getElementById("announcementForm");
const container = document.getElementById("announcementsContainer");
const toast = document.getElementById("toast");
const darkToggle = document.getElementById("toggleDarkMode");

let editIndex = null;

// إظهار رسالة Toast
function showToast(msg) {
  toast.textContent = msg;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 2500);
}

// عرض الإعلانات
function render() {
  const data = JSON.parse(localStorage.getItem("announcements") || "[]");
  container.innerHTML = "";
  data.forEach((item, i) => {
    const li = document.createElement("li");
    li.className = "announcement";
    li.innerHTML = `
      <h3>${item.title}</h3>
      <p>${item.content}</p>
      <div class="details">
        <span class="start-time">تاريخ ووقت الإعلان: ${new Date(
          item.startTime
        ).toLocaleString()}</span>
        <span class="priority ${item.priority}">الأولوية: ${
      item.priority === "high"
        ? "عالية"
        : item.priority === "medium"
        ? "متوسطة"
        : "منخفضة"
    }</span>
      </div>
      <div class="actions">
        <button class="edit" onclick="edit(${i})">✏️</button>
        <button class="delete" onclick="remove(${i})">🗑️</button>
      </div>
    `;
    container.appendChild(li);
  });
}

// إضافة أو تعديل إعلان
function saveAnnouncement() {
  const title = document.getElementById("announcementTitle").value;
  const content = document.getElementById("announcementContent").value;
  const priority = document.getElementById("priority").value;
  const startTime = new Date().toISOString(); // التاريخ والوقت الحالي

  const data = JSON.parse(localStorage.getItem("announcements") || "[]");

  const announcement = { title, content, startTime, priority };

  if (editIndex !== null) {
    data[editIndex] = announcement;
    showToast("✏️ تم تعديل الإعلان");
  } else {
    data.push(announcement);
    showToast("📢 تم إضافة الإعلان");
  }

  localStorage.setItem("announcements", JSON.stringify(data));
  modal.classList.add("hidden");
  render();
}

// تعديل إعلان
function edit(i) {
  const data = JSON.parse(localStorage.getItem("announcements") || "[]");
  document.getElementById("announcementTitle").value = data[i].title;
  document.getElementById("announcementContent").value = data[i].content;
  document.getElementById("priority").value = data[i].priority;
  editIndex = i;
  modal.classList.remove("hidden");
}

// حذف إعلان
function remove(i) {
  if (confirm("هل أنت متأكد من حذف الإعلان؟")) {
    const data = JSON.parse(localStorage.getItem("announcements") || "[]");
    data.splice(i, 1);
    localStorage.setItem("announcements", JSON.stringify(data));
    render();
    showToast("✅ تم حذف الإعلان");
  }
}

// استماع لأحداث النموذج
form.onsubmit = (e) => {
  e.preventDefault();
  saveAnnouncement();
};

// تفعيل الوضع الليلي
darkToggle.onclick = () => {
  document.documentElement.classList.toggle("dark");
};

// فتح نافذة إضافة إعلان
addBtn.onclick = () => {
  form.reset();
  editIndex = null;
  modal.classList.remove("hidden");
};

// إغلاق النافذة
cancelBtn.onclick = () => {
  modal.classList.add("hidden");
};

// بدء العرض
render();
