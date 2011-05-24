var po = org.polymaps;
var color = pv.Scale.linear()
	.domain(0,1,2,3)
    .range("#F00", "#930", "#FC0", "#3B0");

var map = po.map()
    .container(document.getElementById("map").appendChild(po.svg("svg")))
	.center({lat: 36.952335, lon: -94.7088238,})
	.zoom(4.5)
	.zoomRange([3,18])
    .add(po.interact());

map.add(po.image().url(po.url("http://{S}tile.cloudmade.com"
    + "/9a0f2b8dc3d94c90b67b1e0d2a0792dd" 
   + "/998/256/{Z}/{X}/{Y}.png")
    .hosts(["a.", "b.", "c.", ""])));

//points
map.add(po.geoJson()
	.url("airline.json")
	.id("airline")
	.tile(false)
	.on("load", po.stylist()
		.attr("stroke", function(d) { return color(d.properties.NONSTOPDIST/(d.properties.AVG_ONE_WAY_FARE.replace('$', ''))).color; } )
		));

map.add(po.compass()
    .pan("none"));


function get_city_names(v){
	var a=[];
	var names = ['one', 'two', 'three'];
	for(var i=0;i<names.length;i++){
		a.push({id:i, value:v+names[i], info:"demo string #"+i});
	}
	return a;
}
function print_sugg(obj){
	$('$selectbox').html
}
