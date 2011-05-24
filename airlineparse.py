from BeautifulSoup import BeautifulSoup
import re, simplejson, geopy, urllib

html = urllib.urlopen("http://ostpxweb.dot.gov/aviation/domfares/web20101.htm").read()
re_cityname = re.compile('(\S+,\s\S{2})|(\S+\s\w+, \w{2})|(Washington, \S{4})')
soup = BeautifulSoup(html)
city_latlon = {}

airline = soup.findAll("table", id='table1')
for a in airline:
	for row in a.findAll("tr"):
		col = row.findAll("td")
		try:
			city1 = re_cityname.search(col[1].string.strip())
			city2 = re_cityname.search(col[2].string.strip())
			nonstop_distance = col[3].string.strip()
			psg_per_day = col[4].string.strip()
			avg_one_way = col[5].string.strip()
			print city1.group(0), "\t", city2.group(0), "\t", nonstop_distance, "\t", avg_one_way
		except:
			continue
			