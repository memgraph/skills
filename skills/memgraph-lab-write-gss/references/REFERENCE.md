# GSS Built-in Function Reference

Complete catalog of all built-in functions in Graph Style Script.

## Color functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `Darker` | `(color: Color)` | Color | Darker version of the color |
| `Lighter` | `(color: Color)` | Color | Lighter version of the color |
| `Mix` | `(color1: Color, color2: Color)` | Color | Linear interpolation of two colors |
| `Red` | `(color: Color)` | Number (0-255) | Red component |
| `Green` | `(color: Color)` | Number (0-255) | Green component |
| `Blue` | `(color: Color)` | Number (0-255) | Blue component |
| `Alpha` | `(color: Color)` | Number (0-1) | Alpha (transparency) component |
| `RGB` | `(red, green, blue: Number)` | Color | Create color from RGB |
| `RGBA` | `(red, green, blue, alpha: Number)` | Color | Create color from RGBA |
| `Hue` | `(color: Color)` | Number (0-359) | HSL hue component |
| `Saturation` | `(color: Color)` | Number (0-100) | HSL saturation component |
| `Lightness` | `(color: Color)` | Number (0-100) | HSL lightness component |
| `HSL` | `(hue, saturation, lightness: Number)` | Color | Create color from HSL |
| `HSLA` | `(hue, saturation, lightness, alpha: Number)` | Color | Create color from HSLA |

## Conditional functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `And` | `(value1, value2, ...valueN: Any)` | Boolean | True if all values truthy; short-circuits |
| `Or` | `(value1, value2, ...valueN: Any)` | Boolean | True if any value truthy; short-circuits |
| `Not` | `(value: Any)` | Boolean | Negation (truthy becomes false) |
| `Equals` | `(value1, value2: Any)` | Boolean | Equality check (by value for primitives, by identity for nodes/edges) |
| `Greater` | `(value1, value2: Number)` | Boolean | value1 > value2 |
| `Less` | `(value1, value2: Number)` | Boolean | value1 < value2 |
| `If` | `(condition, then, else: Any)` | Any | Conditional; returns `then` if truthy, `else` otherwise |

## Graph functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `HasLabel` | `(node: Node, label: String)` | Boolean | True if node has the label |
| `HasProperty` | `(nodeOrEdge: Node\|Rel, name: String)` | Boolean | True if entity has property |
| `Property` | `(nodeOrEdge: Node\|Rel, name: String)` | Any | Get property value |
| `Labels` | `(node: Node)` | List[String] | All labels of a node |
| `Type` | `(edge: Rel)` | String | Relationship type |
| `Id` | `(nodeOrEdge: Node\|Rel)` | Number | Internal ID |
| `Identity` | `(nodeOrEdge: Node\|Rel)` | Number | Same as `Id` |
| `InEdges` | `(node: Node)` | List[Rel] | Inbound relationships |
| `OutEdges` | `(node: Node)` | List[Rel] | Outbound relationships |
| `Edges` | `(graphOrNode: Graph\|Node)` | List[Rel] | All relationships (of graph or node) |
| `InNodes` | `(node: Node)` | List[Node] | Unique inbound neighbor nodes |
| `OutNodes` | `(node: Node)` | List[Node] | Unique outbound neighbor nodes |
| `Nodes` | `(graphOrEdge: Graph\|Rel)` | List[Node] | All nodes (of graph) or start+end nodes (of edge) |
| `AdjacentNodes` | `(node: Node)` | List[Node] | All directly connected nodes |
| `StartNode` | `(edge: Rel)` | Node | Source node of relationship |
| `EndNode` | `(edge: Rel)` | Node | Target node of relationship |
| `NodeCount` | `(graph: Graph)` | Number | Total node count |
| `EdgeCount` | `(graph: Graph)` | Number | Total relationship count |
| `IsTreeStructure` | `(graph: Graph, minDepth?: Number)` | Boolean | True if graph is a directed tree (default min depth: 2) |

## Map functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `MapKeys` | `(map: Map)` | List[String] | Array of all map keys |
| `MapValues` | `(map: Map)` | List[Any] | Array of all map values |

See also: `AsMap`, `IsMap`, `Get`, `Set`, `Del` in Utility and Type sections.

## Math functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `Add` | `(value1, value2, ...valueN: Number)` | Number | Sum of values |
| `Sub` | `(value1, value2: Number)` | Number | value1 - value2 |
| `Mul` | `(value1, value2, ...valueN: Number)` | Number | Product of values |
| `Div` | `(value1, value2: Number)` | Number | value1 / value2 |
| `Sqrt` | `(value: Number)` | Number | Square root |
| `Exp` | `(value: Number)` | Number | e^value |
| `Log` | `(value: Number)` | Number | Natural logarithm |
| `Log10` | `(value: Number)` | Number | Base-10 logarithm |
| `Floor` | `(value: Number)` | Number | Round down |
| `Ceil` | `(value: Number)` | Number | Round up |
| `Round` | `(value: Number)` | Number | Round to nearest integer |
| `Random` | `()` | Number | Random float in [0, 1) |
| `RandomInt` | `(bound: Number)` | Number | Random integer in [0, bound) |
| `Sum` | `(array: List[Number])` | Number | Sum of array (0 for empty) |
| `Avg` | `(array: List[Number])` | Number | Average of array |
| `Min` | `(array: List[Number])` | Number | Minimum of array |
| `Max` | `(array: List[Number])` | Number | Maximum of array |

