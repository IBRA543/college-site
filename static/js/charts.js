// النقاط الخاصة بكل نوع من المخططات
const points = {
    barChart: 85,
    lineChart: 70,
    pieChart: 95,
    doughnutChart: 60,
    polarChart: 80,
    compareChart: 75,
  };
  
  // تحديث الملاحظات والنصائح بناءً على النقاط
  function updateNotesAndTips() {
    for (const chartId in points) {
      const pointsValue = points[chartId];
      const capitalizedId = chartId.charAt(0).toUpperCase() + chartId.slice(1);
  
      const noteElement = document.getElementById(`note${capitalizedId}`);
      const tipElement = document.getElementById(`tip${capitalizedId}`);
  
      // الملاحظات
      if (pointsValue >= 90) {
        noteElement.innerHTML = "📌 ملاحظة: أداء ممتاز! استمر في العمل الجاد.";
      } else if (pointsValue >= 75) {
        noteElement.innerHTML = "📌 ملاحظة: أداء جيد، يمكن تحسين بعض الجوانب.";
      } else {
        noteElement.innerHTML = "📌 ملاحظة: تحتاج إلى تحسين أدائك في بعض المواد.";
      }
  
      // النصائح
      if (pointsValue >= 90) {
        tipElement.innerHTML = "💡 نصيحة: حافظ على تركيزك وابدأ التفكير في التحديات الأكبر!";
      } else if (pointsValue >= 75) {
        tipElement.innerHTML = "💡 نصيحة: استمر في المراجعة وركز على تحسين نقاط الضعف.";
      } else {
        tipElement.innerHTML = "💡 نصيحة: قم بوضع خطة لتحسين النقاط الضعيفة.";
      }
    }
  }
  updateNotesAndTips();
  
  // البيانات القادمة من السيرفر
  const labels = {{ data|map(attribute='subject')|list|tojson|safe }};
  const pointsData = {{ data|map(attribute='points')|list|tojson|safe }};

  
  // تصفية البيانات غير الصالحة
  const filteredLabels = [];
  const filteredPoints = [];
  
  for (let i = 0; i < pointsData.length; i++) {
    const val = parseFloat(pointsData[i]);
    if (!isNaN(val)) {
      filteredLabels.push(labels[i]);
      filteredPoints.push(val);
    }
  }
  
  // رسم المخطط الشريطي
  new Chart(document.getElementById('barChart'), {
    type: 'bar',
    data: {
      labels: filteredLabels,
      datasets: [{
        label: 'النقطة حسب المادة',
        data: filteredPoints,
        backgroundColor: '#3498db',
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'مخطط شريطي للنقاط',
        }
      }
    }
  });
  
  // رسم المخطط الخطي
  new Chart(document.getElementById('lineChart'), {
    type: 'line',
    data: {
      labels: filteredLabels,
      datasets: [{
        label: 'تطور النقطة',
        data: filteredPoints,
        borderColor: '#2ecc71',
        fill: false,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'منحنى تطور النقاط',
        }
      }
    }
  });
  
  // رسم المخطط الدائري
  new Chart(document.getElementById('pieChart'), {
    type: 'pie',
    data: {
      labels: filteredLabels,
      datasets: [{
        label: 'نسب النقاط',
        data: filteredPoints,
        backgroundColor: filteredLabels.map(() => 
          '#' + Math.floor(Math.random() * 16777215).toString(16))
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'نسبة توزيع النقاط حسب المادة',
        }
      }
    }
  });
  
  // توليد ألوان HSL عشوائية
  const generateColors = (count) => {
    return Array.from({ length: count }, () =>
      `hsl(${Math.floor(Math.random() * 360)}, 70%, 60%)`
    );
  };
  
  const colors = generateColors(filteredLabels.length);
  
  // رسم مخطط الدونات
  new Chart(document.getElementById('doughnutChart'), {
    type: 'doughnut',
    data: {
      labels: filteredLabels,
      datasets: [{
        label: 'نقاط',
        data: filteredPoints,
        backgroundColor: colors
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'مخطط الدونات للنقاط',
        },
        tooltip: {
          callbacks: {
            label: ctx => `المادة: ${ctx.label} - ${ctx.parsed}`
          }
        }
      },
      animation: {
        animateScale: true
      }
    }
  });
  
  // رسم المخطط القطبي
  new Chart(document.getElementById('polarChart'), {
    type: 'polarArea',
    data: {
      labels: filteredLabels,
      datasets: [{
        label: 'نقاط',
        data: filteredPoints,
        backgroundColor: colors
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'مخطط قطبي متقدم',
        }
      },
      animation: {
        animateRotate: true,
        animateScale: true
      }
    }
  });
  
  // بيانات الفصول
  const semester1Data = {{ data|selectattr("semester", "equalto", "الفصل الأول") }};
  const semester2Data = {{ data|selectattr("semester", "equalto", "الفصل الثاني") }};
  const semester3Data = {{ data|selectattr("semester", "equalto", "الفصل الثالث") }};
  const semester4Data = {{ data|selectattr("semester", "equalto", "الفصل الرابع") }};
  const semester5Data = {{ data|selectattr("semester", "equalto", "الفصل الخامس") }};
  const semester6Data = {{ data|selectattr("semester", "equalto", "الفصل السادس") }};
  
  // حساب المعدل لكل فصل
  const calculateAverage = (data) => {
    const totalPoints = data.reduce((sum, item) => sum + parseFloat(item.points), 0);
    const totalSubjects = data.length;
    return totalSubjects > 0 ? totalPoints / totalSubjects : 0;
  };
  
  const semester1Average = calculateAverage(semester1Data);
  const semester2Average = calculateAverage(semester2Data);
  const semester3Average = calculateAverage(semester3Data);
  const semester4Average = calculateAverage(semester4Data);
  const semester5Average = calculateAverage(semester5Data);
  const semester6Average = calculateAverage(semester6Data);
  
  // رسم مخطط المقارنة بين الفصول
  new Chart(document.getElementById('compareChart'), {
    type: 'bar',
    data: {
      labels: [
        'الفصل الأول',
        'الفصل الثاني',
        'الفصل الثالث',
        'الفصل الرابع',
        'الفصل الخامس',
        'الفصل السادس'
      ],
      datasets: [{
        label: 'النقطة الإجمالية',
        data: [
          semester1Average,
          semester2Average,
          semester3Average,
          semester4Average,
          semester5Average,
          semester6Average
        ],
        backgroundColor: [
          'rgba(52, 152, 219, 0.7)',   // الأول
          'rgba(231, 76, 60, 0.7)',    // الثاني
          'rgba(46, 204, 113, 0.7)',   // الثالث
          'rgba(241, 196, 15, 0.7)',   // الرابع
          'rgba(155, 89, 182, 0.7)',   // الخامس
          'rgba(241, 148, 138, 0.7)'   // السادس
        ]
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: '📚 مقارنة النقاط الإجمالية بين الفصول',
        }
      }
    }
  });






  