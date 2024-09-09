// This example requires the Visualization library. Include the libraries=visualization
// parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=visualization">
let map, heatmap;

async function initMap() {
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

async function refreshData() {
    let serverData = await getServerData();
    let center = serverData.center;
    let zoom = serverData.zoom;
    let points = serverData.points;
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: zoom,
        center: center,
        mapTypeId: "satellite",
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

window.initMap = initMap;