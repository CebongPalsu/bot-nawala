import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from playwright.async_api import async_playwright

# ============ CONFIG ============
TOKEN = "TOKEN_BOT_LO"  # ganti dengan environment variable nanti di Railway
GROUP_ID = -4931279381  # ganti dengan environment variable nanti di Railway
MAX_DOMAIN = 50

# ============ FUNCTION CHECK DOMAIN ============
async def cek_domain(domain, browser):
    try:
        page = await browser.new_page()
        await page.goto("https://nawala.online/")
        await page.fill("input[name='url']", domain)
        await page.click("button[type='submit']")
        await page.wait_for_selector(".result")  # sesuaikan selector
        result_text = await page.inner_text(".result")
        await page.close()
        if "not blocked" in result_text.lower():
            return domain, "✅ Aman"
        else:
            return domain, "❌ Terblokir"
    except Exception as e:
        return domain, f"⚠ Error: {e}"

# ============ HANDLER COMMAND ============
async def cek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GROUP_ID:
        await update.message.reply_text("Bot hanya bisa digunakan di grup ini bro 😎")
        return

    if len(context.args) == 0:
        await update.message.reply_text(
            "Kirim domain setelah /cek, contoh:\n/cek domain1.com domain2.com ..."
        )
        return

    domains = context.args[:MAX_DOMAIN]
    await update.message.reply_text(f"Sedang cek {len(domains)} domain... ⏳")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        tasks = [cek_domain(domain, browser) for domain in domains]
        results = await asyncio.gather(*tasks)
        await browser.close()

    # Buat
