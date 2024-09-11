cd /Users/charliechapman/Developer/rssify
./scrape-feeds.sh

git add .
git status
git commit -m "update feeds"
git push origin HEAD -u
git status