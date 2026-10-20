
from flask import Flask, render_template, request, jsonify, session
import sqlite3
import json
import random
import uuid
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-demo-key-before-publishing"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "codequest.db"
QUESTIONS_PER_GAME = 10

# هر سؤال: متن، گزینه‌ها، شماره پاسخ درست، توضیح، سطح دشواری
RAW_QUESTIONS = [
    ("HTML معمولاً چه کاری انجام می‌دهد؟", ["طراحی ظاهر", "ساختار صفحه", "ذخیره اطلاعات", "اجرای سرور"], 1, "HTML ساختار و محتوای صفحه را مشخص می‌کند.", "آسان"),
    ("CSS برای چیست؟", ["استایل و ظاهر", "مدیریت پایگاه داده", "ساخت سرور", "نوشتن کوئری SQL"], 0, "CSS رنگ، فاصله‌بندی و ظاهر صفحه را تنظیم می‌کند.", "آسان"),
    ("JavaScript در صفحه وب چه کاربردی دارد؟", ["فقط ذخیره فایل", "تعامل و رفتار پویا", "جایگزینی HTML", "مدیریت سیستم‌عامل"], 1, "JavaScript به صفحه رفتار و تعامل اضافه می‌کند.", "آسان"),
    ("کدام مورد یک زبان برنامه‌نویسی است؟", ["HTML", "CSS", "Python", "HTTP"], 2, "Python یک زبان برنامه‌نویسی عمومی است.", "آسان"),
    ("Frontend به کدام بخش اشاره دارد؟", ["بخش قابل مشاهده و تعامل کاربر", "فقط پایگاه داده", "فقط سرور", "کابل شبکه"], 0, "Frontend بخشی است که کاربر مستقیماً با آن تعامل دارد.", "آسان"),
    ("Backend معمولاً چه کاری انجام می‌دهد؟", ["پردازش درخواست‌ها", "تنظیم رنگ متن", "طراحی آیکون", "انتخاب فونت مرورگر"], 0, "Backend منطق برنامه و درخواست‌های کاربر را پردازش می‌کند.", "آسان"),
    ("Flask چیست؟", ["زبان برنامه‌نویسی", "فریم‌ورک وب پایتون", "مرورگر", "پایگاه داده"], 1, "Flask فریم‌ورکی سبک برای ساخت برنامه‌های وب با Python است.", "آسان"),
    ("SQLite چیست؟", ["زبان طراحی صفحه", "کتابخانه CSS", "پایگاه داده", "مرورگر"], 2, "SQLite یک پایگاه داده سبک است که معمولاً در یک فایل ذخیره می‌شود.", "آسان"),
    ("کدام تگ HTML برای عنوان سطح اول است؟", ["<p>", "<h1>", "<img>", "<br>"], 1, "تگ h1 برای عنوان اصلی سطح اول استفاده می‌شود.", "آسان"),
    ("کدام تگ برای پیوند استفاده می‌شود؟", ["<a>", "<div>", "<table>", "<title>"], 0, "تگ a برای ساخت لینک به کار می‌رود.", "آسان"),
    ("کدام ویژگی تصویر را به تگ img معرفی می‌کند؟", ["href", "src", "class", "alt فقط"], 1, "ویژگی src مسیر تصویر را مشخص می‌کند.", "آسان"),
    ("در CSS، کدام ویژگی رنگ متن را تعیین می‌کند؟", ["font-size", "margin", "color", "padding"], 2, "ویژگی color رنگ متن را تعیین می‌کند.", "آسان"),
    ("در CSS، margin چه چیزی را تنظیم می‌کند؟", ["فاصله بیرونی", "رنگ متن", "نوع داده", "مسیر فایل"], 0, "margin فضای بیرون مرز عنصر را تنظیم می‌کند.", "آسان"),
    ("کدام دستور در Python متن را چاپ می‌کند؟", ["echo()", "print()", "show()", "write_screen()"], 1, "تابع print برای نمایش خروجی استفاده می‌شود.", "آسان"),
    ("کدام علامت برای کامنت تک‌خطی Python است؟", ["//", "<!--", "#", "/*"], 2, "در Python از # برای کامنت تک‌خطی استفاده می‌شود.", "آسان"),
    ("نوع داده True و False در Python چیست؟", ["str", "bool", "list", "float"], 1, "bool نوع داده منطقی با مقدارهای True و False است.", "آسان"),
    ("کدام ساختار برای تکرار در Python استفاده می‌شود؟", ["for", "def فقط", "import", "return"], 0, "حلقه for برای پیمایش و تکرار استفاده می‌شود.", "آسان"),
    ("تابع در Python با کدام کلمه تعریف می‌شود؟", ["func", "function", "def", "make"], 2, "تعریف تابع در Python با def آغاز می‌شود.", "آسان"),
    ("کدام ساختار در Python برای نگهداری چند مقدار مرتب مناسب است؟", ["list", "int", "bool", "None"], 0, "لیست می‌تواند چند مقدار را به ترتیب نگهداری کند.", "آسان"),
    ("درخواست HTTP از مرورگر به سرور برای دریافت داده معمولاً چیست؟", ["GET", "PAINT", "STYLE", "PRINT"], 0, "GET معمولاً برای دریافت داده از سرور استفاده می‌شود.", "آسان"),
    ("کدام روش HTTP معمولاً برای ارسال داده جهت ایجاد یا پردازش استفاده می‌شود؟", ["GET فقط", "POST", "COLOR", "HTML"], 1, "POST معمولاً داده را در بدنه درخواست می‌فرستد.", "متوسط"),
    ("در Flask، دکوراتور @app.route چه کاری دارد؟", ["تعریف مسیر URL", "ساخت تصویر", "تنظیم فونت", "حذف پایگاه داده"], 0, "این دکوراتور یک مسیر را به تابع مرتبط می‌کند.", "متوسط"),
    ("در Flask، render_template معمولاً چه می‌کند؟", ["نمایش قالب HTML", "اجرای کوئری CSS", "نصب Python", "ساخت مرورگر"], 0, "render_template رندر کردن قالب‌های پوشه templates را انجام می‌دهد.", "متوسط"),
    ("کدام تابع Flask داده JSON را معمولاً به پاسخ تبدیل می‌کند؟", ["jsonify", "print", "input", "range"], 0, "jsonify پاسخ JSON می‌سازد.", "متوسط"),
    ("در JavaScript، const چه معنایی دارد؟", ["تعریف متغیر با انتساب مجدد ممنوع", "ساخت تابع پایتون", "ساخت جدول SQL", "تعریف تگ HTML"], 0, "const اجازه انتساب دوباره به همان متغیر را نمی‌دهد.", "متوسط"),
    ("در JavaScript، === چه چیزی را بررسی می‌کند؟", ["برابری مقدار و نوع", "فقط بزرگ‌تر بودن", "تقسیم", "تعریف آرایه"], 0, "=== برابری سخت‌گیرانه مقدار و نوع را بررسی می‌کند.", "متوسط"),
    ("کدام دستور JavaScript برای درخواست شبکه‌ای مناسب است؟", ["fetch()", "print()", "SELECT()", "margin()"], 0, "fetch برای ارسال درخواست و دریافت پاسخ شبکه استفاده می‌شود.", "متوسط"),
    ("DOM در توسعه وب به چه اشاره دارد؟", ["مدل شیء سند صفحه", "پایگاه داده سرور", "نوعی زبان پایتون", "فایل CSS"], 0, "DOM ساختار صفحه را به صورت مجموعه‌ای از اشیا در دسترس JavaScript قرار می‌دهد.", "متوسط"),
    ("API معمولاً چه نقشی دارد؟", ["راه ارتباط نرم‌افزارها", "رنگ‌آمیزی متن", "فشرده‌سازی تصویر فقط", "تعریف تگ عنوان"], 0, "API راهی مشخص برای ارتباط بین بخش‌های نرم‌افزاری فراهم می‌کند.", "متوسط"),
    ("JSON بیشتر برای چه کاری استفاده می‌شود؟", ["نمایش و تبادل داده", "تنظیم فاصله CSS", "اجرای حلقه", "ساخت فونت"], 0, "JSON قالبی متنی برای تبادل داده ساخت‌یافته است.", "متوسط"),
    ("در SQL، SELECT برای چیست؟", ["خواندن داده", "تغییر رنگ", "ساخت صفحه", "اجرای حلقه Python"], 0, "SELECT برای دریافت داده از جدول استفاده می‌شود.", "متوسط"),
    ("در SQL، INSERT چه می‌کند؟", ["افزودن رکورد", "حذف مرورگر", "تعریف کلاس CSS", "نمایش تصویر"], 0, "INSERT رکورد جدیدی به جدول اضافه می‌کند.", "متوسط"),
    ("کلید اصلی (Primary Key) چه کاربردی دارد؟", ["شناسه یکتای هر رکورد", "تنظیم رنگ جدول", "افزایش سرعت اینترنت همیشه", "ذخیره فونت"], 0, "کلید اصلی هر رکورد را به شکل یکتا مشخص می‌کند.", "متوسط"),
    ("چرا در SQL از پارامترهای جایگزین به جای چسباندن متن ورودی استفاده می‌کنیم؟", ["کاهش خطر SQL Injection", "زیباتر شدن CSS", "اجرای HTML", "کم شدن اندازه نمایشگر"], 0, "پارامترگذاری کمک می‌کند ورودی کاربر به عنوان داده تفسیر شود، نه بخشی از دستور SQL.", "سخت"),
    ("چرا نباید debug=True را در سرور عمومی فعال گذاشت؟", ["ممکن است اطلاعات حساس و ابزار دیباگ را افشا کند", "ظاهر صفحه تغییر می‌کند", "SQLite حذف می‌شود", "HTML دیگر کار نمی‌کند"], 0, "حالت دیباگ برای توسعه محلی است و نباید در محیط تولید فعال باشد.", "متوسط"),
    ("اگر تابع Python به return نرسد، معمولاً چه برمی‌گرداند؟", ["0", "False", "None", "رشته خالی"], 2, "تابعی که مقدار بازگشتی مشخصی ندارد، معمولاً None برمی‌گرداند.", "متوسط"),
    ("خروجی print(2 + 3 * 4) چیست؟", ["20", "14", "24", "9"], 1, "ضرب پیش از جمع انجام می‌شود: 2 + 12 = 14.", "متوسط"),
    ("خروجی len('code') چیست؟", ["3", "4", "5", "خطا"], 1, "رشته code چهار نویسه دارد.", "متوسط"),
    ("در Python، کدام گزینه برای مدیریت خطا مناسب است؟", ["try/except", "if/style", "HTML/CSS", "SELECT/PAINT"], 0, "try/except امکان مدیریت استثناها را فراهم می‌کند.", "متوسط"),
    ("در یک درخواست وب، کد وضعیت 404 معمولاً به چه معناست؟", ["موفق", "یافت نشدن منبع", "خطای داخلی سرور", "هدایت دائمی"], 1, "کد 404 یعنی منبع درخواست‌شده پیدا نشده است.", "متوسط"),
    ("کد وضعیت HTTP در بازه 500 معمولاً نشان‌دهنده چیست؟", ["مشکل سمت سرور", "موفقیت", "خطای تایپی کاربر فقط", "فایل CSS"], 0, "کدهای 5xx معمولاً به خطاهای سمت سرور اشاره دارند.", "متوسط"),
    ("چرا رمز عبور نباید به صورت متن ساده ذخیره شود؟", ["افشای پایگاه داده رمزها را آشکار می‌کند", "سرعت CSS کم می‌شود", "HTML خراب می‌شود", "URL کوتاه می‌شود"], 0, "سامانه‌های واقعی باید از روش‌های مناسب هش رمز عبور استفاده کنند.", "سخت"),
    ("اصل اعتبارسنجی ورودی کاربر چرا مهم است؟", ["کاهش خطا و سوءاستفاده", "زیاد کردن اندازه فونت", "تغییر رنگ پس‌زمینه", "ساخت خودکار تصویر"], 0, "اعتبارسنجی ورودی به جلوگیری از داده نامعتبر و برخی حمله‌ها کمک می‌کند.", "متوسط"),
    ("در طراحی واکنش‌گرا (Responsive)، هدف چیست؟", ["سازگاری چیدمان با اندازه صفحه", "افزایش تعداد جدول‌ها", "حذف JavaScript", "ذخیره رمزها"], 0, "طراحی واکنش‌گرا صفحه را برای نمایشگرهای مختلف سازگار می‌کند.", "آسان"),
    ("Flexbox در CSS بیشتر برای چیست؟", ["چیدمان و هم‌ترازی عناصر", "ذخیره رکوردها", "ارسال درخواست HTTP", "تعریف تابع Python"], 0, "Flexbox ابزار چیدمان عناصر در یک بُعد است.", "متوسط"),
    ("در Python، کدام ساختار برای جفت کلید و مقدار مناسب است؟", ["dict", "tuple فقط", "bool", "float"], 0, "دیکشنری داده‌ها را به صورت کلید و مقدار نگه می‌دارد.", "آسان"),
    ("چرا تابع random.sample در انتخاب سؤال‌ها مناسب است؟", ["انتخاب چند عضو بدون تکرار", "مرتب‌سازی بر اساس نام", "ذخیره رکورد در SQL", "تبدیل CSS به HTML"], 0, "random.sample تعدادی عضو یکتا از یک مجموعه انتخاب می‌کند.", "متوسط"),
    ("چرا امتیاز نهایی باید در سمت سرور محاسبه یا تأیید شود؟", ["برای دشوارتر کردن دست‌کاری نتیجه از سمت مرورگر", "برای تغییر فونت", "برای کم کردن تعداد سؤال‌ها", "برای نمایش عکس"], 0, "داده‌های سمت مرورگر قابل دست‌کاری‌اند؛ سرور باید پاسخ و امتیاز را بررسی کند.", "سخت"),
    ("در پروژه چندبازیکنه، شناسه مستقل بازی چه کمکی می‌کند؟", ["جدا نگه‌داشتن وضعیت هر دور بازی", "تغییر خودکار زبان برنامه", "حذف نیاز به پاسخ‌سنجی", "جلوگیری از همه خطاها"], 0, "شناسه مستقل کمک می‌کند وضعیت و پاسخ‌های هر بازی از بازی دیگر جدا بماند.", "سخت"),
    ("چرا در کوئری SQL بهتر است از پارامترها استفاده کنیم؟", ["برای جدا نگه‌داشتن داده از دستور", "برای افزودن رنگ", "برای ساخت انیمیشن", "برای تغییر نوع فونت"], 0, "پارامترگذاری هم ایمن‌تر است و هم از خطاهای ناشی از ورودی جلوگیری می‌کند.", "سخت"),
]

