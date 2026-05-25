
import os
import time
from playwright.sync_api import sync_playwright
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASSWORD = os.getenv("USER_PASSWORD")
RESUME_PATH = os.getenv("RESUME_PATH")
API_KEY = os.getenv("API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.3-70B-Versatile"

file_path = "resume.txt"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
except FileNotFoundError:
    print(f"Error: File '{file_path}' not found.")
except Exception as e:
    print(f"Error reading file: {e}")

def answer(question):
    print(question)

    history = []
    history.append({"role": "user", "content": file_content})
    history.append({"role": "user", "content": question})
    history.append({
        "role": "user",
        "content": "if there is question and options given answer from list without any changes return one answer dont do any changes in options"
    })

    response = client.chat.completions.create(
        model=MODEL,
        messages=history,
        temperature=0.7
    )

    reply = response.choices[0].message.content
    return reply

def get_real_question_text(page):
    time.sleep(2)

    msgs = page.locator("div.botMsg, div.chatbot_Message")

    for i in range(msgs.count() - 1, -1, -1):
        text = msgs.nth(i).inner_text().strip()

        if len(text) < 8:
            continue

        lower = text.lower()

        if any(x in lower for x in [
            "hi", "hello", "welcome", "thank", "please wait", "processing"
        ]):
            continue

        return text

    return "Unknown Question"

def answer_question(page):
    answered_questions = set()

    try:
        print("Checking for questions...")
        page.wait_for_timeout(1200)

        start_time = time.time()

        while True:

            if time.time() - start_time > 120:
                print("Skipping job — exceeded 2 minutes")
                return False

            if "saveApply" in page.url:
                print("Application auto-submitted")
                return True

            text_box = page.locator(
                "div[contenteditable='true'][id*='InputBox']:visible"
            )

            radio_container = page.locator(
                "div.singleselect-radiobutton-container:visible"
            )

            checkbox_container = page.locator(
                "div.multicheckboxes-container:visible"
            )

            save_btn = page.locator(
                "div.sendMsg:has-text('Save'), button:has-text('Save')"
            )

            proceed_btn = page.locator(
                "button:has-text('Next'), button:has-text('Continue'), div.sendMsg:has-text('Continue')"
            )

            if (
                text_box.count() == 0
                and radio_container.count() == 0
                and checkbox_container.count() == 0
            ):
                page.wait_for_timeout(800)
                continue

            question = get_real_question_text(page)
            print("Detected Question:", question)

            if question in answered_questions:
                print("Question already answered — skipping")

                if save_btn.count() > 0:
                    save_btn.first.click(force=True)
                elif proceed_btn.count() > 0:
                    proceed_btn.first.click(force=True)

                page.wait_for_timeout(1200)
                continue

            if radio_container.count() > 0:
                print("Radio Question")

                options = page.locator(
                    "div.singleselect-radiobutton-container label"
                )

                if options.count() > 0:
                    options.first.evaluate("el => el.click()")
                    print("Radio selected")

                answered_questions.add(question)

                if save_btn.count() > 0:
                    save_btn.first.click(force=True)

                page.wait_for_timeout(1200)
                continue

            if checkbox_container.count() > 0:
                print("Checkbox Question detected")

                options = checkbox_container.locator(
                    "div[role='checkbox'], label"
                )

                if options.count() > 0:
                    options.first.scroll_into_view_if_needed()
                    options.first.click(force=True)
                    print("Checkbox selected")

                answered_questions.add(question)

                if save_btn.count() > 0:
                    save_btn.first.click(force=True)

                page.wait_for_timeout(1200)
                continue

            if text_box.count() > 0:
                print("Text Question")

                ans = answer(question).strip()
                print("Answer:", ans)

                input_box = text_box.first
                input_box.click(force=True)

                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                page.keyboard.type(ans, delay=40)
                page.keyboard.press("Enter")

                answered_questions.add(question)

                print("Text answered")
                page.wait_for_timeout(1500)
                continue

    except Exception as e:
        print("answer_question error:", e)
        return False

def update_resume():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = browser.new_page()

        page.goto("https://www.naukri.com/nlogin/login")

        page.fill("#usernameField", USER_EMAIL)
        page.fill("#passwordField", USER_PASSWORD)

        page.click("button[type='submit']")

        try:
            page.wait_for_selector("text=My Naukri", timeout=3000)
            print("Login success")
        except:
            print("Manual OTP/Captcha if required")
            time.sleep(5)

        page.goto("https://www.naukri.com/mnjuser/profile")

        try:
            page.wait_for_selector("#attachCV", timeout=8000)
            page.locator("#attachCV").set_input_files(RESUME_PATH)
            print("Resume uploaded")
        except:
            print("Resume upload skipped")

        while True:
            page.goto("https://www.naukri.com/mnjuser/recommendedjobs")
            time.sleep(1)

            jobs = page.locator("div.saveJobContainer.tuple-check-box")
            count = jobs.count()

            print(f"Found {count} jobs")

            if count == 0:
                time.sleep(2)
                continue

            for i in range(count):
                page.goto("https://www.naukri.com/mnjuser/recommendedjobs")
                time.sleep(1)

                jobs = page.locator("div.saveJobContainer.tuple-check-box")

                if i >= jobs.count():
                    continue

                try:
                    jobs.nth(i).click()
                    print(f"Job {i+1} selected")
                except:
                    continue

                time.sleep(0.6)

                try:
                    page.locator("button:has-text('Apply')").first.click()
                    print("Apply clicked")
                except:
                    continue

                answer_question(page)
                time.sleep(2)

            print("Looping again...")

if __name__ == "__main__":
    update_resume()
