   #!/bin/bash
   source /Users/charliechapman/Developer/rssify/rss_env/bin/activate
   
   python /Users/charliechapman/Developer/rssify/scrape-wkt.py
   python /Users/charliechapman/Developer/rssify/post-articles.py