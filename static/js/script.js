document.addEventListener("DOMContentLoaded", () => {
  const sortableList = document.querySelector(".sortable-list");
  const items = sortableList.querySelectorAll(".item");

  items.forEach((item) => {
    item.addEventListener("dragstart", () => {
      setTimeout(() => item.classList.add("dragging"), 0);
    });

    item.addEventListener("dragend", () => {
      item.classList.remove("dragging");
      showStatusMessage();
    });
  });

  const initSortableList = (e) => {
    e.preventDefault();
    const draggingItem = document.querySelector(".dragging");

    let siblings = [...sortableList.querySelectorAll(".item:not(.dragging)")];
    let nextSibling = siblings.find((sibling) => {
      return e.clientY <= sibling.offsetTop + sibling.offsetHeight / 2;
    });

    sortableList.insertBefore(draggingItem, nextSibling);
  };

  sortableList.addEventListener("dragover", initSortableList);
  sortableList.addEventListener("dragenter", (e) => e.preventDefault());

  const showStatusMessage = () => {
    const message = document.getElementById("status-message");
    message.style.display = "block";
    setTimeout(() => {
      message.style.display = "none";
    }, 2000);
  };
});
