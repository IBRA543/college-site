function showHigherScores(studentMax, allData, studentNumber) {
  // التأكد من أن allData هو مصفوفة صالحة
  if (!Array.isArray(allData) || allData.length === 0) {
    alert("لا توجد بيانات صالحة للمقارنة.");
    return;
  }

  // تجميع أعلى نقطة واحدة لكل طالب مختلف عن الطالب الحالي
  let highestPerStudent = {};

  allData.forEach((entry) => {
    if (entry.student_number !== studentNumber) {
      if (
        !highestPerStudent[entry.student_number] ||
        entry.points > highestPerStudent[entry.student_number]
      ) {
        highestPerStudent[entry.student_number] = entry.points;
      }
    }
  });

  // استخراج النقاط الأعلى من نقطة الطالب الحالي
  let higherThanMax = Object.values(highestPerStudent)
    .filter((p) => p > studentMax) // تصفية النقاط الأعلى من نقطة الطالب
    .sort((a, b) => b - a) // ترتيب النقاط من الأعلى إلى الأدنى
    .slice(0, 5); // عرض أعلى 5 فقط

  // بناء الرسالة
  let message = `
          <p><span style="color: green; font-size: 24px;">&#9650</span> أعلى النقاط التي تفوق نتيجتك (${studentMax}):</p>
          <ul style="text-align:right; direction:rtl; margin-top: 10px;">
            ${
              higherThanMax.length > 0
                ? higherThanMax.map((p) => `<li>⭐ ${p}</li>`).join("")
                : "<li>لا توجد نقاط أعلى من نتيجتك.</li>"
            }
          </ul>
          <hr>
          <p><strong>شرح حساب النسبة المئوية مقارنة بأعلى نقطة في الفصل:</strong></p>
          <p>النسبة المئوية التي حصلت عليها تم حسابها بناءً على ترتيبك بين الطلاب من حيث أعلى نقطة.</p>
          <p><strong>الطريقة:</strong></p>
          <p>نقوم بحساب عدد الطلاب الذين حصلوا على نقاط أقل منك، ثم نحسب نسبتك وفق المعادلة التالية:</p>
          <pre>النسبة المئوية = (عدد الطلاب الذين حصلوا على نقاط أقل منك ÷ إجمالي عدد الطلاب) × 100</pre>
          <p><strong>مثال رقمي:</strong></p>
          <pre>أعلى نقطة في الفصل = 20</pre>
          <pre>نقطتك = 18</pre>
          <p>الطلاب الذين حصلوا على نقاط أقل من 18 = 4</p>
          <p>إجمالي عدد الطلاب = 7</p>
          <p>النسبة المئوية = (4 ÷ 7) × 100 ≈ 57.14%</p>
          <hr>
          <p><strong>ملاحظة:</strong> إذا كانت النتيجة 100%، فهذا يعني أن الطالب حصل على أعلى درجة في الفصل.</p>
        `;

  // عرض الرسالة باستخدام SweetAlert
  Swal.fire({
    title: "النقاط الأعلى من نتيجتك",
    html: message,
    icon: "info",
    confirmButtonText: "موافق",
    confirmButtonColor: "#7380ec",
    background: "#fff",
    color: "#363949",
  });
}

