function updateDashboard(){

    fetch("/api/dashboard")

    .then(r=>r.json())

    .then(data=>{

        document.getElementById("surface").innerHTML =
            data.surface.toFixed(2)+" ha";

        document.getElementById("commune").innerHTML =
            data.commune;

        document.getElementById("departement").innerHTML =
            data.departement;

        document.getElementById("annee").innerHTML =
            data.classement;

    });

}

updateDashboard();