QUESTIONS = [
    {
        "id": index + 1,
        "question": item[0],
        "options": item[1],
        "answer": item[2],
        "explanation": item[3],
        "difficulty": item[4],
    }
    for index, item in enumerate(RAW_QUESTIONS)
]


def get_db():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS games (
                game_id TEXT PRIMARY KEY,
                question_ids TEXT NOT NULL,
                score INTEGER NOT NULL DEFAULT 0,
                answered_ids TEXT NOT NULL DEFAULT '[]',
                player_name TEXT,
                finished INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def error(message, status=400):
    return jsonify({"error": message}), status


def find_game(game_id):
    if not game_id:
        return None
    with get_db() as connection:
        return connection.execute(
            "SELECT * FROM games WHERE game_id = ?", (game_id,)
        ).fetchone()


@app.route("/")
def home():
    return render_template("index.html")



def start_quiz():
    difficulty = request.args.get("difficulty", "medium")
allowed_difficulties = {"easy", "medium", "hard"}

if difficulty not in allowed_difficulties:
    difficulty = "medium"

difficulty_names = {
    "easy": "آسان",
    "medium": "متوسط",
    "hard": "سخت"
}

available = [
    q for q in QUESTIONS
    if q["difficulty"] == difficulty_names.get(difficulty, "متوسط")
]

if len(available) < QUESTIONS_PER_GAME:
    available = QUESTIONS

selected = random.sample(available, QUESTIONS_PER_GAME)
    game_id = str(uuid.uuid4())
    question_ids = [q["id"] for q in selected]

    with get_db() as connection:
        connection.execute(
            """INSERT INTO games (game_id, question_ids)
               VALUES (?, ?)""",
            (game_id, json.dumps(question_ids)),
        )

    # سازگاری موقت با نسخه فعلی JavaScript
    session["current_game_id"] = game_id

    return jsonify({
        "game_id": game_id,
        "questions": [
            {
                "id": q["id"],
                "question": q["question"],
                "options": q["options"],
                "difficulty": q["difficulty"],
            }@app.get("/api/start")
            for q in selected
        ],
        "total": QUESTIONS_PER_GAME,
        "question_bank_size": len(QUESTIONS),
    })


@app.post("/api/answer")
def answer_question():
    data = request.get_json(silent=True) or {}
    game_id = data.get("game_id") or session.get("current_game_id")
    question_id = data.get("question_id")
    choice = data.get("choice")

    if type(question_id) is not int or type(choice) is not int:
        return error("پاسخ ارسالی معتبر نیست.")

    game = find_game(game_id)
    if game is None:
        return error("بازی پیدا نشد؛ لطفاً بازی را دوباره شروع کن.", 404)
    if game["finished"]:
        return error("این بازی قبلاً تمام شده است.")

    question_ids = json.loads(game["question_ids"])
    if question_id not in question_ids:
        return error("این سؤال متعلق به این بازی نیست.")

    answered = json.loads(game["answered_ids"])
    if question_id in answered:
        return error("به این سؤال قبلاً پاسخ داده‌ای.")

    question = next(q for q in QUESTIONS if q["id"] == question_id)
    if choice < 0 or choice >= len(question["options"]):
        return error("گزینه انتخاب‌شده معتبر نیست.")

    correct = choice == question["answer"]
    score = game["score"] + int(correct)
    answered.append(question_id)

    with get_db() as connection:
        connection.execute(
            """UPDATE games
               SET score = ?, answered_ids = ?
               WHERE game_id = ? AND finished = 0""",
            (score, json.dumps(answered), game_id),
        )

    return jsonify({
        "correct": correct,
        "explanation": question["explanation"],
        "score": score,
        "difficulty": question["difficulty"],
    })


@app.post("/api/finish")
def finish_quiz():
    data = request.get_json(silent=True) or {}
    game_id = data.get("game_id") or session.get("current_game_id")
    name = str(data.get("name", "")).strip()
    name = "".join(ch for ch in name if ch.isprintable())[:30].strip()

    if not name:
        return error("لطفاً نام بازیکن را وارد کن.")

    game = find_game(game_id)
    if game is None:
        return error("بازی پیدا نشد؛ لطفاً یک دور جدید شروع کن.", 404)
    if game["finished"]:
        return error("نتیجه این بازی قبلاً ثبت شده است.")

    answered = json.loads(game["answered_ids"])
    total_questions = len(json.loads(game["question_ids"]))

    if len(answered) < total_questions:
        return error("هنوز به همه سؤال‌ها پاسخ داده نشده است.")

    with get_db() as connection:
        connection.execute(
            """INSERT INTO scores (player_name, score, total)
               VALUES (?, ?, ?)""",
            (name, game["score"], total_questions),
        )
        connection.execute(
            """UPDATE games
               SET player_name = ?, finished = 1
               WHERE game_id = ? AND finished = 0""",
            (name, game_id),
        )

    if session.get("current_game_id") == game_id:
        session.pop("current_game_id", None)

    return jsonify({
        "saved": True,
        "score": game["score"],
        "total": total_questions,
    })


@app.get("/api/leaderboard")
def leaderboard():
    with get_db() as connection:
        rows = connection.execute("""
            SELECT player_name, score, total
            FROM scores
            ORDER BY score DESC, id ASC
            LIMIT 10
        """).fetchall()

    return jsonify([
        {
            "name": row["player_name"],
            "score": row["score"],
            "total": row["total"],
        }
        for row in rows
    ])


init_db()

if __name__ == "__main__":
    app.run(debug=True)