// دالة عرض النقاط الأدنى مع شرح بسيط
function showLowerScores(studentMin, allScores) {
  // العثور على النقاط الأدنى من النقطة الدنيا للطالب
  let lowerThanMin = allScores
    .filter((score) => score < studentMin)
    .sort((a, b) => a - b); // ترتيب النقاط من الأدنى إلى الأعلى

  // بناء الرسالة مع الشرح البسيط
  let message = `
          <p>🔻 الطلاب الذين حصلوا على نقاط أقل من نقطتك (${studentMin}):</p>
          <ul style="text-align:right; direction:rtl; margin-top: 10px;">
            ${lowerThanMin.map((score) => `<li>⭐ ${score}</li>`).join("")}
          </ul>
          <hr>
          <p><strong>شرح حساب النسبة المئوية مقارنة بأدنى نقطة في الفصل:</strong></p>
          <p>النسبة المئوية التي حصلت عليها تم حسابها بناءً على ترتيبك بين الطلاب من حيث أدنى نقطة.</p>
          <p><strong>الطريقة:</strong></p>
          <p>نقوم بحساب عدد الطلاب الذين حصلوا على نقاط أعلى منك، ثم نحسب نسبتك وفق المعادلة التالية:</p>
          <pre>النسبة المئوية = (عدد الطلاب الذين حصلوا على نقاط أعلى منك ÷ إجمالي عدد الطلاب) × 100</pre>
          <p>على سبيل المثال: إذا كانت أدنى نقطة في الفصل هي 5، وكانت نقطتك 7:</p>
          <p>1. أولاً، نحسب كم طالبًا حصلوا على نقاط أعلى من 7.</p>
          <p>2. ثم نحسب النسبة المئوية باستخدام المعادلة.</p>
          <hr>
          <p><strong>شرح المعادلة:</strong></p>
          <p>المعادلة تعتمد على تحديد الفرق بين نقطتك وأدنى نقطة في الفصل، ومن ثم مقارنة ذلك مع الفارق بين أعلى وأدنى نقطة في الفصل لحساب النسبة المئوية.</p>
          <p><strong>المعادلة:</strong></p>
          <p>النسبة المئوية = (عدد الطلاب الذين حصلوا على نقاط أعلى منك ÷ إجمالي عدد الطلاب) × 100</p>
          <p><strong>ملاحظة:</strong> كلما كانت النسبة أقرب للأدنى، ستكون النسبة المئوية أقل، وكلما كانت النقطة أقرب للأعلى، كلما كانت النسبة المئوية أعلى.</p>
        `;

  // عرض الرسالة باستخدام SweetAlert2
  Swal.fire({
    title: "نقاط أدنى",
    html: message,
    icon: "info",
    confirmButtonText: "موافق",
    confirmButtonColor: "#7380ec",
    background: "#fff",
    color: "#363949",
  });
}
function showHigherAverages(studentAvg, allAverages) {
  // العثور على المعدلات الأعلى من معدل الطالب
  let higherThanAvg = allAverages
    .filter((avg) => avg > studentAvg)
    .sort((a, b) => b - a); // ترتيب من الأعلى إلى الأدنى

  // بناء الرسالة مع الشرح
  let message = `
    <p>🔺 الطلاب الذين حصلوا على معدل أعلى من معدلك (${studentAvg.toFixed(
      1
    )}):</p>
    <ul style="text-align:right; direction:rtl; margin-top: 10px;">
      ${higherThanAvg.map((avg) => `<li>🌟 ${avg.toFixed(1)}</li>`).join("")}
    </ul>
    <hr>
    <p><strong>شرح حساب النسبة المئوية لمعدل الطالب:</strong></p>
    <p>النسبة المئوية تم حسابها بمقارنة معدلك بأعلى معدل تم تحقيقه في الفصل.</p>
    <p><strong>الطريقة:</strong></p>
    <p>نقوم بقسمة معدل الطالب على أعلى معدل في الفصل، ثم نحول الناتج إلى نسبة مئوية:</p>
    <pre>النسبة المئوية = (معدلك ÷ أعلى معدل) × 100</pre>
    <p>على سبيل المثال: إذا كان أعلى معدل هو 18، ومعدلك هو 15:</p>
    <p>1. نحسب النسبة: (15 ÷ 18) × 100 = 83.3%</p>
    <p>2. هذه النسبة تعكس مدى قربك من أفضل معدل في الفصل.</p>
    <hr>
    <p><strong>ملاحظات:</strong></p>
    <p>✔ كلما اقترب معدل الطالب من أعلى معدل في الفصل، ارتفعت نسبته المئوية.</p>
    <p>✔ يُشترط أن يكون لدى الطالب 7 نقاط لاحتساب المعدل.</p>
  `;

  // عرض الرسالة باستخدام SweetAlert2
  Swal.fire({
    title: "معدلات أعلى",
    html: message,
    icon: "info",
    confirmButtonText: "موافق",
    confirmButtonColor: "#00c292",
    background: "#fff",
    color: "#363949",
  });
}
function showLowerAverages(studentAvg, allAverages) {
  // العثور على المعدلات الأقل من معدل الطالب
  let lowerThanAvg = allAverages
    .filter((avg) => avg < studentAvg)
    .sort((a, b) => a - b); // ترتيب من الأدنى إلى الأعلى

  // بناء الرسالة مع الشرح
  let message = `
    <p>🔻 الطلاب الذين حصلوا على معدل أقل من معدلك (${studentAvg.toFixed(
      1
    )}):</p>
    <ul style="text-align:right; direction:rtl; margin-top: 10px;">
      ${lowerThanAvg.map((avg) => `<li>⭐ ${avg.toFixed(1)}</li>`).join("")}
    </ul>
    <hr>
    <p><strong>شرح حساب النسبة المئوية لمعدل الطالب:</strong></p>
    <p>النسبة المئوية تم احتسابها بمقارنة معدلك بأدنى معدل في الفصل.</p>
    <p><strong>الطريقة:</strong></p>
    <p>نحسب مدى اقتراب معدل الطالب من أدنى معدل باستخدام الفارق بين المعدل الأدنى والمعدل الأعلى:</p>
    <pre>النسبة المئوية = 100 - ((معدلك - أدنى معدل) ÷ (أعلى معدل - أدنى معدل)) × 100</pre>
    <p>على سبيل المثال: إذا كان أدنى معدل هو 9، وأعلى معدل 17، ومعدلك 11:</p>
    <p>1. نحسب النسبة: 100 - ((11 - 9) ÷ (17 - 9)) × 100 = 75%</p>
    <p>2. كلما اقترب المعدل من الحد الأدنى، قلت النسبة المئوية، والعكس.</p>
    <hr>
    <p><strong>ملاحظات:</strong></p>
    <p>✔ النسبة تعتمد على موقع المعدل بين الحد الأدنى والأعلى في الفصل.</p>
    <p>✔ يُشترط أن يكون لدى الطالب 7 نقاط لاحتساب المعدل.</p>
  `;

  // عرض الرسالة باستخدام SweetAlert2
  Swal.fire({
    title: "معدلات أقل",
    html: message,
    icon: "info",
    confirmButtonText: "موافق",
    confirmButtonColor: "#f44336",
    background: "#fff",
    color: "#363949",
  });
}
function showSuccessRate(studentSuccessRate, allSuccessRates) {
  // العثور على النسب التي أقل من نسبة النجاح للطالب
  let lowerThanSuccessRate = allSuccessRates
    .filter((rate) => rate < studentSuccessRate)
    .sort((a, b) => a - b); // ترتيب من الأدنى إلى الأعلى

  // بناء الرسالة مع الشرح
  let message = `
    <p>🔻 الطلاب الذين حصلوا على نسبة نجاح أقل من نسبتك (${studentSuccessRate.toFixed(
      1
    )}%):</p>
    <ul style="text-align:right; direction:rtl; margin-top: 10px;">
      ${lowerThanSuccessRate
        .map((rate) => `<li>⭐ ${rate.toFixed(1)}%</li>`)
        .join("")}
    </ul>
    <hr>
    <p><strong>شرح حساب نسبة النجاح:</strong></p>
    <p>النسبة تم احتسابها بناءً على أعلى وأدنى معدلات الفصل، مع تحديد كيف يتوزع نجاح الطلاب.</p>
    <p><strong>الطريقة:</strong></p>
    <p>نحسب الفرق بين معدلك وأعلى وأدنى معدل، ومن ثم نقارن هذه النسبة ببقية الطلاب:</p>
    <pre>النسبة = 100 - ((معدلك - أدنى معدل) ÷ (أعلى معدل - أدنى معدل)) × 100</pre>
    <p>على سبيل المثال: إذا كان المعدل الأدنى 9، وأعلى معدل 17، ومعدلك 13:</p>
    <p>1. نحسب النسبة: 100 - ((13 - 9) ÷ (17 - 9)) × 100 = 50%</p>
    <p>2. كلما اقترب المعدل من الأعلى، تزيد النسبة المئوية.</p>
    <hr>
    <p><strong>ملاحظات:</strong></p>
    <p>✔ النسبة تعتمد على موقع المعدل بين الحد الأدنى والأعلى في الفصل.</p>
  `;

  // عرض الرسالة باستخدام SweetAlert2
  Swal.fire({
    title: "نسبة النجاح",
    html: message,
    icon: "info",
    confirmButtonText: "موافق",
    confirmButtonColor: "#4caf50",
    background: "#fff",
    color: "#363949",
  });
}

