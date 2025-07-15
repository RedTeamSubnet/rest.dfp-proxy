/**
 * Browser fingerprinting script that collects comprehensive browser characteristics
 * and sends them to an endpoint.
 */

function collectFingerprint() {
    return {
        userAgent: navigator.userAgent
    };
}

function createPayload(fingerprint, orderId) {
    const hash = btoa(JSON.stringify(fingerprint)).slice(0, 32);
	// localStorage.setItem("fingerprint", hash);
	console.log("Generated fingerprint:", hash);

	return {
        fingerprint: hash,
        timestamp: new Date().toISOString(),
        order_id: orderId
    };
}

async function sendFingerprint(payload) {
    const request = {
        method: "POST",
        body: JSON.stringify(payload),
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json"
        }
    };

    try {
        const response = await fetch(window.FINGERPRINT_ENDPOINT, request);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Error sending fingerprint:", errFor);
        throw error;
    }
}

function initializeFingerprint() {
    const urlParams = new URLSearchParams(window.location.search);
    const orderId = urlParams.get("order_id");
    const fingerprint = collectFingerprint();
    const payload = createPayload(fingerprint, orderId);
    return sendFingerprint(payload);
}

(function () {
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initializeFingerprint);
    } else {
        initializeFingerprint();
    }
})();
