from playwright.sync_api import sync_playwright
import os
import time

start_time = time.perf_counter()

domain_list = ["greenmountains.ae", "yahoo.com", "biorus.ae", "188[.]92[.]255[.]57", "pragmaticus[.]ru"]
safe_text = "No security vendors flagged this domain as malicious"
safe_rating = "0"
suspicious_list = []

with sync_playwright() as p:
    browser = p.chromium.launch()
    pages = []

    for dom in domain_list:
        page = browser.new_page()
        page.goto("https://www.virustotal.com/gui/search?query=" + dom)
        pages.append(page)
    
    for page in pages:
        eval_locator = page.locator("div > div.card-header.hstack.flex-wrap.justify-content-between.gap-2 > div.hstack.gap-2.fw-bold[class*='text-']")
        rating_locator = page.locator("#positives")
        eval_locator.wait_for(state="visible")
        rating_locator.wait_for(state="visible")
        text = eval_locator.text_content()
        rating = rating_locator.text_content()
        rating = rating.strip()

        if rating != safe_rating and text != safe_text:
            print(f"------------ Suspicious Domain: {dom}")
            page.screenshot(path= os.path.join("screenshots", dom + ".png"))
            suspicious_list.append(dom)
        else:
            print(f"--- Domain: {dom}")
    
        print(f"Evaluation: {text}")
        print(f"Rating: {rating}/91")

    browser.close()
    
print(f"Suspicious Domains: {len(suspicious_list)}")
print(suspicious_list)

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print()
print(f"Ran script in {end_time - start_time:.6f} seconds")