## Text functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `Concat` | `(v1, v2, ...vN: String\|List)` | String\|List | Concatenate strings or arrays |
| `Slice` | `(value: String\|List, start: Number, end?: Number)` | String\|List | Substring/subarray; supports negative indexes |
| `Split` | `(text, delimiter: String)` | List[String] | Split string by delimiter |
| `Format` | `(fmt: String, v1, ...vN: Any)` | String | Substitute `{}` placeholders with values (text inside braces ignored) |
| `Matches` | `(text, regex: String)` | Boolean | Regex test (JS `RegExp.test`) |
| `Replace` | `(text, regex, replacement: String)` | String | Replace first regex match |
| `LowerCase` | `(text: String)` | String | To lower case |
| `UpperCase` | `(text: String)` | String | To upper case |
| `Trim` | `(text: String)` | String | Strip leading/trailing whitespace |

## Array functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `Join` | `(array: List, delimiter: String)` | String | Join elements into string |
| `Contains` | `(array: List, value: Any)` | Boolean | True if array contains value |
| `RandomOf` | `(array: List)` | Any\|Null | Random element |
| `Find` | `(array: List, fn: Function)` | Any\|Null | First element where fn returns truthy |
| `Filter` | `(array: List, fn: Function)` | List | Elements where fn returns truthy |
| `Map` | `(array: List, fn: Function)` | List | Transform each element |
| `Reduce` | `(array: List, fn: Function, init: Any)` | Any | Fold array; fn receives (prev, current) |
| `All` | `(array: List, fn: Function)` | Boolean | True if fn truthy for all elements |
| `Any` | `(array: List, fn: Function)` | Boolean | True if fn truthy for any element |
| `Uniq` | `(array: List)` | List | Remove duplicates (preserves order) |
| `Reverse` | `(array: List)` | List | Reverse order |
| `Sort` | `(array: List[String\|Number\|Boolean])` | List | Sort primitives |
| `Next` | `(iterator: Iterator)` | Any\|Null | Next item from iterator |

## Type functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `AsArray` | `(v1, v2, ...vN: Any)` | List | Create array; also converts Iterator back to array |
| `AsMap` | `(k1, v1, ...kN, vN: Any)` | Map | Create map from key-value pairs (keys must be strings) |
| `AsIterator` | `(array: List)` | Iterator | Create iterator from array |
| `AsNumber` | `(value: String\|Number\|Boolean)` | Number | Parse to number (`True`->1, `False`->0) |
| `AsText` | `(value: Any)` | String | Convert to string |
| `TypeOf` | `(value: Any)` | String | Type name: `"number"`, `"boolean"`, `"string"`, `"Null"`, `"Color"`, `"Node"`, `"Edge"`, `"Graph"`, `"List"`, `"Iterator"`, `"Map"`, `"Function"` |
| `IsArray` | `(value: Any)` | Boolean | Type check |
| `IsMap` | `(value: Any)` | Boolean | Type check |
| `IsIterator` | `(value: Any)` | Boolean | Type check |
| `IsNumber` | `(value: Any)` | Boolean | Type check |
| `IsBoolean` | `(value: Any)` | Boolean | Type check |
| `IsString` | `(value: Any)` | Boolean | Type check |
| `IsNull` | `(value: Any)` | Boolean | Type check |

## Utility functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `Define` | `(name: Variable, value: Any)` | -- | Bind value to name; global outside directives, local inside |
| `Function` | `(arg1, ...argN, body: Any)` | Function | Create a function; args are not evaluated at definition time |
| `Execute` | `(expr1, ...exprN: Any)` | Any | Run all expressions, return last value |
| `Get` | `(obj: List\|Map\|String\|Node\|Rel, key, default?: Any)` | Any | Get element by index/key; returns default or Null on miss |
| `Set` | `(obj: List\|Map, key, value: Any)` | Any\|Null | Set element; returns value on success, Null on out of bounds |
| `Del` | `(map: Map, key: String)` | Any\|Null | Remove key from map; returns removed value |
| `Size` | `(value: List\|Map\|String\|Node\|Rel\|Graph)` | Number | Length / count |
| `Coalesce` | `(v1, ...vN: Any)` | Any\|Null | First non-null value |

## Named colors

All X11/CSS SVG color names are available as identifiers. Common examples:

`red`, `blue`, `green`, `yellow`, `orange`, `purple`, `pink`, `cyan`,
`magenta`, `white`, `black`, `gray`, `grey`, `gold`, `silver`, `coral`,
`crimson`, `tomato`, `salmon`, `chocolate`, `maroon`, `navy`, `teal`,
`olive`, `lime`, `aqua`, `fuchsia`, `indigo`, `violet`, `turquoise`,
`dodgerblue`, `forestgreen`, `firebrick`, `steelblue`, `slategray`,
`darkblue`, `darkgreen`, `darkred`, `darkcyan`, `darkorange`,
`darkviolet`, `deeppink`, `deepskyblue`, `lightblue`, `lightgreen`,
`lightcoral`, `lightgray`, `lightyellow`, `mediumseagreen`,
`mediumslateblue`, `midnightblue`, `royalblue`, `saddlebrown`,
`springgreen`, `yellowgreen`, `aliceblue`, `antiquewhite`, `azure`,
`beige`, `bisque`, `cornflowerblue`, `gainsboro`, `honeydew`, `ivory`,
`khaki`, `lavender`, `linen`, `mintcream`, `mistyrose`, `moccasin`,
`oldlace`, `papayawhip`, `peachpuff`, `plum`, `powderblue`, `seashell`,
`snow`, `tan`, `thistle`, `wheat`, `whitesmoke`

For the full list, see the [W3C CSS Color 3 specification](https://www.w3.org/TR/css-color-3/#svg-color).
