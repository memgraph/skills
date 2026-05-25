# Cypher Built-in Function Reference (Memgraph)

## Scalar functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `id` | `(Node\|Rel) -> integer` | Persisted internal ID |
| `type` | `(Rel) -> string` | Relationship type |
| `labels` | `(Node) -> List[string]` | Node labels |
| `properties` | `(Node\|Rel) -> Map` | All properties as map |
| `propertySize` | `(entity, propName) -> integer` | RAM bytes for property |
| `keys` | `(Map\|Node\|Rel) -> List` | Property keys |
| `values` | `(Map\|Node\|Rel) -> List` | Property values |
| `coalesce` | `(expr, ...) -> any` | First non-null |
| `head` | `(List) -> any` | First element |
| `last` | `(List) -> any` | Last element |
| `tail` | `(List) -> List` | All except first |
| `size` | `(List\|string\|Map\|Path) -> integer` | Length/count |
| `length` | `(List\|string\|Map\|Path) -> integer` | Same as size |
| `degree` | `(Node) -> integer` | Total degree |
| `inDegree` | `(Node) -> integer` | Inbound degree |
| `outDegree` | `(Node) -> integer` | Outbound degree |
| `startNode` | `(Rel) -> Node` | Source node |
| `endNode` | `(Rel) -> Node` | Target node |
| `nodes` | `(Path) -> List[Node]` | Nodes in path |
| `relationships` | `(Path) -> List[Rel]` | Rels in path |
| `counter` | `(name, initial, incr?) -> integer` | Per-query unique counter |
| `randomUUID` | `() -> string` | UUID v4 |
| `timestamp` | `() -> integer` | Microseconds since epoch |
| `valueType` | `(any) -> string` | Type name as string |
| `assert` | `(bool, msg?) -> void` | Raises if false |

## Conversion functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `toBoolean` | `(bool\|int\|string) -> boolean` | |
| `toFloat` | `(number\|string) -> float` | |
| `toInteger` | `(bool\|number\|string) -> integer` | |
| `toString` | `(any) -> string` | Errors on unstringifiable |
| `toStringOrNull` | `(any) -> string\|null` | Null on failure |
| `toBooleanList` | `(List) -> List[boolean]` | |
| `toFloatList` | `(List) -> List[float]` | |
| `toIntegerList` | `(List) -> List[integer]` | |
| `toSet` | `(List) -> List` | Remove duplicates |

## String functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `toLower` | `(string) -> string` | Lower case |
| `toUpper` | `(string) -> string` | Upper case |
| `trim` | `(string) -> string` | Strip whitespace |
| `lTrim` | `(string) -> string` | Strip leading |
| `rTrim` | `(string) -> string` | Strip trailing |
| `replace` | `(original, search, replacement) -> string` | |
| `reverse` | `(string) -> string` | |
| `split` | `(string, delimiter) -> List[string]` | |
| `substring` | `(string, start, length?) -> string` | |
| `left` | `(string, length) -> string` | |
| `right` | `(string, length) -> string` | |
| `contains` | `(string, substring) -> boolean` | Also: `a CONTAINS b` |
| `startsWith` | `(string, prefix) -> boolean` | Also: `a STARTS WITH b` |
| `endsWith` | `(string, suffix) -> boolean` | Also: `a ENDS WITH b` |

## Math functions

| Function | Returns | Notes |
|----------|---------|-------|
| `abs(x)` | number | Absolute value |
| `ceil(x)` | integer | Round up |
| `floor(x)` | integer | Round down |
| `round(x)` | integer | Commercial rounding |
| `sign(x)` | integer | -1, 0, or 1 |
| `sqrt(x)` | float | |
| `exp(x)` | float | e^x |
| `log(x)` | float | Natural log |
| `log10(x)` | float | Base-10 log |
| `rand()` | float | [0, 1) |
| `e()` | float | Euler's number |
| `pi()` | float | Pi |
| `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2` | float | Trig |

## Aggregation functions

| Function | Returns | Notes |
|----------|---------|-------|
| `count(expr)` | integer | Non-null count; `count(*)` for all rows |
| `sum(expr)` | number | |
| `avg(expr)` | float | |
| `min(expr)` | any | Supports temporal types |
| `max(expr)` | any | Supports temporal types |
| `collect(expr)` | List | Collect into list |
| `collect(key, value)` | Map | Collect into map (keys must be strings) |

All aggregations support `DISTINCT`.

## List functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `range` | `(start, end, step?) -> List[integer]` | |
| `reduce` | `(acc = init, var IN list \| expr) -> any` | |
| `extract` | `(var IN list \| expr) -> List` | |
| `all` | `(var IN list WHERE pred) -> boolean` | |
| `any` | `(var IN list WHERE pred) -> boolean` | |
| `none` | `(var IN list WHERE pred) -> boolean` | |
| `single` | `(var IN list WHERE pred) -> boolean` | |
| `uniformSample` | `(list, size) -> List` | Random sample |

## Temporal functions

| Function | Constructor |
|----------|-------------|
| `duration` | `duration("P2DT3H")` or `duration({hour: 3})` |
| `date` | `date("2024-01-15")` or `date({year: 2024, month: 1, day: 15})` |
| `localTime` | `localTime("14:30:00")` or `localTime({hour: 14, minute: 30})` |
| `localDateTime` | `localDateTime("2024-01-15T14:30:00")` |
| `datetime` | `datetime("2024-01-15T14:30:00Z")` or `datetime({year:2024, timezone:"UTC"})` |

Temporal arithmetic: Date +/- Duration = Date, DateTime - DateTime = Duration, etc.

## Spatial functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `point` | `({x, y, [z], [crs\|srid]}) -> Point` | WGS-84 or Cartesian |
| `point.distance` | `(Point, Point) -> float` | Meters for WGS-84 |
| `point.withinbbox` | `(Point, lowerLeft, upperRight) -> boolean` | |

## Graph projection

| Function | Signature |
|----------|-----------|
| `project` | `(path) -> {nodes, edges}` |
| `project` | `(List[Node], List[Rel]) -> {nodes, edges}` |

## Auth functions

| Function | Returns |
|----------|---------|
| `username()` | Current user (null if unauth) |
| `roles(db?)` | List of roles |

## Enum

| Function | Signature |
|----------|-----------|
| `ToEnum` | `("EnumName::Value") -> Enum` |
| `ToEnum` | `("EnumName", "Value") -> Enum` |

## Discovery

```cypher
CALL mg.functions() YIELD *;
CALL mg.procedures() YIELD name, signature;
```
