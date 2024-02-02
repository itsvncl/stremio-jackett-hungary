import Database from "better-sqlite3";

export async function searchCache(title, category) {
	try {
		const db = new Database("./data/cache.db");
		const query = `SELECT * FROM ${category} WHERE title LIKE '%${title}%' COLLATE NOCASE`;
		const results = await new Promise((resolve, reject) => {
			try {
				const rows = db.prepare(query).all();
				resolve(rows);
			} catch (err) {
				reject(err);
			}
		});
		db.close();
		return results;
	} catch (err) {
		console.log("No cache");
		return [];
	}
}
