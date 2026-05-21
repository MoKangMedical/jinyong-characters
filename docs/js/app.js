/**
 * 金庸武侠人物谱研究院 — 商业化系统 v3.1
 * 包含：付费体系、互动答题、进度追踪、结业证书
 */

(function() {
  'use strict';

  // ==================== CONFIG ====================
  var STORAGE_KEY = 'jinyong_academy';
  var FREE_COUNT = 20; // Free courses
  var COURSE_PRICE = 29.99; // USD
  var SUBSCRIPTION_KEYS = {
    'JINYONG2025': { type: 'lifetime', name: '终身会员' },
    'WUXIA2025': { type: 'annual', name: '年度会员' },
  };

  // ==================== STATE ====================
  function getState() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
    } catch(e) {
      return {};
    }
  }

  function saveState(state) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }

  // ==================== MEMBERSHIP SYSTEM ====================
  window.JYMembership = {
    isActive: function() {
      var state = getState();
      if (state.membershipKey && state.membershipType) {
        if (state.membershipType === 'lifetime') return true;
        if (state.membershipType === 'annual') {
          var expiry = state.membershipExpiry;
          if (expiry && Date.now() < expiry) return true;
        }
      }
      return false;
    },

    activate: function(key) {
      var sub = SUBSCRIPTION_KEYS[key.trim().toUpperCase()];
      if (!sub) return { success: false, message: '无效的激活码' };
      
      var state = getState();
      state.membershipKey = key.trim().toUpperCase();
      state.membershipType = sub.type;
      state.membershipName = sub.name;
      if (sub.type === 'annual') {
        state.membershipExpiry = Date.now() + 365 * 24 * 60 * 60 * 1000;
      }
      state.activatedAt = Date.now();
      saveState(state);
      return { success: true, message: sub.name + '激活成功！' };
    },

    canAccess: function(courseIndex) {
      if (courseIndex === undefined) return false;
      if (courseIndex < FREE_COUNT) return true;
      return this.isActive();
    },

    getStatus: function() {
      var state = getState();
      if (!state.membershipKey) return { type: 'free', name: '免费用户' };
      if (state.membershipType === 'lifetime') return { type: 'lifetime', name: '终身会员', key: state.membershipKey };
      if (state.membershipType === 'annual') {
        var expired = state.membershipExpiry && Date.now() > state.membershipExpiry;
        if (expired) return { type: 'expired', name: '年度会员(已过期)', key: state.membershipKey };
        return { type: 'annual', name: '年度会员', key: state.membershipKey, expiry: state.membershipExpiry };
      }
      return { type: 'free', name: '免费用户' };
    }
  };

  // ==================== QUIZ SYSTEM ====================
  window.JYQuiz = {
    submit: function(questionIndex, selectedAnswer) {
      var quizzes = window.JY_QUIZ_DATA;
      if (!quizzes) return { error: '题库未加载' };
      
      var q = quizzes[questionIndex];
      if (!q) return { error: '题目不存在' };
      
      var correct = selectedAnswer === q.answer;
      return {
        correct: correct,
        question: q.question,
        yourAnswer: selectedAnswer,
        correctAnswer: q.answer,
        explanation: q.explanation || ''
      };
    },

    gradeAll: function(answers) {
      var quizzes = window.JY_QUIZ_DATA;
      if (!quizzes) return { error: '题库未加载' };
      
      var correct = 0;
      var results = [];
      for (var i = 0; i < quizzes.length; i++) {
        var q = quizzes[i];
        var selected = answers[i];
        var isCorrect = selected === q.answer;
        if (isCorrect) correct++;
        results.push({
          index: i,
          correct: isCorrect,
          question: q.question,
          yourAnswer: selected,
          correctAnswer: q.answer
        });
      }
      return {
        score: correct,
        total: quizzes.length,
        percentage: Math.round((correct / quizzes.length) * 100),
        results: results
      };
    }
  };

  // ==================== PROGRESS TRACKING ====================
  window.JYProgress = {
    markComplete: function(courseId) {
      var state = getState();
      if (!state.completed) state.completed = [];
      if (state.completed.indexOf(courseId) === -1) {
        state.completed.push(courseId);
      }
      state.lastCourse = courseId;
      state.lastVisit = Date.now();
      saveState(state);
      return state.completed.length;
    },

    isComplete: function(courseId) {
      var state = getState();
      return state.completed && state.completed.indexOf(courseId) !== -1;
    },

    getCompleted: function() {
      var state = getState();
      return state.completed || [];
    },

    getProgress: function(totalCourses) {
      var completed = this.getCompleted().length;
      return {
        completed: completed,
        total: totalCourses || 151,
        percentage: totalCourses ? Math.round((completed / totalCourses) * 100) : 0
      };
    },

    getNovelProgress: function(novelChars) {
      var completed = this.getCompleted();
      var total = 0, done = 0;
      for (var i = 0; i < novelChars.length; i++) {
        total++;
        if (completed.indexOf(novelChars[i]) !== -1) done++;
      }
      return { done: done, total: total, complete: done === total };
    }
  };

  // ==================== QUIZ UI RENDERER ====================
  window.JYQuizUI = {
    init: function() {
      var containers = document.querySelectorAll('.jy-quiz-container');
      if (!containers.length) return;

      var quizzes = window.JY_QUIZ_DATA;
      if (!quizzes) {
        for (var i = 0; i < containers.length; i++) {
          containers[i].innerHTML = '<p style="color:#a0a0ab;text-align:center;">题库加载中...</p>';
        }
        return;
      }

      // Filter by course ID
      var courseId = document.body.getAttribute('data-course-id');
      var filtered = quizzes;
      if (courseId) {
        filtered = quizzes.filter(function(q) { return q.id === courseId; });
      }

      for (var i = 0; i < containers.length; i++) {
        if (i >= filtered.length) break;
        this.renderQuiz(containers[i], i, filtered[i]);
      }
    },

    renderQuiz: function(container, index, quiz) {
      var html = '<div class="jy-quiz" data-index="' + index + '">';
      html += '<h3 class="jy-quiz-title">知识测验 ' + (index + 1) + '</h3>';
      html += '<p class="jy-quiz-question">' + quiz.question + '</p>';
      html += '<div class="jy-quiz-options">';
      
      for (var i = 0; i < quiz.options.length; i++) {
        var letter = String.fromCharCode(65 + i); // A, B, C, D
        html += '<label class="jy-option">';
        html += '<input type="radio" name="jy-q' + index + '" value="' + letter + '">';
        html += '<span class="jy-option-letter">' + letter + '</span>';
        html += '<span class="jy-option-text">' + quiz.options[i] + '</span>';
        html += '</label>';
      }
      
      html += '</div>';
      html += '<button class="jy-submit-btn" onclick="JYQuizUI.submitOne(' + index + ')">提交答案</button>';
      html += '<div class="jy-feedback" id="jy-fb-' + index + '"></div>';
      html += '</div>';
      
      container.innerHTML = html;
    },

    submitOne: function(index) {
      var selected = document.querySelector('input[name="jy-q' + index + '"]:checked');
      var feedback = document.getElementById('jy-fb-' + index);
      
      if (!selected) {
        feedback.innerHTML = '<p style="color:#f59e0b;">请先选择一个答案</p>';
        feedback.style.display = 'block';
        return;
      }
      
      var result = window.JYQuiz.submit(index, selected.value);
      if (result.error) {
        feedback.innerHTML = '<p style="color:#ef4444;">' + result.error + '</p>';
        return;
      }
      
      if (result.correct) {
        feedback.innerHTML = '<div class="jy-fb-correct"><span class="jy-fb-icon">&#10003;</span> 回答正确！</div>';
        if (result.explanation) {
          feedback.innerHTML += '<p class="jy-fb-explain">' + result.explanation + '</p>';
        }
      } else {
        feedback.innerHTML = '<div class="jy-fb-wrong"><span class="jy-fb-icon">&#10007;</span> 回答错误</div>';
        feedback.innerHTML += '<p class="jy-fb-explain">正确答案：<strong>' + result.correctAnswer + '</strong></p>';
        if (result.explanation) {
          feedback.innerHTML += '<p class="jy-fb-explain">' + result.explanation + '</p>';
        }
      }
      feedback.style.display = 'block';
      
      // Disable further changes
      var radios = document.querySelectorAll('input[name="jy-q' + index + '"]');
      for (var i = 0; i < radios.length; i++) {
        radios[i].disabled = true;
      }
      var btn = feedback.previousElementSibling;
      if (btn) btn.disabled = true;
      
      // Track progress
      this.checkAllComplete();
    },

    submitAll: function() {
      var courseId = document.body.getAttribute('data-course-id');
      var quizzes = window.JY_QUIZ_DATA;
      if (!quizzes) return;
      
      // Filter to this course only
      var filtered = quizzes;
      if (courseId) {
        filtered = quizzes.filter(function(q) { return q.id === courseId; });
      }

      var answers = [];
      for (var i = 0; i < filtered.length; i++) {
        var selected = document.querySelector('input[name="jy-q' + i + '"]:checked');
        answers.push(selected ? selected.value : null);
      }
      
      var result = window.JYQuiz.gradeAll(answers);
      
      var summary = document.getElementById('jy-quiz-summary');
      if (summary) {
        summary.innerHTML = '<h3>测验结果：' + result.score + '/' + result.total + ' (' + result.percentage + '%)</h3>';
        for (var j = 0; j < result.results.length; j++) {
          var r = result.results[j];
          var icon = r.correct ? '&#10003;' : '&#10007;';
          var cls = r.correct ? 'jy-fb-correct' : 'jy-fb-wrong';
          summary.innerHTML += '<div class="' + cls + '"><span class="jy-fb-icon">' + icon + '</span> ' + r.question + '</div>';
        }
        summary.style.display = 'block';
      }
      
      return result;
    },

    checkAllComplete: function() {
      var courseId = document.body.getAttribute('data-course-id');
      var quizzes = window.JY_QUIZ_DATA;
      if (!quizzes) return false;
      
      // Filter to this course only
      var filtered = quizzes;
      if (courseId) {
        filtered = quizzes.filter(function(q) { return q.id === courseId; });
      }

      var allAnswered = true;
      for (var i = 0; i < filtered.length; i++) {
        var selected = document.querySelector('input[name="jy-q' + i + '"]:checked');
        if (!selected) { allAnswered = false; break; }
      }
      
      if (allAnswered) {
        var courseId = document.body.getAttribute('data-course-id');
        if (courseId) {
          window.JYProgress.markComplete(courseId);
          this.showCompletionBadge();
        }
      }
      return allAnswered;
    },

    showCompletionBadge: function() {
      var badge = document.getElementById('jy-completion-badge');
      if (badge) {
        badge.style.display = 'block';
      }
    }
  };

  // ==================== PAYWALL UI ====================
  window.JYPaywall = {
    show: function(msg) {
      var existing = document.getElementById('jy-paywall-overlay');
      if (existing) return;
      
      var overlay = document.createElement('div');
      overlay.id = 'jy-paywall-overlay';
      overlay.innerHTML = 
        '<div class="jy-paywall">' +
        '<div class="jy-paywall-inner">' +
        '<h2>金庸武侠人物谱研究院</h2>' +
        '<p class="jy-paywall-desc">' + (msg || '此课程需要会员才能访问') + '</p>' +
        '<p class="jy-paywall-info">前20门主角课程免费学习 | 全库151门仅需 <strong>$' + COURSE_PRICE + '</strong></p>' +
        '<div class="jy-paywall-keys">' +
        '<input type="text" id="jy-key-input" placeholder="输入激活码" autocomplete="off">' +
        '<button onclick="JYPaywall.activate()">激活会员</button>' +
        '</div>' +
        '<p class="jy-paywall-hint">获取激活码请联系客服</p>' +
        '<a href="../../index.html" class="jy-paywall-back">返回首页浏览免费课程</a>' +
        '</div></div>';
      
      document.body.appendChild(overlay);
      
      // Enter key to submit
      var input = document.getElementById('jy-key-input');
      if (input) {
        input.addEventListener('keydown', function(e) {
          if (e.key === 'Enter') window.JYPaywall.activate();
        });
      }
    },

    activate: function() {
      var input = document.getElementById('jy-key-input');
      if (!input || !input.value.trim()) {
        this.showToast('请输入激活码');
        return;
      }
      
      var result = window.JYMembership.activate(input.value.trim());
      if (result.success) {
        var overlay = document.getElementById('jy-paywall-overlay');
        if (overlay) overlay.remove();
        this.showToast(result.message);
        setTimeout(function() { location.reload(); }, 800);
      } else {
        this.showToast(result.message);
      }
    },

    showToast: function(msg) {
      var existing = document.getElementById('jy-toast');
      if (existing) existing.remove();
      
      var toast = document.createElement('div');
      toast.id = 'jy-toast';
      toast.textContent = msg;
      document.body.appendChild(toast);
      
      setTimeout(function() {
        toast.classList.add('jy-toast-hide');
        setTimeout(function() { if (toast.parentNode) toast.remove(); }, 300);
      }, 2500);
    }
  };

  // ==================== INIT ====================
  document.addEventListener('DOMContentLoaded', function() {
    // Init quiz UI if present
    if (document.querySelector('.jy-quiz-container')) {
      window.JYQuizUI.init();
    }
    
    // Check paywall for course page
    var courseIndex = parseInt(document.body.getAttribute('data-course-index'));
    if (!isNaN(courseIndex) && !window.JYMembership.canAccess(courseIndex)) {
      window.JYPaywall.show();
    }
    
    // Update membership badge
    var badge = document.getElementById('jy-member-badge');
    if (badge) {
      var status = window.JYMembership.getStatus();
      badge.textContent = status.name;
      badge.className = 'jy-badge jy-badge-' + status.type;
    }

    // Completion check
    var courseId = document.body.getAttribute('data-course-id');
    if (courseId && window.JYProgress.isComplete(courseId)) {
      var badge = document.getElementById('jy-completion-badge');
      if (badge) badge.style.display = 'block';
    }
  });

})();
