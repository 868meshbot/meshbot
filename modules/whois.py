import sqlite3


class Whois:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def search_nodes(self, search_pattern):
        query = "SELECT * FROM nodes WHERE node_id LIKE ?"
        self.cursor.execute(query, ("%" + search_pattern + "%",))
        return self.cursor.fetchone()

    def search_nodes_sn(self, search_pattern):
        query = "SELECT * FROM nodes WHERE short_name LIKE ?"
        self.cursor.execute(query, ("%" + search_pattern + "%",))
        return self.cursor.fetchone()

    def close_connection(self):
        self.conn.close()


# Example usage:
if __name__ == "__main__":
    db_file = "./db/nodes.db"
    search_pattern = input("Enter the search pattern: ")

    whois_search = Whois(db_file)
    results = whois_search.search_nodes(search_pattern)

    for row in results:
        print(row)

    whois_search.close_connection()
