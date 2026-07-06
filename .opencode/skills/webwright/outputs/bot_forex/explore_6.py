import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

WORKSPACE = Path(".")
SCREENSHOTS = WORKSPACE / "screenshots"
SCREENSHOTS.mkdir(parents=True, exist_ok=True)


async def main():
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 1800})
        page = await context.new_page()

        await page.goto("https://www.bot.com.tw", wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)

        sys.stdout.reconfigure(encoding="utf-8")
        print("URL:", page.url)
        print("TITLE:", await page.title())

        # Get the swiper structure in detail
        swiper_html = await page.evaluate("""
            () => {
                const swiper = document.querySelector('.swiper-fx-rates');
                if (!swiper) return 'swiper not found';
                return swiper.outerHTML.substring(0, 8000);
            }
        """)
        print("\n=== SWIPER HTML ===")
        print(swiper_html)

        # Get all rate values for USD
        usd_values = await page.evaluate("""
            () => {
                const slides = document.querySelectorAll('.swiper-fx-rates .swiper-slide');
                const results = [];
                for (const slide of slides) {
                    const text = slide.textContent.trim();
                    if (text.includes('USD')) {
                        results.push({
                            text: text,
                            html: slide.innerHTML.substring(0, 2000)
                        });
                    }
                }
                return results;
            }
        """)
        print("\n=== USD SLIDES ===")
        for r in usd_values:
            print(f"  text: {r['text']}")
            print(f"  html: {r['html']}")

        # Also get update time
        update_time = await page.evaluate("""
            () => {
                const body = document.body.innerText;
                const match = body.match(/掛牌時間：([^\\n]+)/);
                return match ? match[1] : 'not found';
            }
        """)
        print(f"\n=== UPDATE TIME: {update_time} ===")

        await browser.close()


asyncio.run(main())
