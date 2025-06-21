document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("#dataForm");
  const cneInput = document.getElementById("id_card");
  const majorInput = document.getElementById("major");
  const errorMessage = document.getElementById("error-message");

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    let id_card = cneInput.value.trim().replace(/[‏‎؜]/g, "");
    let major = majorInput.value.trim();
    const cneRegex = /^[A-Za-z]+\d{4,6}$/;
    const majorRegex = /^[A-Za-z]\d{9}$/;

    if (!cneRegex.test(id_card) || !majorRegex.test(major)) {
      showError("❌ المعلومات غير صحيحة");
      return;
    }

    fetch("/Student_space", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ id_card, major }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          document.body.innerHTML = data.html;
        } else {
          showError(data.error);
        }
      })
      .catch(() => {
        showError("❌  حدث خطأ أثناء البحث");
      });
  });

  function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = "block";
    setTimeout(() => {
      errorMessage.style.display = "none";
    }, 3000);
  }

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

const employees = [
  {
    name: "John Doe",
    email: "john.doe@example.com",
    avatar: "static/images/profile-3.jpg",
    department: "Engineering",
    title: "Software Engineer",
    hireDate: "Jun 15, 2020",
    location: "New York",
    status: "active",
  },
  {
    name: "Jane Smith",
    email: "jane.smith@example.com",
    avatar: "static/images/profile-3.jpg",
    department: "Marketing",
    title: "Marketing Manager",
    hireDate: "Sep 23, 2018",
    location: "San Francisco",
    status: "onleave",
  },
  {
    name: "Carl Newton",
    email: "carl.newton@example.com",
    avatar: "https://i.pravatar.cc/150?img=3",
    department: "Human Resources",
    title: "HR Specialist",
    hireDate: "Mar 10, 2021",
    location: "Austin",
    status: "active",
  },
  {
    name: "Emily Davis",
    email: "emily.davis@example.com",
    avatar: "https://i.pravatar.cc/150?img=4",
    department: "Finance",
    title: "Financial Analyst",
    hireDate: "Nov 6, 2019",
    location: "Chicago",
    status: "inactive",
  },
  {
    name: "Michael Brown",
    email: "michael.brown@example.com",
    avatar: "https://i.pravatar.cc/150?img=5",
    department: "Engineering",
    title: "DevOps Engineer",
    hireDate: "Jan 12, 2022",
    location: "Seattle",
    status: "active",
  },
  {
    name: "Nora Thomas",
    email: "nora.thomas@example.com",
    avatar: "https://i.pravatar.cc/150?img=6",
    department: "Marketing",
    title: "Content Strategist",
    hireDate: "May 19, 2023",
    location: "Denver",
    status: "active",
  },
  {
    name: "John Doe",
    email: "john.doe@example.com",
    avatar: "static/images/profile-3.jpg",
    department: "Engineering",
    title: "Software Engineer",
    hireDate: "Jun 15, 2020",
    location: "New York",
    status: "active",
  },
  {
    name: "Jane Smith",
    email: "jane.smith@example.com",
    avatar: "static/images/profile-3.jpg",
    department: "Marketing",
    title: "Marketing Manager",
    hireDate: "Sep 23, 2018",
    location: "San Francisco",
    status: "onleave",
  },
  {
    name: "Carl Newton",
    email: "carl.newton@example.com",
    avatar: "https://i.pravatar.cc/150?img=3",
    department: "Human Resources",
    title: "HR Specialist",
    hireDate: "Mar 10, 2021",
    location: "Austin",
    status: "active",
  },
];
let filteredEmployees = [...employees];
const rowsPerPage = 3;
let currentPage = 1;

document.getElementById("search-box").addEventListener("input", function () {
  const query = this.value.toLowerCase();
  filteredEmployees = employees.filter(
    (emp) =>
      emp.name.toLowerCase().includes(query) ||
      emp.email.toLowerCase().includes(query)
  );
  currentPage = 1;
  renderTable();
});

function renderTable() {
  const tbody = document.getElementById("employee-body");
  tbody.innerHTML = "";
  const start = (currentPage - 1) * rowsPerPage;
  const paginatedItems = filteredEmployees.slice(start, start + rowsPerPage);
  for (const emp of paginatedItems) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="name-cell">
        <img class="avatar" src="${emp.avatar}" alt="">
        <div>
          <strong>${emp.name}</strong><br>
          <small style="color: gray; font-size: 12px">${emp.email}</small>
        </div>
      </td>
      <td><span class="badge">${emp.department}</span></td>
      <td>${emp.title}</td>
      <td>${emp.hireDate}</td>
      <td>${emp.location}</td>
      <td class="status ${emp.status.toLowerCase()}">${emp.status}</td>
    `;
    tbody.appendChild(tr);
  }
  document.getElementById(
    "total-count"
  ).innerText = `(${filteredEmployees.length})`;
  renderPagination();
}

let smallChartRoot = null;
function drawSmallChart() {
  // إذا كان هناك جذر موجود مسبقًا، دمره أولًا
  if (smallChartRoot) {
    smallChartRoot.dispose();
  }

  smallChartRoot = am5.Root.new("smallChart");

  smallChartRoot.setThemes([am5themes_Animated.new(smallChartRoot)]);

  let chart = smallChartRoot.container.children.push(
    am5percent.PieChart.new(smallChartRoot, {
      innerRadius: am5.percent(40),
    })
  );

  let series = chart.series.push(
    am5percent.PieSeries.new(smallChartRoot, {
      valueField: "value",
      categoryField: "category",
    })
  );

  series.data.setAll([
    { category: "ناجح", value: 85 },
    { category: "راسب", value: 15 },
  ]);

  series.appear(1000, 100);
}
function loadTeacherData() {
  console.log("loadTeacherData غير معرفة حاليًا.");
}

function renderPagination() {
  const pagination = document.getElementById("pagination");
  pagination.innerHTML = "";
  const totalPages = Math.ceil(filteredEmployees.length / rowsPerPage);
  for (let i = 1; i <= totalPages; i++) {
    const btn = document.createElement("button");
    btn.innerText = i;
    if (i === currentPage) btn.classList.add("active");
    btn.addEventListener("click", () => {
      currentPage = i;
      renderTable();
    });
    pagination.appendChild(btn);
  }
}

renderTable();

// am5 chart setup
am5.ready(function () {
  let root = am5.Root.new("chartdiv2");
  root.setThemes([am5themes_Animated.new(root)]);

  let chart = root.container.children.push(
    am5percent.PieChart.new(root, {
      endAngle: 270,
      layout: root.verticalLayout,
      innerRadius: am5.percent(60),
    })
  );

  let series = chart.series.push(
    am5percent.PieSeries.new(root, {
      valueField: "value",
      categoryField: "category",
      endAngle: 270,
      labelsEnabled: false,
    })
  );

  series.set(
    "colors",
    am5.ColorSet.new(root, {
      colors: [am5.color(0x7e57c2), am5.color(0x42a5f5)],
    })
  );

  let data = [
    { category: "Male", value: 45 },
    { category: "Female", value: 55 },
  ];

  series.data.setAll(data);

  let legend = chart.children.push(
    am5.Legend.new(root, {
      centerX: am5.percent(50),
      x: am5.percent(50),
      marginTop: 15,
      marginBottom: 15,
    })
  );
  legend.markerRectangles.template.adapters.add("fillGradient", function () {
    return undefined;
  });
  legend.data.setAll(series.dataItems);
  series.appear(1000, 100);
});
