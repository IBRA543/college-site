let sidebar = document.querySelector(".sidebar");
let toggleBtn = document.querySelector("#toggle-btn");
let arrows = document.querySelectorAll(".arrow");

toggleBtn.onclick = () => {
  sidebar.classList.toggle("close");
};

arrows.forEach((arrow) => {
  arrow.addEventListener("click", (e) => {
    let parent = e.target.closest("li");
    parent.classList.toggle("showMenu");
  });
});
