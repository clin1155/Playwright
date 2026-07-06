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
        await page.screenshot(path=str(SCREENSHOTS / "explore_5_home.png"))

        sys.stdout.reconfigure(encoding='utf-8')
        print("URL:", page.url)
        print("TITLE:", await page.title())

        # Get innerText of the whole body
        inner_text = await page.evaluate("() => document.body.innerText")
        print("\n=== BODY INNER TEXT ===")
        sys.stdout.reconfigure(encoding='utf-8')
        with open("body_text.txt", "w", encoding="utf-8") as f:
            f.write(inner_text)
        print(inner_text[:5000])

        # Get the full DOM around the exchange rate section
        # Find elements that contain rate text
        rate_html = await page.evaluate("""
            () => {
                const elements = document.querySelectorAll('[class*="rate"], [class*="Rate"], [class*="forex"], [class*="exchange"]');
                const results = [];
                for (const el of elements) {
                    results.push({
                        class: el.className,
                        text: el.textContent.trim().substring(0, 500),
                        id: el.id
                    });
                }
                return results;
            }
        """)
        print("\n=== RATE-RELATED ELEMENTS ===")
        for r in rate_html:
            print(f"  class={r['class'][:80]}, text={r['text'][:200]}")

        # Look for specific currency converter section
        converter = await page.evaluate("""
            () => {
                const sections = document.querySelectorAll('app-currency-converter, [class*="currency"], [class*="Currency"]');
                const results = [];
                for (const el of sections) {
                    results.push({
                        tag: el.tagName,
                        class: el.className,
                        html: el.outerHTML.substring(0, 3000)
                    });
                }
                return results;
            }
        """)
        print("\n=== CURRENCY CONVERTER ===")
        for c in converter:
            print(f"  tag={c['tag']}, class={c['class'][:80]}")
            print(f"  html={c['html']}")

        # Get the immediate DOM around text nodes with USD and numbers
        all_text = await page.evaluate("""
            () => {
                const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ALL, null, false);
                const results = [];
                let node;
                while (node = walker.nextNode()) {
                    if (node.nodeType === 1) {
                        const text = node.textContent.trim();
                        if (text && text.includes('USD') && !node.querySelector('*')) {
                            results.push({
                                tag: node.tagName,
                                text: text,
                                parentClass: node.parentElement?.className || '',
                                outer: node.parentElement?.outerHTML?.substring(0, 1000) || ''
                            });
                        }
                    }
                }
                return results;
            }
        """)
        print("\n=== USD CONTAINERS ===")
        for r in all_text:
            print(f"  tag={r['tag']}, text={r['text']}, parentClass={r['parentClass'][:80]}")
            print(f"  outer={r['outer']}")
            print("---")

        await browser.close()

asyncio.run(main())
