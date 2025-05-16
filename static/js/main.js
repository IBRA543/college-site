document.addEventListener("DOMContentLoaded", function () {
  var swiper = new Swiper(".swiper", {
    effect: "cube",
    grabCursor: true,
    allowTouchMove: true,
    cubeEffect: {
      shadow: true,
      slideShadows: true,
      shadowOffset: 20,
      shadowScale: 0.94,
    },
    mousewheel: {
      forceToAxis: true,
      sensitivity: 0.3, // تخفيض الحساسية
      releaseOnEdges: true, // يمنع الانتقال العنيف في الحواف
      thresholdDelta: 30, // تجاهل الحركات الصغيرة
      thresholdTime: 500, // يمنع الانتقالات المتتالية السريعة
    },
    on: {
      slideChange: function () {
        // تحديث الزر المحدد عند التمرير
        const activeIndex = this.activeIndex;
        document
          .querySelectorAll(".Links li")
          .forEach((li) => li.classList.remove("activeLink"));
        document
          .querySelectorAll(".Links li")
          [activeIndex].classList.add("activeLink");
      },
    },
  });

  window.Navigate = function (indx) {
    // إزالة التحديد من جميع الأزرار
    document
      .querySelectorAll(".Links li")
      .forEach((li) => li.classList.remove("activeLink"));
    // إضافة التحديد للزر الحالي
    document.querySelectorAll(".Links li")[indx].classList.add("activeLink");
    // التبديل إلى الشريحة المناسبة
    swiper.slideTo(indx, 1000, true);
  };
});
