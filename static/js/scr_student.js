const tabs = document.querySelector(".tabs");
const buttons = tabs.querySelectorAll("button");
const studentTable = document.getElementById("studentTable");
const line = document.querySelector(".line");
const studentBtn = document.getElementById("studentTab");
const sideBarSelector = document.querySelector(".selectorsCombined");
const allSelectors = document.querySelectorAll(".selectors");

let removeAllTables = function () {
  studentTable.classList.add("hidden"); // إخفاء جدول الطلاب فقط
};

let removeActiveBar = function () {
  allSelectors.forEach((selector) => {
    selector.classList.remove("activeBar");
  });
};

removeAllTables();
studentTable.classList.remove("hidden"); // عرض جدول الطلاب فقط
line.style.left = studentBtn.offsetLeft + "px";

sideBarSelector.addEventListener("click", function (selected) {
  const clickedSelector = selected.target;
  if (clickedSelector.className === "selectors default") {
    removeActiveBar();
    clickedSelector.classList.add("activeBar");
  }
});

tabs.addEventListener("click", function (button) {
  const clickedButton = button.target;

  if (clickedButton.tagName === "BUTTON") {
    removeActive();
    removeAllTables(); // إخفاء جدول الطلاب فقط
    clickedButton.classList.add("active");

    if (clickedButton.id === "studentTab") {
      studentTable.classList.remove("hidden"); // عرض جدول الطلاب فقط
    }

    line.style.width = clickedButton.offsetWidth + "px";
    line.style.left = clickedButton.offsetLeft + "px";
  }
});

// chart1
/**
 * ---------------------------------------
 * This demo was created using amCharts 5.
 *
 * For more information visit:
 * https://www.amcharts.com/
 *
 * Documentation is available at:
 * https://www.amcharts.com/docs/v5/
 * ---------------------------------------
 */

// Create root element
// https://www.amcharts.com/docs/v5/getting-started/#Root_element
var root = am5.Root.new("chartdiv1");

// Set themes
// https://www.amcharts.com/docs/v5/concepts/themes/
root.setThemes([am5themes_Animated.new(root)]);

// Create chart
// https://www.amcharts.com/docs/v5/charts/xy-chart/
var chart = root.container.children.push(
  am5xy.XYChart.new(root, {
    panX: true,
    panY: true,
    wheelX: "panX",
    wheelY: "zoomX",
    pinchZoomX: true,
    paddingLeft: 0,
    paddingRight: 1,
  })
);

// Add cursor
// https://www.amcharts.com/docs/v5/charts/xy-chart/cursor/
var cursor = chart.set("cursor", am5xy.XYCursor.new(root, {}));
cursor.lineY.set("visible", false);

// Create axes
// https://www.amcharts.com/docs/v5/charts/xy-chart/axes/
var xRenderer = am5xy.AxisRendererX.new(root, {
  minGridDistance: 0,
  minorGridEnabled: false,
});

xRenderer.labels.template.setAll({
  rotation: -90,
  centerY: am5.p50,
  centerX: am5.p100,
  paddingRight: 15,
});

xRenderer.grid.template.setAll({
  location: 1,
});

var xAxis = chart.xAxes.push(
  am5xy.CategoryAxis.new(root, {
    maxDeviation: 0.3,
    categoryField: "year",
    renderer: xRenderer,
    tooltip: am5.Tooltip.new(root, {}),
  })
);

var yRenderer = am5xy.AxisRendererY.new(root, {
  strokeOpacity: 0,
});

var yAxis = chart.yAxes.push(
  am5xy.ValueAxis.new(root, {
    maxDeviation: 0.3,
    renderer: yRenderer,
  })
);

yAxis.get("renderer").grid.template.set("forceHidden", true);
xAxis.get("renderer").grid.template.set("forceHidden", true);
// Create series
// https://www.amcharts.com/docs/v5/charts/xy-chart/series/
var series = chart.series.push(
  am5xy.ColumnSeries.new(root, {
    name: "Series 1",
    xAxis: xAxis,
    yAxis: yAxis,
    valueYField: "value",
    sequencedInterpolation: true,
    categoryXField: "year",
    tooltip: am5.Tooltip.new(root, {
      labelText: "{valueY}",
    }),
  })
);

series.columns.template.setAll({
  cornerRadiusTL: 5,
  cornerRadiusTR: 5,
  strokeOpacity: 0,
});
series.columns.template.adapters.add("fill", function (fill, target) {
  return chart.get("colors").getIndex(series.columns.indexOf(target));
});

series.columns.template.adapters.add("stroke", function (stroke, target) {
  return chart.get("colors").getIndex(series.columns.indexOf(target));
});

// Set data
var data = [
  {
    year: "2017",
    value: 650,
  },
  {
    year: "2018",
    value: 550,
  },
  {
    year: "2019",
    value: 700,
  },
  {
    year: "2020",
    value: 400,
  },
  {
    year: "2021",
    value: 800,
  },
  {
    year: "2022",
    value: 450,
  },
  {
    year: "2023",
    value: 750,
  },
  {
    year: "2024",
    value: 600,
  },
];

xAxis.data.setAll(data);
series.data.setAll(data);

