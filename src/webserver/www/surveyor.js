// This example requires the Visualization library. Include the libraries=visualization
// parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=visualization">
let map;
let heatmap = null;
let loggingEnabled = false;
let markers;
const { Map } = await google.maps.importLibrary("maps");
const { AdvancedMarkerElement, PinElement } = await google.maps.importLibrary("marker");

async function initMap() {
    document
        .getElementById("enable-logging")
        .addEventListener("click", toggleLogging);
    document
        .getElementById("display-type")
        .addEventListener("change", refreshPointData);
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
        .addEventListener("click", refreshPointData);
    document
        .getElementById("start-time")
        .addEventListener("change.td", refreshPointData);
    document
        .getElementById("stop-time")
        .addEventListener("change", refreshPointData);
    map = await new Map(document.getElementById("map"), {
        mapTypeId: 'satellite',
        tilt: 0,
        mapId: '2b79a6cc78f5307a'
    });
    checkInProcessSession();
    markers = [];
    await refreshPointData();
}

async function checkInProcessSession() {
    // The state of the logging operation is held in the server, not the client.
    //
    // Query the server and update the UI accordingly
    let sessionName = await serverSessionName();
    let button = document.getElementById("enable-logging");
    if (sessionName != '') {
        button.style.backgroundColor = "red";
        button.innerHTML = sessionName;
        loggingEnabled = true;
    } else {
        button.style.backgroundColor = "green";
        button.innerHTML = 'Start logging';
        loggingEnabled = false;
    }
}

function clearMarkers() {
    if (markers != []) {
        markers.map(marker => {
            marker.setMap(null);
        });
        markers = [];
    }
}

async function refreshPointData() {
    clearMarkers();
    let pointData = await serverGetPoints();
    let displayTypeDropdown = document.getElementById("display-type");
    let displayTypeValue = displayTypeDropdown.options[displayTypeDropdown.selectedIndex].text;
    let heatmapPanel = document.getElementById("floating-heatmap-panel");
    let pointList = pointData.points;
    let center = pointData.center;
    let zoom = pointData.zoom;
    map.setCenter(center);
    map.setZoom(zoom);
    if (typeof pointList !== 'undefined') {
        switch (displayTypeValue) {
            case 'Points':
                if (typeof pointList !== 'undefined') {
                    pointList.forEach((point) => {
                        let newMarker = new AdvancedMarkerElement({
                            position: point,
                            map: map
                        });
                        markers.push(newMarker);
                    });
                    heatmapPanel.style.visibility = 'hidden';
                    if (map && heatmap) {
                        heatmap.setMap(null);
                    }
                }
                break;
            case 'Signal strength':
                heatmapPanel.style.visibility = 'hidden';
                if (map && heatmap) {
                    heatmap.setMap(null);
                }
                break;
            case 'Heatmap':
                if (heatmap !== null) {
                    heatmap.setMap(null);
                    heatmap = null;
                }
                let googlePointList = await pointsToGoogleLatLng(pointList);
                heatmap = await new google.maps.visualization.HeatmapLayer({
                    data: googlePointList
                });
                heatmapPanel.style.visibility = 'visible';
                heatmap.setMap(map);
                break;
            default:
                break;
        }
    }
}


async function pointsToGoogleLatLng(points) {
    let result = points.map(point => {
        let lat = point['lat'];
        let lng = point['lng'];
        return new google.maps.LatLng(lat, lng);
    });
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
            button.innerHTML = sessionName;
            await serverStartLogging(sessionName);
            loggingEnabled = true;
        }
    } else {
        button.style.backgroundColor = "green";
        button.innerHTML = 'Start logging';
        await serverStopLogging();
        loggingEnabled = false;
    }
}

function toggleLogging() {
    enableLogging(!loggingEnabled)
}

// --------------------------------------
// Server interaction
// --------------------------------------

async function serverGetPoints() {
    let serverJSON;
    try {
        let startTime;
        let stopTime;
        let startTimeField = document.getElementById("start-time");
        if (startTimeField.value == '') {
            startTime = Math.round(Date.now() / 1000);
        } else {
            startTime = Math.round(Date.parse(startTimeField.value) / 1000);
        }
        let stopTimeField = document.getElementById("stop-time");
        if (stopTimeField.value == '') {
            stopTime = Math.round(Date.now() / 1000);
        } else {
            stopTime = Math.round(Date.parse(stopTimeField.value) / 1000);
        }
        let serverResponse = await fetch('point-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                startTime: startTime,
                stopTime: stopTime
            })
        });
        serverJSON = serverResponse.json();
    } catch (error) {
        console.error(error.message);
    }
    return serverJSON;
}

async function serverStartLogging(sessionName) {
    let serverJSON;
    try {
        const response = await fetch('logging', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                logging: {
                    sessionName: sessionName
                }
            })
        });
        serverJSON = await response.json();
    } catch (error) {
        console.error(error.message);
    }
    return serverJSON;
}

async function serverStopLogging() {
    let serverJSON;
    try {
        const response = await fetch('logging', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                logging: stop
            })
        });
        serverJSON = await response.json();
    } catch (error) {
        console.error(error.message);
    }
    return serverJSON;
}

async function serverSessionName() {
    let serverJSON;
    try {
        const response = await fetch('logging', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                logging: 'query'
            })
        });
        serverJSON = await response.json();
        return serverJSON.sessionName;
    } catch (error) {
        console.error(error.message);
    }
}

initMap();