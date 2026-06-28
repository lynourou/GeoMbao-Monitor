L.control.scale().addTo(map);

map.on("mousemove",function(e){

document.getElementById("coords").innerHTML=

"Lat : "

+

e.latlng.lat.toFixed(6)

+

" | Lon : "

+

e.latlng.lng.toFixed(6);

});