// Make stuff animate on load
// https://www.amcharts.com/docs/v5/concepts/animations/
series.appear(1000);
chart.appear(1000, 100);

function toggleRightBar() {
  const rightBar = document.querySelector(".rightBar");
  rightBar.classList.toggle("visible"); // إظهار أو إخفاء الشريط الجانبي
}

document.addEventListener("DOMContentLoaded", function () {
  const studentButton = document.getElementById("studentButton");
  const studentSection = document.getElementById("studentSection");
  const teacherButton = document.getElementById("teacherButton");
  const teacherSection = document.getElementById("teacherSection");
  const searchBox = document.getElementById("search-box-students");
  

  
  studentButton.addEventListener("click", function () {
    toggleSections(studentSection);
    setTimeout(renderStudentTable, 100);
  });

  teacherButton.addEventListener("click", function () {
    toggleSections(teacherSection);
    // Set a timeout to load teacher data if needed
  });

  document
    .getElementById("search-box-students")
    .addEventListener("input", function () {
      const query = this.value.toLowerCase();
      filteredStudents = students.filter(
        (student) =>
          student.name.toLowerCase().includes(query) ||
          student.department.toLowerCase().includes(query) ||
          student.major.toLowerCase().includes(query)
      );
      currentPage = 1;
      renderStudentTable();
    });
  
  function setupEventListeners() {
    tabs.addEventListener("click", handleTabClick);
    sideBarSelector.addEventListener("click", handleSideBarClick);
    studentButton.addEventListener("click", () =>
      toggleSection(studentSection)
    );
    teacherButton.addEventListener("click", () =>
      toggleSection(teacherSection)
    );
    searchBox.addEventListener("input", handleSearchInput);
  }

  function renderStudentTable() {
    const tableBody = document.getElementById("studentTableBody");
    tableBody.innerHTML = "";

    filteredStudents.forEach((student) => {
      const row = document.createElement("tr");
      const statusColor = getStatusColor(student.status);
      row.innerHTML = `
        <td style="display: flex; align-items: center; gap: 0.5rem;">
          <img src="${student.avatar}" alt="Avatar" style="width:40px; height:40px; border-radius:50%;">
          <div>
            <b>${student.name}</b><br>
            <small style="color: var(--color-info);">${student.email}</small>
          </div>
        </td>
        <td>${student.department}</td>
        <td>${student.major}</td>
        <td style="color: ${statusColor}; font-weight: bold;">${student.status}</td>
        <td>${student.dateOfEnrollment}</td>
        <td>${student.location}</td>
      `;
      tableBody.appendChild(row);
    });
  }

  function getStatusColor(status) {
    switch (status.toLowerCase()) {
      case "active":
        return "green";
      case "inactive":
        return "red";
      case "onleave":
        return "orange";
      default:
        return "gray";
    }
  }

  // ===== تحميل بيانات من السيرفر =====
  fetch("/students1")
    .then((res) => res.json())
    .then((data) => {
      students = data;
      filteredStudents = [...students];
      renderStudentTable();
    })
    .catch((err) => console.error("Error fetching students:", err));

  init();


  function renderStudentPagination() {
    const pagination = document.getElementById("student-pagination");
    pagination.innerHTML = "";
    const totalPages = Math.ceil(filteredStudents.length / rowsPerPage);
    for (let i = 1; i <= totalPages; i++) {
      const btn = document.createElement("button");
      btn.innerText = i;
      if (i === currentPage) btn.classList.add("active");
      btn.addEventListener("click", () => {
        currentPage = i;
        renderStudentTable();
      });
      pagination.appendChild(btn);
    }
  }

  function toggleSections(showSection) {
    const allSections = document.querySelectorAll(".body > div");
    allSections.forEach((section) => {
      section.style.display = "none";
    });
    showSection.style.display = "block";
  }

  renderStudentTable();
});

const userRole = "{{ session['role'] }}"; // تحديد الدور في جافا سكربت

// دالة لجلب الإعلانات
function fetchAnnouncements() {
  fetch("/get_announcements")
    .then((response) => response.json())
    .then((data) => {
      const container = document.getElementById("announcements-container");
      container.innerHTML = ""; // تفريغ الحاوية السابقة

      if (data.length > 0) {
        data.forEach((announcement) => {
          const announcementDiv = document.createElement("div");
          announcementDiv.classList.add("announcement");
          announcementDiv.innerHTML = `
                  <h4>${announcement.type}</h4>
                  <p>${announcement.content}</p>
                  <p><strong>الأستاذ:</strong> ${
                    announcement.teacher_name
                      ? announcement.teacher_name
                      : "غير متوفر"
                  }</p>
                  <p class="text-muted">نُشر في: ${
                    announcement.timestamp || "غير متوفر"
                  }</p>
                `;
          container.appendChild(announcementDiv);
        });
      } else {
        container.innerHTML =
          "<p class='text-muted'>لا توجد إعلانات متاحة حاليًا.</p>";
      }
    })
    .catch((error) => {
      console.error("Error fetching announcements:", error);
    });
}

// استدعاء الدالة عند تحميل الصفحة
window.onload = function () {
  fetchAnnouncements(); // جلب الإعلانات عند تحميل الصفحة للطلاب فقط
};
