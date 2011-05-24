require 'rubygems'
require 'nokogiri'
require 'rest-open-uri'
require 'pp'
require 'json'
require 'geokit'
include Geokit::Geocoders

url = "http://ostpxweb.dot.gov/aviation/domfares/web20101.htm"
htmlcontent = ""
re_cityname = /.+,\s\S{2}|[A-z]+\s\w+, \w{2}|Washington, \S{4}/

open(url){|f|
	htmlcontent = f.read
}

doc = Nokogiri::HTML.parse(htmlcontent)
table1 = doc.xpath("//table[@id='table1']/tr")

details = {:type => "FeatureCollection", :features=>[]}

table1.each do |row| 
	isNilEntry = false
	detail = {:properties => {}, :type=> "Feature", :geometry => {:type=>"LineString", :coordinates=>[]}}
	[
		[:CITYNAME1, 'td[2]/text()'],
		[:CITYNAME2, 'td[3]/text()'],
		[:NONSTOPDIST, 'td[4]/text()'],
		[:AVG_ONE_WAY_FARE, 'td[6]/text()']
	
	].collect do |name, xpath|
		if name.to_s.include?('CITYNAME')
			citymatch = re_cityname.match(row.at_xpath(xpath).to_s.strip)
			if not citymatch.nil?
				detail[:properties][name] = citymatch[0]
				city = MultiGeocoder.geocode(citymatch[0])
				detail[:geometry][:coordinates] << [city.lng, city.lat]
			else
				isNilEntry = true
			end
		else
			detail[:properties][name] = row.at_xpath(xpath).to_s.strip
		end
	end
	if !isNilEntry
		details[:features] << detail  
	end
end
	
File.open('airline.json', 'w') {|f| f.write(details.to_json)}
