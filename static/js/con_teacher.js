// Buttons and Sections
const dashboardElements = document.querySelectorAll(
  ".topBar, .cardsContainer, .secondRow, .database"
);
const overviewButton = document.getElementById("overviewButton");
const teacherButton = document.getElementById("teacherButton");
const resultsButton = document.getElementById("resultsButton");
const announcementsButton = document.getElementById("announcementsButton");

const overviewSection = document.getElementById("overviewSection");
const teacherSection = document.getElementById("teacherSection");
const resultsSection = document.getElementById("resultsSection");
const announcementsSection = document.getElementById("announcements-section");

function toggleSections(showSection) {
  const allSections = document.querySelectorAll(
    ".body > div, .topBar, .cardsContainer, .secondRow, .database"
  );
  allSections.forEach((section) => {
    section.style.display = "none";
  });

  if (
    NodeList.prototype.isPrototypeOf(showSection) ||
    Array.isArray(showSection)
  ) {
    showSection.forEach((el) => {
      el.style.display = "block";
    });
  } else {
    showSection.style.display = "block";
  }
}

overviewButton.addEventListener("click", function () {
  toggleSections(overviewSection);
  setTimeout(drawSmallChart, 100);
});

teacherButton.addEventListener("click", function () {
  toggleSections(teacherSection);
  setTimeout(loadTeacherData, 100);
});

resultsButton.addEventListener("click", function () {
  toggleSections(resultsSection);
  const studentFormContainer = document.getElementById("studentFormContainer");
  studentFormContainer.style.display = "block";
  setTimeout(loadResultsData, 100);
});

announcementsButton.addEventListener("click", function () {
  toggleSections(announcementsSection);
});

dashboardButton.addEventListener("click", function () {
  toggleSections(dashboardElements);
});
