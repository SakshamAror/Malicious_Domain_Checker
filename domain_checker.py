from playwright.sync_api import sync_playwright
import sys
import os
import time
import random

#######################    SETTINGS    ############################

# If chromium path doesn't resolve to an executable, it will automatically run 
# playwright's browser binaries
chromium_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

subject_list = ["amazon.com", "yahoo.com", "google.com"]

safe_texts = ["No security vendors flagged this", "No security vendor flagged this"]
safe_rating = "0"
sus_text = "------------------ Suspicious Subject: "
maybesus_text = "-------- Perhaps Suspicious Subject: "
notsus_text = "--- Safe Subject: "

# in seconds
pause_time = 5
timeout = 10

no_parallel = 5

headless_mode = False
# For window sizing in headful mode
default_settings = True # Instead just run with default viewport
screen_height = 982
screen_width = 1512
# If any of the positions are a negative number, load in fullscreen
exec_settings = [screen_height, screen_width, 0, 0]
exec_height, exec_width, exec_xpos, exec_ypos = exec_settings

####################################################################

def cla(): # command line arguments
    if len(sys.argv) < 1:
        return
    
    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print("File not found.")
        print("Usage: python domain_checker.py (filepath to a subject_list.txt with one subject per line)")
        quit()
    if not file_path.lower().endswith(".txt"):
        print(f"Error: '{file_path}' is not a .txt file")
        print("Usage: python domain_checker.py (filepath to a subject_list.txt with one subject per line)")
        quit()

    global subject_list
    subject_list = []
    subjects = open(file_path, "r")
    for line in subjects:
        line = line.strip()
        if line and line not in subject_list:
            subject_list.append(line)

    print("Initializing with these subjects:")
    print(subject_list)
    subjects.close()

def main():
    start_time = time.perf_counter()
    log = open("logs.txt", "w")

    with sync_playwright() as p:

        suspicious_list = []

        fullscreen = False
        for setting in exec_settings:
            if setting < 0:
                fullscreen = True

        launch_options = {
            "headless": headless_mode,
        }

        if os.path.isfile(chromium_path):
            launch_options["executable_path"] = chromium_path

        if default_settings:
            print("Launching with default viewport ...")
        elif fullscreen:
            print("Launching in fullscreen ...")
            launch_options["args"] = [
                "--start-fullscreen",
                f"--window-position={0},{0}"]
        else:
            print("Launching ...")
            launch_options["args"] = [
                    f"--window-size={exec_width},{exec_height}",
                    f"--window-position={exec_xpos},{exec_ypos}"]

        try:
            browser = p.chromium.launch(**launch_options)
        except Exception as e:
            print("Launching with playwright installed chromium browser")
            launch_options.pop("executable_path", None)
            browser = p.chromium.launch(**launch_options)

        if not default_settings:
            context = browser.new_context(
                viewport={"width": screen_width, "height": screen_height}
            )
        else :
            context = browser.new_context()

        global no_parallel
        if (no_parallel < 1):
            no_parallel = 1
        pages = {}
        open_pages = [None] * no_parallel
        for i in range(no_parallel):
            open_pages[i] = context.new_page()
        for i in range(len(subject_list) // no_parallel + 1):
            bump = False

            j = 0
            for sub in subject_list[i*no_parallel:(i+1)*no_parallel]:
                global pause_time
                if (pause_time < 0.25):
                    pause_time = 0.25
                time.sleep(random.random()*(pause_time/2) + pause_time/2)
                page = open_pages[j]
                page.set_default_timeout(timeout*1000)
                page.goto("https://www.virustotal.com/gui/search?query=" + sub, wait_until="commit")
                pages[sub] = page
                j += 1

            for sub in subject_list[i*no_parallel:(i+1)*no_parallel]:
                # Wait for some time to ensure everything has been cleaned up properly

                eval_locator = pages[sub].locator("div > div.card-header.hstack.flex-wrap.justify-content-between.gap-2 "
                                                    "> div.hstack.gap-2.fw-bold[class*='text-']")
                rating_locator = pages[sub].locator("#positives")
                if bump and not eval_locator.is_visible() and not rating_locator.is_visible():
                    pages[sub].goto("https://www.virustotal.com/gui/search?query=" + sub)
                    eval_locator = pages[sub].locator("div > div.card-header.hstack.flex-wrap.justify-content-between.gap-2 "
                                                    "> div.hstack.gap-2.fw-bold[class*='text-']")
                    rating_locator = pages[sub].locator("#positives")

                loaded = False
                while not loaded:
                    try:
                        eval_locator = pages[sub].locator("div > div.card-header.hstack.flex-wrap.justify-content-between.gap-2 "
                                                    "> div.hstack.gap-2.fw-bold[class*='text-']")
                        rating_locator = pages[sub].locator("#positives")
                        eval_locator.wait_for(state="visible")
                        rating_locator.wait_for(state="visible")
                        loaded = True
                    except Exception as e:
                        pages[sub].bring_to_front()
                        bump = True
                        user_intervention = input(f"Task on subject {sub} has timed out, investigate highlighted tab and type " \
                                            "anything to continue/try again or q to exit: ")
                        if user_intervention == "q":
                            return
                        pages[sub].reload()
                
                text = eval_locator.text_content()
                text = text.strip()
                rating = rating_locator.text_content()
                rating = rating.strip()

                safeText = False
                for st in safe_texts:
                    if st.lower() in text.lower():
                        safeText = True

                if rating != safe_rating and not safeText:
                    print(sus_text + sub)
                    pages[sub].screenshot(path= os.path.join("screenshots", sub + ".png"))
                    log.write(sus_text + sub + "\n")
                    suspicious_list.append(sub)
                elif rating != safe_rating or not safeText:
                    print(maybesus_text + sub)
                    log.write(maybesus_text + sub + "\n")
                else:
                    print(notsus_text + sub)
                    log.write(notsus_text + sub + "\n")
            
                print(f"Evaluation: {text}")
                log.write(f"Evaluation: {text}\n")
                print(f"Rating: {rating}/91")
                log.write(f"Rating: {rating}/91\n")
                print()
                log.write('\n')

        context.close()
        browser.close()

    print()
    log.write("\n")
    print("(Screenshots saved in /screenshots)")
    print(f"Suspicious Subjects: {len(suspicious_list)}")
    log.write(f"Suspicious Subjects: {len(suspicious_list)}\n")
    print(suspicious_list)
    for item in suspicious_list:
        log.write(item + "\n")

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print()
    print(f"Ran script in {end_time - start_time:.6f} seconds checking {len(subject_list)} subjects")
    log.close()


cla()
main()