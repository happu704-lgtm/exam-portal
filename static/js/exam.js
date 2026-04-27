// Exam Interface JavaScript - Timer, Navigation, Answer Management

let currentQuestion = 0;
let totalQuestions = 0;
let answers = {};
let flagged = new Set();
let timerInterval = null;
let remainingSeconds = 0;
let examId = 0;

function initExam(examIdParam, durationMinutes, questionCount) {
    examId = examIdParam;
    totalQuestions = questionCount;
    remainingSeconds = durationMinutes * 60;

    // Restore any saved state
    const saved = sessionStorage.getItem(`exam_${examId}_answers`);
    if (saved) {
        try {
            answers = JSON.parse(saved);
            // Restore visual state
            Object.keys(answers).forEach(qid => {
                const option = answers[qid];
                const el = document.querySelector(`[data-question="${qid}"] .option-item[data-option="${option}"]`);
                if (el) el.classList.add('selected');
            });
        } catch (e) { }
    }

    const savedTime = sessionStorage.getItem(`exam_${examId}_time`);
    if (savedTime) {
        const elapsed = Math.floor((Date.now() - parseInt(savedTime)) / 1000);
        remainingSeconds = Math.max(0, remainingSeconds - elapsed);
    } else {
        sessionStorage.setItem(`exam_${examId}_time`, Date.now().toString());
    }

    startTimer();
    showQuestion(0);
    updateNavigation();
}

function startTimer() {
    updateTimerDisplay();
    timerInterval = setInterval(() => {
        remainingSeconds--;
        updateTimerDisplay();

        if (remainingSeconds <= 0) {
            clearInterval(timerInterval);
            autoSubmit();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const hours = Math.floor(remainingSeconds / 3600);
    const minutes = Math.floor((remainingSeconds % 3600) / 60);
    const seconds = remainingSeconds % 60;

    const display = document.getElementById('timerDisplay');
    if (!display) return;

    if (hours > 0) {
        display.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    } else {
        display.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    // Warning at 5 minutes
    const timer = document.getElementById('examTimer');
    if (remainingSeconds <= 300 && timer) {
        timer.classList.add('danger');
    }
}

function showQuestion(index) {
    if (index < 0 || index >= totalQuestions) return;

    // Hide all questions
    document.querySelectorAll('.question-card').forEach((card, i) => {
        card.style.display = i === index ? 'block' : 'none';
    });

    currentQuestion = index;
    updateNavigation();

    // Update prev/next button states
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    if (prevBtn) prevBtn.disabled = index === 0;
    if (nextBtn) nextBtn.textContent = index === totalQuestions - 1 ? 'Review' : 'Next →';
}

function selectOption(questionId, option, element) {
    // Remove previous selection
    const container = element.closest('.options-list');
    container.querySelectorAll('.option-item').forEach(item => {
        item.classList.remove('selected');
    });

    // Select this option
    element.classList.add('selected');
    answers[questionId] = option;

    // Save to session
    sessionStorage.setItem(`exam_${examId}_answers`, JSON.stringify(answers));
    updateNavigation();
}

function updateNavigation() {
    const buttons = document.querySelectorAll('.nav-btn');
    buttons.forEach((btn, index) => {
        btn.classList.remove('current', 'answered', 'flagged');
        const qid = btn.dataset.questionId;

        if (index === currentQuestion) {
            btn.classList.add('current');
        }
        if (answers[qid]) {
            btn.classList.add('answered');
        }
        if (flagged.has(qid)) {
            btn.classList.add('flagged');
        }
    });

    // Update progress
    const answered = Object.keys(answers).length;
    const progressText = document.getElementById('progressText');
    if (progressText) {
        progressText.textContent = `${answered} of ${totalQuestions} answered`;
    }
}

function goToQuestion(index) {
    showQuestion(index);
}

function nextQuestion() {
    if (currentQuestion < totalQuestions - 1) {
        showQuestion(currentQuestion + 1);
    }
}

function prevQuestion() {
    if (currentQuestion > 0) {
        showQuestion(currentQuestion - 1);
    }
}

function toggleFlag() {
    const qCards = document.querySelectorAll('.question-card');
    const currentCard = qCards[currentQuestion];
    if (!currentCard) return;

    const qid = currentCard.dataset.questionId;
    if (flagged.has(qid)) {
        flagged.delete(qid);
    } else {
        flagged.add(qid);
    }
    updateNavigation();
}

function confirmSubmit() {
    const answered = Object.keys(answers).length;
    const unanswered = totalQuestions - answered;

    const modal = document.getElementById('submitModal');
    const info = document.getElementById('submitInfo');
    if (info) {
        info.innerHTML = `You have answered <strong>${answered}</strong> out of <strong>${totalQuestions}</strong> questions.`;
        if (unanswered > 0) {
            info.innerHTML += `<br><span style="color: var(--danger);">${unanswered} question(s) remain unanswered.</span>`;
        }
    }
    showModal('submitModal');
}

function submitExam() {
    hideModal('submitModal');
    clearInterval(timerInterval);

    // Remove beforeunload listener
    window.removeEventListener('beforeunload', () => { });

    // Show loading state
    const submitBtn = document.querySelector('.submit-exam-btn');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
    }

    fetch(`/api/student/exam/${examId}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers: answers })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Clear session data
                sessionStorage.removeItem(`exam_${examId}_answers`);
                sessionStorage.removeItem(`exam_${examId}_time`);
                window.onbeforeunload = null;
                window.location.href = `/api/student/result/${data.result_id}`;
            } else {
                alert('Error submitting exam. Please try again.');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Exam';
                }
            }
        })
        .catch(err => {
            console.error('Submit error:', err);
            alert('Error submitting exam. Please try again.');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Exam';
            }
        });
}

function autoSubmit() {
    alert('Time is up! Your exam will be submitted automatically.');
    submitExam();
}
