
const a = 6378137.0;  
const f = 1 / 298.257223563; 
const e2 = (Math.pow(a, 2) - Math.pow(a * (1 - f), 2)) / Math.pow(a, 2);  


function degToRad(deg) {
    return deg * (Math.PI / 180);
}

function radToDeg(rad) {
    return rad * (180 / Math.PI);
}


function geodeticToCartesian(lat, lon, h) {
    lat = degToRad(lat);
    lon = degToRad(lon);
    
    const N = a / Math.sqrt(1 - e2 * Math.pow(Math.sin(lat), 2));
    
    const X = (N + h) * Math.cos(lat) * Math.cos(lon);
    const Y = (N + h) * Math.cos(lat) * Math.sin(lon);
    const Z = (N * (1 - e2) + h) * Math.sin(lat);
    
    return { X, Y, Z };
}

function cartesianToGeodeticDirect(X, Y, Z) {
    const r = Math.sqrt(X**2 + Y**2 + Z**2);
    const mu = Math.atan((Z / Math.sqrt(X**2 + Y**2)) * (((1 - f)) + ((a * e2) / r)));

    const lon = Math.atan2(Y, X);  

    const sin_mu = Math.sin(mu);
    const cos_mu = Math.cos(mu);
    
    const lat = Math.atan(
        (Z * (1 - f) + e2 * a * Math.pow(sin_mu, 3)) /
        ((1 - f) * (Math.sqrt(X**2 + Y**2) - e2 * a * Math.pow(cos_mu, 3)))
    );

    const h = (Math.sqrt(X**2 + Y**2) * Math.cos(lat) +
         Z * Math.sin(lat) -
         a * Math.sqrt(1 - e2 * Math.sin(lat)**2));
    
    return { lat: radToDeg(lat), lon: radToDeg(lon), h };
}


function cartesianToGeodeticIterative(X, Y, Z, epsilon = 1e-12, max_iter = 1000) {
    const lon = Math.atan2(Y, X);
    
    const p = Math.sqrt(X**2 + Y**2);
    let phi = Math.atan(Z / p);
    
    for (let i = 0; i < max_iter; i++) {
        const N = a / Math.sqrt(1 - e2 * Math.sin(phi)**2);
        const h = p / Math.cos(phi) - N;
        
        const phi_new = Math.atan((Z / p) * (1 / (1 - e2 * N / (N + h))));
        
        if (Math.abs((phi_new - phi) / phi_new) < epsilon) {
            phi = phi_new;
            break;
        }
        
        phi = phi_new;
    }
    
    const lat = radToDeg(phi);
    
    return { lat, lon: radToDeg(lon), h };
}

function convert() {
    const conversionType = document.querySelector('input[name="conversion"]:checked').value;
    let result;

    if (conversionType === "geodeticToCartesian") {
        const lat = parseFloat(document.getElementById("latitude").value);
        const lon = parseFloat(document.getElementById("longitude").value);
        const h = parseFloat(document.getElementById("height").value);
        result = geodeticToCartesian(lat, lon, h);
        document.getElementById("result").innerHTML = `X: ${result.X.toFixed(6)}, Y: ${result.Y.toFixed(6)}, Z: ${result.Z.toFixed(6)}`;
    } else if (conversionType === "cartesianToGeodeticDirect") {
        const X = parseFloat(document.getElementById("X").value);
        const Y = parseFloat(document.getElementById("Y").value);
        const Z = parseFloat(document.getElementById("Z").value);
        result = cartesianToGeodeticDirect(X, Y, Z);
        document.getElementById("result").innerHTML = `Latitude: ${result.lat}, Longitude: ${result.lon}, Altitude: ${result.h.toFixed(2)} meters`;
    } else if (conversionType === "cartesianToGeodeticIterative") {
        const X = parseFloat(document.getElementById("X").value);
        const Y = parseFloat(document.getElementById("Y").value);
        const Z = parseFloat(document.getElementById("Z").value);
        result = cartesianToGeodeticIterative(X, Y, Z);
        document.getElementById("result").innerHTML = `Latitude: ${result.lat}, Longitude: ${result.lon}, Altitude: ${result.h.toFixed(2)} meters`;
    } else {
        document.getElementById("result").innerHTML = "Erreur : Type de conversion non reconnu.";
    }
}

