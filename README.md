Scraping products in promotional campaigns from Intermarche.pt


* Runs every day with GitHub Action scheduled to execute every 30 minutes from 10:15 to 13:45
* Saves products in CSV until webpages blocks it (usually after 3 or 4 requests)
* Combines result with earlier executions on the same day
* Conditional action: only executes when there are more pages to obtain products from
