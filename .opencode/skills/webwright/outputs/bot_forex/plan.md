# Task

到台銀官網取得最新的台幣美金匯率

# Critical Points

- [x] CP1: Navigate to Bank of Taiwan official website forex/rate page
  - Evidence: `final_runs/run_1/screenshots/final_execution_2_page_loaded.png`, URL=`https://www.bot.com.tw/tw/personal-banking`
- [x] CP2: Locate the USD/TWD exchange rate on the page
  - Evidence: `final_runs/run_1/screenshots/final_execution_3_usd_slide_visible.png`, log step 3 confirms USD slide found
- [x] CP3: Record the displayed buying and selling rates for USD
  - Evidence: `final_runs/run_1/screenshots/final_execution_4_rates_extracted.png`, log step 4: 現金買進=31.625, 現金賣出=32.295, 即期買進=31.95, 即期賣出=32.1
- [x] CP4: Final datum appended to final_script_log.txt
  - Evidence: `final_runs/run_1/final_script_log.txt` lines 6-11 contain FINAL_RESPONSE
