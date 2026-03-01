# Text Search

### Query the text index

Search a specific property (replace `entitySearch` with your index name and `<value>` with the search term):

```cypher
CALL text_search.search('entitySearch', 'data.title:<value>')
YIELD node, score
RETURN node.title AS title, score
ORDER BY score DESC LIMIT 10;
```

Search across **all** indexed properties (no property prefix needed):

```cypher
CALL text_search.search_all('entitySearch', '<value>')
YIELD node, score
RETURN node.title AS title, score
ORDER BY score DESC LIMIT 10;
```

Use **boolean expressions** to combine conditions:

```cypher
CALL text_search.search('entitySearch', '(data.title:<term1> OR data.title:<term2>) AND data.description:<term3>')
YIELD node, score
RETURN node.title AS title, score
ORDER BY score DESC LIMIT 10;
```

Use **regex search** to match patterns across all properties:

```cypher
CALL text_search.regex_search('entitySearch', '<pattern>.*')
YIELD node, score
RETURN node.title AS title, score
ORDER BY score DESC LIMIT 10;
```

### Notes

- Text indices are powered by the [Tantivy](https://github.com/quickwit-oss/tantivy) full-text search engine.
- Only properties of type `String`, `Integer`, `Float`, or `Boolean` are indexed.
- Changes made within the same transaction are **not** visible to the index — commit first.
- When referencing property names in search queries, always use the `data.` prefix (e.g., `data.title`).
- To drop an index: `DROP TEXT INDEX entitySearch;`

Run the `CREATE TEXT INDEX` command before attempting any text search queries on
the graph.