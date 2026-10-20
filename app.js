const startScreen = document.getElementById("start-screen");
const quizScreen = document.getElementById("quiz-screen");
const finishScreen = document.getElementById("finish-screen");
const startButton = document.getElementById("start-btn");
const nextButton = document.getElementById("next-btn");
const restartButton = document.getElementById("restart-btn");
const nameInput = document.getElementById("player-name");
const startError = document.getElementById("start-error");
const questionText = document.getElementById("question-text");
const optionsBox = document.getElementById("options");
const feedback = document.getElementById("feedback");
const questionCount = document.getElementById("question-count");
const progressLabel = document.getElementById("progress-label");
const scoreLabel = document.getElementById("score-label");
const progressBar = document.getElementById("progress-bar");
const finalScore = document.getElementById("final-score");
const finishMessage = document.getElementById("finish-message");
const finishTitle = document.getElementById("finish-title");
const leaderboardBox = document.getElementById("leaderboard");

let questions = [];
let currentIndex = 0;
let score = 0;
let playerName = "";
let waitingForNext = false;
const letters = ["الف", "ب", "ج", "د"];

function showScreen(screenToShow) {
  [startScreen, quizScreen, finishScreen].forEach(screen => screen.classList.add("hidden"));
  screenToShow.classList.remove("hidden");
}

async function getLeaderboard() {
  try {
    const response = await fetch("/api/leaderboard");
    const rows = await response.json();
    leaderboardBox.replaceChildren();

    if (rows.length === 0) {
      const empty = document.createElement("p");
      empty.className = "muted";
      empty.textContent = "هنوز امتیازی ثبت نشده؛ اولین قهرمان تو باش!";
      leaderboardBox.appendChild(empty);
      return;
    }

    rows.forEach((row, index) => {
      const item = document.createElement("div");
      item.className = "leader-row";
      const rank = document.createElement("span");
      rank.className = "rank" + (index === 0 ? " first" : "");
      rank.textContent = String(index + 1).padStart(2, "0");
      const name = document.createElement("span");
      name.className = "player-name";
      name.textContent = row.name;
      const points = document.createElement("span");
      points.className = "player-score";
      points.textContent = `${row.score} / ${row.total}`;
      item.append(rank, name, points);
      leaderboardBox.appendChild(item);
    });
  } catch {
    leaderboardBox.textContent = "جدول امتیازها فعلاً بارگذاری نشد.";
  }
}

function renderQuestion() {
  const question = questions[currentIndex];
  waitingForNext = false;
  questionCount.textContent = `مرحله ${currentIndex + 1} از ${questions.length}`;
  progressLabel.textContent = `سؤال ${currentIndex + 1} از ${questions.length}`;
  scoreLabel.textContent = `امتیاز: ${score}`;
  progressBar.style.width = `${(currentIndex / questions.length) * 100}%`;
  questionText.textContent = question.question;
  optionsBox.replaceChildren();
  feedback.className = "feedback hidden";
  feedback.textContent = "";
  nextButton.classList.add("hidden");

  question.options.forEach((option, index) => {
    const button = document.createElement("button");
    button.className = "option-btn";
    button.type = "button";
    const letter = document.createElement("span");
    letter.className = "option-letter";
    letter.textContent = letters[index];
    const label = document.createElement("span");
    label.textContent = option;
    button.append(letter, label);
    button.addEventListener("click", () => submitAnswer(question.id, index, button));
    optionsBox.appendChild(button);
  });
}

async function startQuiz() {
  playerName = nameInput.value.trim();
  if (!playerName) {
    startError.textContent = "اول اسم بازیکن رو وارد کن.";
    nameInput.focus();
    return;
  }

  startError.textContent = "";
  startButton.disabled = true;
  try {
    const response = await fetch("/api/start");
    const data = await response.json();
    questions = data.questions;
    currentIndex = 0;
    score = 0;
    showScreen(quizScreen);
    renderQuestion();
  } catch {
    startError.textContent = "ارتباط با سرور برقرار نشد. مطمئن شو برنامه در حال اجراست.";
  } finally {
    startButton.disabled = false;
  }
}

async function submitAnswer(questionId, choice, selectedButton) {
  if (waitingForNext) return;
  waitingForNext = true;
  const buttons = [...optionsBox.querySelectorAll("button")];
  buttons.forEach(button => button.disabled = true);

  try {
    const response = await fetch("/api/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question_id: questionId, choice })
    });
    const result = await response.json();

    if (!response.ok) throw new Error(result.error || "پاسخ ثبت نشد.");
    if (result.correct) {
      score = result.score;
      selectedButton.classList.add("correct");
      feedback.className = "feedback good";
      feedback.textContent = `آفرین! پاسخ درسته. ${result.explanation}`;
    } else {
      selectedButton.classList.add("wrong");
      feedback.className = "feedback bad";
      feedback.textContent = `این بار نه! ${result.explanation}`;
    }
    scoreLabel.textContent = `امتیاز: ${score}`;
    feedback.classList.remove("hidden");
    nextButton.textContent = currentIndex === questions.length - 1 ? "دیدن نتیجه ←" : "سؤال بعدی ←";
    nextButton.classList.remove("hidden");
  } catch (error) {
    waitingForNext = false;
    buttons.forEach(button => button.disabled = false);
    feedback.className = "feedback bad";
    feedback.textContent = error.message;
    feedback.classList.remove("hidden");
  }
}

async function finishQuiz() {
  questionCount.textContent = "پایان مأموریت";
  try {
    const response = await fetch("/api/finish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: playerName })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "ذخیره‌ی امتیاز انجام نشد.");

    finalScore.textContent = `${result.score}`;
    finishTitle.textContent = result.score === result.total ? "فوق‌العاده بود!" : "مأموریت انجام شد!";
    finishMessage.textContent = `${playerName}، از ${result.total} سؤال به ${result.score} سؤال درست جواب دادی.`;
    progressBar.style.width = "100%";
    showScreen(finishScreen);
    await getLeaderboard();
  } catch (error) {
    alert(error.message);
  }
}

startButton.addEventListener("click", startQuiz);
nameInput.addEventListener("keydown", event => {
  if (event.key === "Enter") startQuiz();
});

nextButton.addEventListener("click", () => {
  if (currentIndex < questions.length - 1) {
    currentIndex += 1;
    renderQuestion();
  } else {
    finishQuiz();
  }
});

restartButton.addEventListener("click", () => {
  showScreen(startScreen);
  questionCount.textContent = "آماده‌ای؟";
  nameInput.value = playerName;
  getLeaderboard();
});

getLeaderboard();
