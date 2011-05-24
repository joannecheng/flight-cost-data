require 'rubygems'
require 'nokogiri'
require 'rest-open-uri'
require 'pp'
require 'json'
require 'geokit'
require 'net/http'
require 'uri'
include Geokit::Geocoders

host_url = "http://airline-data.appspot.com/"
#host_url = "http://localhost:8080/"

url = "http://ostpxweb.dot.gov/aviation/domfares/web20101.htm"
add_city_url = host_url+"add_city"
add_route_url = host_url+"add_route"
htmlcontent = ""
re_cityname = /Washington, \S{4}|.+,\s\S{2}|[A-z]+\s\w+, \w{2}/

open(url){|f|
	htmlcontent = f.read
}

doc = Nokogiri::HTML.parse(htmlcontent)
table1 = doc.xpath("//table[@id='table1']/tr")

table1.each do |row| 
	isNilEntry = false
	formdata = {}
	formdata2 = {}
	[
		[:CITYNAME1, 'td[2]/text()'],
		[:CITYNAME2, 'td[3]/text()'],
		[:NONSTOPDIST, 'td[4]/text()'],
		[:AVG_ONE_WAY_FARE, 'td[6]/text()']
	
	].collect do |name, xpath|
		if name.to_s.include?('CITYNAME')
			citymatch = re_cityname.match(row.at_xpath(xpath).to_s.strip)
			if not citymatch.nil?
				city = MultiGeocoder.geocode(citymatch[0])
				formdata[name.to_s] = JSON.generate({:city_name => citymatch[0], :lat => city.lat, :long =>city.lng})
			else
				isNilEntry = true
			end
		else
			formdata[name.to_s] = row.at_xpath(xpath).to_s.strip
		end
	end
	if !isNilEntry
		res2= Net::HTTP.post_form(URI.parse(add_route_url), formdata)
	end
end
	
