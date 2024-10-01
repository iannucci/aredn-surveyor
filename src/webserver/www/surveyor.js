// This example requires the Visualization library. Include the libraries=visualization
// parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=visualization">
let map;
let heatmap = null;
let loggingEnabled = false;

async function initMap() {
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
    enableLogging(false);
    document
        .getElementById("enable-logging")
        .addEventListener("click", toggleLogging);
    document
        .getElementById("display-type")
        .addEventListener("change", refreshData);
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
        .getElementById("start-time")
        .addEventListener("change", serverStartTime);
    document
        .getElementById("stop-time")
        .addEventListener("change", serverStopTime);
    let serverData = await serverGetPoints();
    await refreshMap(Map, serverData);
    await refreshData(AdvancedMarkerElement, serverData);
}

async function refreshMap(MapClass, serverData) {
    let center = serverData.center;
    let zoom = serverData.zoom;
    map = await new MapClass(document.getElementById("map"), {
        zoom: zoom,
        center: center,
        mapTypeId: 'satellite',
        tilt: 0,
        mapId: '2b79a6cc78f5307a'
    });
}

function refreshData(MarkerClass, serverData) {
    let displayTypeDropdown = document.getElementById("display-type");
    let displayTypeValue = displayTypeDropdown.options[displayTypeDropdown.selectedIndex].text;
    let heatmapPanel = document.getElementById("floating-heatmap-panel");
    let points = serverData.points;
    switch (displayTypeValue) {
        case 'Points':
            points.forEach(point => {
                new MarkerClass({
                    position: point,
                    map: map
                });
            });
            heatmapPanel.style.visibility = 'hidden';
            if (map && heatmap) {
                heatmap.setMap(null);
            }
            break;
        case 'Signal strength':
            heatmapPanel.style.visibility = 'hidden';
            if (map && heatmap) {
                heatmap.setMap(null);
            }
            break;
        case 'Heatmap':
            heatmap = new google.maps.visualization.HeatmapLayer({
                // data: pointsToGoogleLatLng(points),
                data: points,
                map: map,
            });
            heatmapPanel.style.visibility = 'visible';
            heatmap.setMap(map);
            break;
        default:
            break;
    }
}

function pointsToGoogleLatLng(points) {
    // pattern: new google.maps.LatLng(37.751266, -122.403355)
    let result = [];
    for (point in points) {
        let lat = point['lat'];
        let lng = point['lng'];
        let googleLatLng = 'new google.maps.LatLng(${lat}, ${lng})';
        result.push(googleLatLng)
    }
    return result
}

// --------------------------------------
// Heatmap specific
// --------------------------------------

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

// --------------------------------------
// Logging specific 
// --------------------------------------

async function enableLogging(enable) {
    let button = document.getElementById("enable-logging");
    let sessionNameField = document.getElementById('session-name');
    if (enable) {
        let promptString = 'Enter the name for this session';
        var sessionName = prompt(promptString, "");
        if (sessionName) {
            button.style.backgroundColor = "red";
            button.innerHTML = 'Stop logging';
            sessionNameField.innerHTML = sessionName;
        }
        await serverStartLogging(sessionName);
    } else {
        button.style.backgroundColor = "green";
        button.innerHTML = 'Start logging';
        sessionNameField.innerHTML = '';
        await serverStopLogging();
    }
    loggingEnabled = enable;
}

function toggleLogging() {
    enableLogging(!loggingEnabled)
}

// --------------------------------------
// Server interaction
// --------------------------------------

async function serverGetPoints() {
    let serverResponse = await fetch('point-data');
    let serverJSON = serverResponse.json();
    return serverJSON;
}

async function serverStartLogging(sessionName) {
    const response = await fetch('logging', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            logging: true,
            sessionName: sessionName 
        }) 
    });
    return response;
}

async function serverStopLogging() {
    const response = await fetch('logging', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            logging: false 
        })
    });
    return response;
}

async function serverStartTime(time) {
    let button = document.getElementById("start-time");
    let startDate = button.innerHTML;
    const response = await fetch('logging', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            startTime: time
        })
    });
    return response;
}

async function serverStopTime(time) {
    let button = document.getElementById("stop-time");
    let startDate = button.innerHTML;
    const response = await fetch('logging', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            stopTime: time
        })
    });
    return response;
}

// window.initMap = initMap;
initMap();