const updatesDiv = document.querySelector(".updates");
const studentName = "{{ student.name }}";
let userScrolledUp = false;

updatesDiv.addEventListener("scroll", () => {
  userScrolledUp =
    updatesDiv.scrollTop <
    updatesDiv.scrollHeight - updatesDiv.clientHeight - 50;
});

function shareMessage() {
  const messageInput = document.getElementById("new-message");
  const message = messageInput.value.trim();
  const emailInput = document.getElementById("email");
  const email = emailInput ? emailInput.value.trim() : "";

  if (message !== "") {
    fetch("/send_message", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: studentName,
        message: message,
        email: email,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "success") {
          addMessageToDOM(
            studentName,
            email,
            message,
            new Date().toLocaleString()
          );

          if (!userScrolledUp) {
            setTimeout(() => {
              updatesDiv.scrollTop = updatesDiv.scrollHeight;
            }, 100);
          }

          messageInput.value = "";
          if (emailInput) emailInput.value = "";
        } else {
          alert("فشل إرسال الرسالة.");
        }
      });
  } else {
    alert("الرجاء كتابة رسالة أولاً.");
  }
}

function addMessageToDOM(name, email, message, timestamp) {
  const newMessageDiv = document.createElement("div");
  newMessageDiv.classList.add("message");

  const isCurrentUser = name === studentName;
  const deleteButton = isCurrentUser
    ? `<button onclick="deleteMessage(this)">🗑️ حذف</button>`
    : "";

  newMessageDiv.innerHTML = `
    <span class="material-icons-sharp more-options">more_vert</span>
    <div class="options-menu" style="display: none;">
      <button onclick="reportMessage(this)">🚨 إبلاغ</button>
      <div class="reactions">
        <span onclick="reactToMessage(this)">❤️</span>
        <span onclick="reactToMessage(this)">😆</span>
        <span onclick="reactToMessage(this)">👍</span>
        <span onclick="reactToMessage(this)">👎</span>
        <span onclick="reactToMessage(this)">😢</span>
      </div>
      ${deleteButton}
    </div>
    <p><b>${name} ${email ? `(${email})` : ""}:</b> ${message}</p>
    <small class="text-muted">${timestamp}</small>
  `;

  document.getElementById("updates").appendChild(newMessageDiv);
  bindMoreOptionsEvents();
}

