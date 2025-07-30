export async function preProcess() {
	console.log("[PreProcess] Starting environment cleanup...");

	// Clear storages
	localStorage.clear();
	sessionStorage.clear();
	if (indexedDB?.databases) {
		const dbs = await indexedDB.databases();
		for (const db of dbs) {
			indexedDB.deleteDatabase(db.name);
		}
	}

	// Sanitize navigator properties
	try {
		Object.defineProperty(navigator, "plugins", { get: () => [] });
		Object.defineProperty(navigator, "languages", { get: () => ["en-US"] });
		Object.defineProperty(navigator, "webdriver", { get: () => false });
	} catch (e) {
		console.warn("[PreProcess] Failed to redefine navigator props:", e);
	}

	// Fake screen info
	//   Object.defineProperty(window.screen, 'width', { get: () => 1920 });
	//   Object.defineProperty(window.screen, 'height', { get: () => 1080 });

	// Delay to simulate async actions (like purging cache via Service Worker)
	await new Promise((resolve) => setTimeout(resolve, 100));

	console.log("[PreProcess] Done.");
}
