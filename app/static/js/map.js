const map = L.map("map");

map.setView([14.75,-17.33],14);

const osm = L.tileLayer(

"https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",

{

maxZoom:20,

attribution:"OpenStreetMap"

}

);

osm.addTo(map);