function bindMoreOptionsEvents() {
  const moreOptions = document.querySelectorAll(".more-options");

  moreOptions.forEach((icon) => {
    if (!icon.dataset.bound) {
      icon.addEventListener("click", function (e) {
        e.stopPropagation();
        const currentMenu = this.nextElementSibling;

        document.querySelectorAll(".options-menu").forEach((menu) => {
          if (menu !== currentMenu) menu.style.display = "none";
        });

        currentMenu.style.display =
          currentMenu.style.display === "block" ? "none" : "block";
      });

      icon.dataset.bound = "true";
    }
  });
}

function reportMessage(button) {
  alert("تم إرسال الإبلاغ. شكراً لتواصلك.");
  button.parentElement.style.display = "none";
}

function reactToMessage(emojiSpan) {
  const reaction = emojiSpan.textContent;
  const parentMessage = emojiSpan.closest(".message");
  const existingReaction = parentMessage.querySelector(".reaction-display");

  if (existingReaction) {
    existingReaction.textContent = reaction;
  } else {
    const reactionDisplay = document.createElement("div");
    reactionDisplay.classList.add("reaction-display");
    reactionDisplay.textContent = reaction;
    parentMessage.appendChild(reactionDisplay);
  }

  emojiSpan.closest(".options-menu").style.display = "none";
}

function deleteMessage(button) {
  const messageDiv = button.closest(".message");
  const messageText = messageDiv.querySelector("p").innerText.trim(); // إضافة strip
  const timestamp = messageDiv.querySelector("small").innerText.trim(); // إضافة strip

  // طباعة لتوضيح النص الذي يتم إرساله
  console.log("Message text:", messageText);
  console.log("Timestamp:", timestamp);

  fetch("/delete_message", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ messageText, timestamp }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "success") {
        messageDiv.remove();
      } else {
        alert("فشل حذف الرسالة.");
      }
    });
}

// عند تحميل الصفحة
document.addEventListener("DOMContentLoaded", function () {
  bindMoreOptionsEvents();

  // إغلاق القوائم عند النقر في أي مكان بالخارج
  document.addEventListener("click", () => {
    document.querySelectorAll(".options-menu").forEach((menu) => {
      menu.style.display = "none";
    });
  });

  // جلب الرسائل السابقة من السيرفر
  fetch("/messages")
    .then((res) => res.json())
    .then((messages) => {
      messages.forEach((msg) => {
        addMessageToDOM(msg.name, msg.email, msg.message, msg.timestamp);
      });

      updatesDiv.scrollTop = updatesDiv.scrollHeight;
    });
});
