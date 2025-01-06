Scraping products in promotional campaigns from Intermarche.pt

Update 2025/01/06: Apparently, the Python version I had chosen for this project (3.7.15) is no longer supported, so I made the switch to 3.7.17, which is on the list of supported versions: https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json

* Runs every day with GitHub Action scheduled to execute every 30 minutes from 10:15 to 13:45
* Saves products in CSV until webpages blocks it (usually after 3 or 4 requests)
* Combines result with earlier executions on the same day
* Conditional action: only executes when there are more pages to obtain products from
