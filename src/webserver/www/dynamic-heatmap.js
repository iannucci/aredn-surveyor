// This example requires the Visualization library. Include the libraries=visualization
// parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=visualization">
let map
let heatmap
let loggingEnabled = false

async function initMap() {
    let serverData = await getServerData();
    let center = serverData.center;
    let zoom = serverData.zoom;
    let points = serverData.points;
    enableLogging(false);
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: zoom,
        center: center,
        mapTypeId: "satellite",
        tilt: 0,
    });
    heatmap = new google.maps.visualization.HeatmapLayer({
        data: pointsToGoogleLatLng(points),
        map: map,
    });
    document
        .getElementById("toggle-heatmap")
        .addEventListener("click", toggleHeatmap);
    document
        .getElementById("change-gradient")
        .addEventListener("click", changeGradient);
    document
        .getElementById("change-opacity")
        .addEventListener("click", changeOpacity);
    document
        .getElementById("change-radius")
        .addEventListener("click", changeRadius);
    document
        .getElementById("refresh-data")
        .addEventListener("click", refreshData);
    document
        .getElementById("enable-logging")
        .addEventListener("click", toggleLogging)
}

function toggleHeatmap() {
    heatmap.setMap(heatmap.getMap() ? null : map);
}

function changeGradient() {
    const gradient = [
        "rgba(0, 255, 255, 0)",
        "rgba(0, 255, 255, 1)",
        "rgba(0, 191, 255, 1)",
        "rgba(0, 127, 255, 1)",
        "rgba(0, 63, 255, 1)",
        "rgba(0, 0, 255, 1)",
        "rgba(0, 0, 223, 1)",
        "rgba(0, 0, 191, 1)",
        "rgba(0, 0, 159, 1)",
        "rgba(0, 0, 127, 1)",
        "rgba(63, 0, 91, 1)",
        "rgba(127, 0, 63, 1)",
        "rgba(191, 0, 31, 1)",
        "rgba(255, 0, 0, 1)",
    ];

    heatmap.set("gradient", heatmap.get("gradient") ? null : gradient);
}

function changeRadius() {
    heatmap.set("radius", heatmap.get("radius") ? null : 20);
}

function changeOpacity() {
    heatmap.set("opacity", heatmap.get("opacity") ? null : 0.2);
}

function toggleLogging() {
    enableLogging(!loggingEnabled)
}

function enableLogging(enable) {
    let button = document.getElementById("enable-logging");
    if (enable) {
        button.style.backgroundColor = "red";
        button.innerHTML = 'Stop logging';
        let promptString = 'Enter the name for this session';
        var retVal = prompt(promptString, "");
    } else {
        button.style.backgroundColor = "green";
        button.innerHTML = 'Start logging';
    }
    loggingEnabled = enable;
}

async function refreshData() {
    let serverData = await getServerData();
    let center = serverData.center;
    let zoom = serverData.zoom;
    let points = serverData.points;
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: zoom,
        center: center,
        mapTypeId: "satellite",
        tilt: 0,
    });
    heatmap = new google.maps.visualization.HeatmapLayer({
        data: pointsToGoogleLatLng(points),
        map: map,
    });
}

async function getServerData() {
    let serverResponse = await fetch('heatmap-data');
    let serverJSON = serverResponse.json()
    return serverJSON;
}

function pointsToGoogleLatLng(points) {
    let result = [];
    points.forEach(point => {
        let lat = point.lat
        let lng = point.lng
        let googleLatLng = new google.maps.LatLng(lat, lng)
        result.push(googleLatLng)
    }); 
    return result;
}


function loggingModal() {
    var modal = document.getElementById("loggingModal");
    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];
    // When the user clicks on <span> (x), close the modal
    span.onclick = function () {
        modal.style.display = "none";
    }
    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function (event) {
        if (event.target != modal) {
            modal.style.display = "none";
        }
    }
}
window.initMap = initMap;