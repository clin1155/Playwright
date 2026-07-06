import asyncio
import re
from pathlib import Path

from playwright.async_api import async_playwright

RUN_DIR = Path(__file__).parent
SCREENSHOTS = RUN_DIR / "screenshots"
SCREENSHOTS.mkdir(parents=True, exist_ok=True)
LOG = RUN_DIR / "final_script_log.txt"
LOG.write_text("")

def log(step: int, msg: str) -> None:
    line = f"step {step} action: {msg}\n"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line)
    print(line, end="")

async def main():
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 1800})
        page = await context.new_page()

        await page.goto("https://www.bot.com.tw", wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)

        await page.screenshot(path=str(SCREENSHOTS / "final_execution_1_open_homepage.png"))
        log(1, "open Bank of Taiwan homepage")

        url = page.url
        title = await page.title()
        log(2, f"page loaded: url={url}, title={title}")
        await page.screenshot(path=str(SCREENSHOTS / "final_execution_2_page_loaded.png"))

        # Locate USD card in the swiper-fx-rates slider
        usd_slide = page.locator(".swiper-fx-rates .swiper-slide").filter(has_text="USD")
        await usd_slide.first.wait_for(state="visible", timeout=10000)

        await page.screenshot(path=str(SCREENSHOTS / "final_execution_3_usd_slide_visible.png"))
        log(3, "USD slide is visible in the forex rates carousel")

        # Extract rates from the USD card
        rates = await usd_slide.first.evaluate("""
            (el) => {
                const labels = el.querySelectorAll('.market-out');
                const values = el.querySelectorAll('.market-no');
                const result = {};
                for (let i = 0; i < labels.length; i++) {
                    result[labels[i].textContent.trim()] = values[i].textContent.trim();
                }
                return result;
            }
        """)

        # Extract update time
        body_text = await page.evaluate("() => document.body.innerText")
        time_match = re.search(r'掛牌時間：([^\n]+)', body_text)
        update_time = time_match.group(1) if time_match else "unknown"

        await page.screenshot(path=str(SCREENSHOTS / "final_execution_4_rates_extracted.png"))
        log(4, f"USD rates extracted: {rates}, update time: {update_time}")

        spot_buying = rates.get("即期買進", "N/A")
        spot_selling = rates.get("即期賣出", "N/A")
        cash_buying = rates.get("現金買進", "N/A")
        cash_selling = rates.get("現金賣出", "N/A")

        # Build final response
        final = (
            f"臺灣銀行美金/臺幣即期匯率 (掛牌時間：{update_time})\n"
            f"  即期買入 (Spot Buying):  {spot_buying}\n"
            f"  即期賣出 (Spot Selling): {spot_selling}\n"
            f"  現金買入 (Cash Buying):   {cash_buying}\n"
            f"  現金賣出 (Cash Selling):  {cash_selling}\n"
        )

        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"\nFINAL_RESPONSE:\n{final}\n")

        print(f"\n=== FINAL_RESPONSE ===\n{final}")

        await browser.close()

asyncio.run(main())
