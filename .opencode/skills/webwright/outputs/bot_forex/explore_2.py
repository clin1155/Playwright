import asyncio
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
        await page.wait_for_timeout(3000)
        await page.screenshot(path=str(SCREENSHOTS / "explore_2_home.png"))

        print("URL:", page.url)
        print("TITLE:", await page.title())

        # Get all links
        links = await page.evaluate("""
            () => Array.from(document.querySelectorAll('a')).map(a => ({
                href: a.href,
                text: a.textContent.trim()
            }))
        """)
        print("\n=== ALL LINKS ===")
        for l in links:
            if l['text']:
                print(f"  {l['text']} -> {l['href']}")

        # Get all headings
        headings = await page.evaluate("""
            () => Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => ({
                tag: h.tagName,
                text: h.textContent.trim()
            }))
        """)
        print("\n=== HEADINGS ===")
        for h in headings:
            if h['text']:
                print(f"  {h['tag']}: {h['text']}")

        # Check for forex / rate related elements
        body_text = await page.evaluate("() => document.body.innerText")
        print("\n=== BODY TEXT (first 2000 chars) ===")
        print(body_text[:2000])

        await browser.close()

asyncio.run(main())
