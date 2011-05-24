from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson
from google.appengine.ext.webapp import template
import os, logging


class CityInfo(db.Model):
	date_updated = db.DateTimeProperty(auto_now_add=True)
	city_name = db.StringProperty()
	location = db.GeoPtProperty()
	def __unicode__(self):
		return self.city_name
	
class Route(db.Model):
	#switch to IDs?!??!
	distance = db.IntegerProperty()
	avg_one_way_fare = db.IntegerProperty()
	cities = db.ListProperty(db.Key)
	
	def cost_per_mile(self):
		return float(self.avg_one_way_fare)/float(self.distance)
	

class MainPage(webapp.RequestHandler):
	def get(self):
		cities = db.GqlQuery("Select * From CityInfo")
		ret_array = [c.city_name for c in cities]
		template_values = {
			'cities': ret_array,
		}
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))
		
class AddCity(webapp.RequestHandler):
	def post(self):
		city = CityInfo()
		
		lat = self.request.get('lat')
		long = self.request.get('long')
		city.city_name = self.request.get('city_name')
		city2 = CityInfo().all().filter("city_name = ", city.city_name).fetch(1)
		
		if(lat != "" and long != "") and len(city2) == 0:
			city.location = db.GeoPt(lat, long)
			city.put()
		self.redirect('/')

class TestRoutes(webapp.RequestHandler):
	def post(self):
		routes = Route().all()
		
		for r in routes:
			self.response.out.write("<br />%s "%r.cities)

		
class AddRoute(webapp.RequestHandler):
	def isNotInCityInfo(self, city_name):
		if len(CityInfo().all().filter("city_name = ", city_name).fetch(1)) == 0:
			return 1
		return 0
		
	def addCityInfo(self, cityinfo):
		city = CityInfo()
		city.location = db.GeoPt(cityinfo['lat'], cityinfo['long'])
		city.city_name = cityinfo["city_name"]
		return city
	
	def post(self):
		route = Route()
		city1 = CityInfo()
		
		route.distance = int(self.request.get('NONSTOPDIST'))
		route.avg_one_way_fare = int(self.request.get('AVG_ONE_WAY_FARE').strip('$'))
		
		
		cityinfo1 = simplejson.loads(self.request.get('CITYNAME1'))
		if self.isNotInCityInfo(cityinfo1["city_name"]):
			city = self.addCityInfo(cityinfo1)
			city.put()
			route.cities.append(city.key())
			route.put()
		else: 
			city = CityInfo().gql("WHERE city_name= :1", cityinfo1['city_name']).get()
			route.cities.append(city.key())
			route.put()
			
		cityinfo2 = simplejson.loads(self.request.get('CITYNAME2'))
		if self.isNotInCityInfo(cityinfo2["city_name"]):
			city = self.addCityInfo(cityinfo2)
			city.put()
			route.cities.append(city.key())
			route.put()
		else: 
			city = CityInfo().gql("WHERE city_name= :1", cityinfo2['city_name']).get()
			route.cities.append(city.key())
			route.put()
		
class DelCity(webapp.RequestHandler):
	def post(self):
		city = db.GqlQuery("SELECT * FROM CityInfo WHERE city_name = '%s'" % self.request.get('city_name'))
		results = city.fetch(1)
		db.delete(results)
		self.redirect('/')

		
class GetCities(webapp.RequestHandler):
	def get(self):
		self.response.headers.add_header("content-type", "application/json")
		cities = CityInfo.all()
		ret_array = [c.city_name for c in cities]
		self.response.out.write(simplejson.dumps({"cities":ret_array}))

class GetOtherCities(webapp.RequestHandler):
	def get(self):
		self.response.headers.add_header("content-type", "application/json")
		city1 = self.request.get('city1')

		city = CityInfo.gql("WHERE city_name = '%s'"%city1).get()
		cities = []
		routes = []
		
		endpoints = Route.gql("WHERE cities = :1", city.key())
		for r in endpoints:
			r_cities = set(r.cities)
			r_cities.remove(city.key())
			cities.append({"label": CityInfo.get(r_cities.pop()).city_name, "id": str(r.key())}) 
			
		self.response.out.write(simplejson.dumps(cities))

class GetScale(webapp.RequestHandler):
	def get(self):
		self.response.headers.add_header("content-type", "application/json")
		routedata = Route.all()
		cpermile = [r.cost_per_mile() for r in routedata]
		
		self.response.out.write(simplejson.dumps({
			"max": max(cpermile), 
			"min": min(cpermile), 
			"mid1": max(cpermile)/4, 
			"mid2": (max(cpermile)*3)/4}
		))
		

class GetRoute(webapp.RequestHandler):
	def get(self):
		self.response.headers.add_header("content-type", "application/json")
		routeid = self.request.get('route')
		routedata = Route.get(db.Key(encoded=routeid))
		coordinates = [];
		for c in routedata.cities:
			city = CityInfo.get(c)
			coordinates.append([city.location.lon, city.location.lat])
			
		detail = {
			"properties": {
				"avg_one_way_fare": routedata.avg_one_way_fare, 
				"distance": routedata.distance,
				"cost_per_mile": routedata.cost_per_mile()
			}, 
			"type": "Feature", 
			"geometry": 
				{"type": "LineString",
				"coordinates": coordinates
				}
			}
		
		self.response.out.write(simplejson.dumps(detail))
		
application = webapp.WSGIApplication(
							[('/', MainPage),
							('/add_city', AddCity),
							('/del_city', DelCity),
							('/get_cities', GetCities),
							('/get_route', GetRoute),
							('/get_other_cities', GetOtherCities),
							('/test_routes', TestRoutes),
							('/get_scale', GetScale),
							('/add_route', AddRoute)], 
							debug=True)

def main():
	run_wsgi_app(application)
	
if __name__ == "__main__":
	main()