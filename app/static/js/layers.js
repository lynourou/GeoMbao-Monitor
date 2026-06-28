let foretLayer = null;

fetch("/api/foret/")
.then(response => response.json())
.then(data => {

    foretLayer = L.geoJSON(data, {

        style: {
            color: "#008000",
            weight: 2,
            fillColor: "#00AA00",
            fillOpacity: 0.30
        },

        onEachFeature: function(feature, layer){

            layer.bindPopup(`
                <h3>${feature.properties.nom}</h3>
                <b>Commune :</b> ${feature.properties.commune}<br>
                <b>Superficie :</b> ${feature.properties.superficie_ha.toFixed(2)} ha<br>
                <b>Département :</b> ${feature.properties.departement}<br>
                <b>Gestionnaire :</b> ${feature.properties.organisme_gestionaire}
            `);

        }

    });

    foretLayer.addTo(map);

    map.fitBounds(foretLayer.getBounds());

});


document
.getElementById("foret")
.addEventListener("change", function(){

    if(!foretLayer) return;

    if(this.checked){

        map.addLayer(foretLayer);

    }else{

        map.removeLayer(foretLayer);

    }

});