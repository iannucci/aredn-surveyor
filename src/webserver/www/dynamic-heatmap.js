// This example requires the Visualization library. Include the libraries=visualization
// parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=visualization">
let map
let heatmap
let loggingEnabled = false
const resizeObserver = new ResizeObserver(entries => {
    for (let entry of entries) {
        entry.target.style.width = entry.contentRect.width + 'px';
    }
})

async function initMap() {
    let serverData = await getServerData();
    let center = serverData.center;
    let zoom = serverData.zoom;
    let points = serverData.points;
    let controlPanel = document.getElementById('floating-control-panel');
    resizeObserver.observe(controlPanel);
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
    enableHeatmap(false);
    document
        .getElementById("enable-logging")
        .addEventListener("click", toggleLogging);
    document
        .getElementById("display-type")
        .addEventListener("change", changeDisplayType);
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

function changeDisplayType() {
    let heatmapPanel = document.getElementById("floating-heatmap-panel");
    let displayTypeDropdown = document.getElementById("display-type");
    let displayTypeValue = displayTypeDropdown.options[displayTypeDropdown.selectedIndex].text;
    enableHeatmap(displayTypeValue == 'Heatmap')
}

function enableHeatmap(enable) {
    let heatmapPanel = document.getElementById("floating-heatmap-panel");
    if (enable) {
        heatmapPanel.style.visibility = 'visible';
        heatmapPanel.offsetWidth;
        heatmap.setMap(map);
    } else {
        heatmapPanel.style.visibility = 'hidden';
        heatmapPanel.offsetWidth;
        heatmap.setMap(null);
    }
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

async function enableLogging(enable) {
    let button = document.getElementById("enable-logging");
    let sessionNameField = document.getElementById('session-name');
    if (enable) {
        let promptString = 'Enter the name for this session';
        var logName = prompt(promptString, "");
        if (logName) {
            button.style.backgroundColor = "red";
            button.innerHTML = 'Stop logging';
            sessionNameField.innerHTML = logName;
        }
        await serverStartLogging(logName);
    } else {
        button.style.backgroundColor = "green";
        button.innerHTML = 'Start logging';
        sessionNameField.innerHTML = '';
        await serverStopLogging();
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

async function serverStartLogging(logName) {
    const response = await fetch('logging', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            logging: true,
            logName: logName 
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