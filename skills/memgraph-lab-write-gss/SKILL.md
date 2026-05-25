---
name: memgraph-lab-write-gss
description: >-
  Write and edit Graph Style Script (GSS) code for Memgraph Lab graph
  visualization. Use when the user asks to style graphs, change node or edge
  colors, add labels, set images, configure graph layouts, or write any GSS /
  Graph Style Script code for Memgraph Lab.
compatibility: Memgraph Lab required.
metadata:
  version: "0.0.1"
  author: memgraph
---

# Writing Graph Style Script (GSS)

GSS is Memgraph's language for customizing graph visualization in Memgraph Lab.
A GSS file is a sequence of **expressions** and **directives**.

## Language basics

### Value types

`Boolean`, `Color`, `Number`, `String`, `Array`, `Map`, `Function`, `Null`

### Expressions

Three forms:

1. **Literals** -- strings `"Hello"`, numbers `42` / `3.14`, colors `#ff0000`,
   booleans `True` / `False`, `Null`
2. **Name expressions** -- identifiers bound via `Define`; all CSS/X11 color
   names are built-in (e.g. `dodgerblue`, `gold`, `red`)
3. **Function calls** -- `FunctionName(arg1, arg2, ...)`

Name rules: starts with a letter, may contain digits, `-`, `_`.

Strings support `\` escaping for `"` and newlines.

### Truthy / Falsy

Six falsy values: `False`, `0`, `""`, `Null`, `[]` (empty array), `{}` (empty map).
Everything else is truthy.

### Short-circuit evaluation

`If`, `And`, `Or` skip branches that are not needed.
`Function()` does not evaluate argument names or body until call time.

## Directives

Directives are CSS-like blocks that set visual properties.

```
@<DirectiveName> <optional predicate> {
  <property-name>: <expression>
  ...
}
```

- Later directives **override** earlier ones (cascade, like CSS).
- Properties are `name: expression` pairs separated by newlines.
- The predicate is an optional boolean expression that filters which
  elements the directive applies to.

### Available directives

| Directive | Styles | Binds variable |
|-----------|--------|----------------|
| `@NodeStyle` | Graph nodes | `node` |
| `@EdgeStyle` | Graph relationships | `edge` |
| `@ViewStyle` | Canvas / layout | `graph` |

`@ViewStyle.Map` is **deprecated** since Lab 3.4 -- use `@ViewStyle` with
`map-tile-layer` instead.

### Scope variables

| Variable | Available in | Type |
|----------|-------------|------|
| `node` | `@NodeStyle` only | Map (properties, labels, id) |
| `edge` | `@EdgeStyle` only | Map (properties, type, start, end, id) |
| `graph` | Everywhere (global + all directives) | Graph |

Using `node` outside `@NodeStyle` or `edge` outside `@EdgeStyle` causes a
**compile error**.

## File structure and execution order

1. **Global context**: all expressions outside directives run first. Use for
   `Define` calls and cached computations. `graph` is available here.
2. **`@NodeStyle`**: evaluated per node.
3. **`@EdgeStyle`**: evaluated per relationship.

Global names are visible inside directives. `Define` inside a directive creates
a **local** variable (useful for per-element caching).

```
Define(EDGE_COUNT, EdgeCount(graph))

@NodeStyle {
  size: Sqrt(NodeCount(graph))
}

@EdgeStyle {
  width: If(Greater(EDGE_COUNT, 1000), 1, 2)
}
```

## `@NodeStyle` properties

| Property | Type | Notes |
|----------|------|-------|
| `border-color` | Color | |
| `border-color-hover` | Color | |
| `border-color-selected` | Color | |
| `border-width` | Number | px |
| `border-width-selected` | Number | px |
| `color` | Color | Background fill |
| `color-hover` | Color | |
| `color-selected` | Color | |
| `font-background-color` | Color | Label background |
| `font-color` | Color | Label text |
| `font-family` | String | e.g. `"sans-serif"` |
| `font-size` | Number | px |
| `image-url` | String | PNG/JPEG/GIF(static)/WEBP/base64; overrides `color` |
| `image-url-selected` | String | |
| `label` | String | Text below node |
| `shadow-color` | Color | |
| `shadow-size` | Number | Blur radius (0 = solid) |
| `shadow-offset-x` | Number | |
| `shadow-offset-y` | Number | |
| `shape` | String | `"dot"` (default), `"square"`, `"diamond"`, `"triangle"`, `"triangleDown"`, `"star"` |
| `size` | Number | Node radius in px |
| `z-index` | Number | Stack order |

## `@EdgeStyle` properties

| Property | Type | Notes |
|----------|------|-------|
| `arrow-size` | Number | 0 = no arrow |
| `color` | Color | Line color |
| `color-hover` | Color | |
| `color-selected` | Color | |
| `font-background-color` | Color | |
| `font-color` | Color | |
| `font-family` | String | |
| `font-size` | Number | |
| `label` | String | |
| `shadow-color` | Color | |
| `shadow-size` | Number | |
| `shadow-offset-x` | Number | |
| `shadow-offset-y` | Number | |
| `width` | Number | Line width in px |
| `width-hover` | Number | |
| `width-selected` | Number | |
| `z-index` | Number | |

## `@ViewStyle` properties

| Property | Type | Default |
|----------|------|---------|
| `background-color` | Color | |
| `view` | String | `"default"` -- also `"map"`, `"force"`, `"tree"` |
| `force-collision-radius` | Number | 15 |
| `force-repel-force` | Number | -100 |
| `force-link-distance` | Number | 30 |
| `force-physics-enabled` | Boolean | |
| `tree-orientation` | String | `"vertical"` or `"horizontal"` |
| `tree-node-gap` | Number | |
| `tree-level-gap` | Number | |
| `map-tile-layer` | String | `"detailed"`, `"light"`, `"dark"`, `"basic"`, `"satellite"` |

Map view requires nodes with `latitude` and `longitude` properties.

## Custom functions

Use `Define` + `Function` to create reusable logic:

```
Define(square, Function(x, Mul(x, x)))
square(5)  // -> 25

Define(pow, Function(x, n,
  If(Equals(n, 1), x, Mul(x, pow(x, Sub(n, 1))))
))
pow(2, 10)  // -> 1024
```

Lambdas for higher-order functions:

```
Filter(AsArray(1, 2, 3, 4), Function(item, Greater(item, 2)))
// -> [3, 4]
```

Use `Execute` to run side-effect expressions and return the last value:

```
Execute(
  Set(map, "key1", "value1"),
  Set(map, "key2", "value2"),
  MapKeys(map)
)
```

## Colors

Three ways to specify a color:

1. **Named** -- any X11/CSS color name: `red`, `dodgerblue`, `gold`, etc.
2. **Hex literal** -- `#FF0000`, `#1E90FF`
3. **Functions** -- `RGB(r, g, b)`, `RGBA(r, g, b, a)`, `HSL(h, s, l)`,
   `HSLA(h, s, l, a)`, `Darker(color)`, `Lighter(color)`, `Mix(c1, c2)`

## Common patterns

### Label from node property

```
@NodeStyle {
  label: Property(node, "name")
}
```

### Conditional styling with predicates

```
@NodeStyle HasLabel(node, "Person") {
  color: dodgerblue
  size: 40
}

@NodeStyle And(HasLabel(node, "Person"), Greater(Property(node, "age"), 30)) {
  color: coral
}
```

### Image on nodes

```
@NodeStyle HasLabel(node, "Country") {
  image-url: Format("https://flagcdn.com/w320/{}.png",
                    LowerCase(Property(node, "code")))
}
```

### Override cascade (general then specific)

```
@NodeStyle {
  color: lightgray
  size: 20
}

@NodeStyle Equals(Property(node, "name"), "Special") {
  color: gold
  size: 50
}
```

### Normalization with caching

```
Define(MIN_SIZE, 5)
Define(MAX_SIZE, 20)
Define(PROP, "age")
Define(SIZE_RANGE, Sub(MAX_SIZE, MIN_SIZE))

Define(GetProps, Function(nodes, prop,
  Map(nodes, Function(n, Property(n, prop)))
))
Define(KeepNumbers, Function(vals,
  Filter(vals, Function(v, IsNumber(v)))
))

Define(MAX_VAL, If(Greater(NodeCount(graph), 0),
  Max(KeepNumbers(GetProps(Nodes(graph), PROP))), 0))
Define(MIN_VAL, If(Greater(NodeCount(graph), 0),
  Min(KeepNumbers(GetProps(Nodes(graph), PROP))), 0))

Define(Normalize, Function(n,
  Add(MIN_SIZE, Mul(SIZE_RANGE,
    Div(Sub(Property(n, PROP), MIN_VAL), Sub(MAX_VAL, MIN_VAL))
  ))
))

@NodeStyle And(HasLabel(node, "Person"), IsNumber(Property(node, PROP))) {
  Define(NORM, Normalize(node))
  size: NORM
  label: Format("Age: {}", AsText(Property(node, PROP)))
}
```

### Tree view auto-detection

```
@ViewStyle IsTreeStructure(graph) {
  view: "tree"
}
```

### Edge styling by relationship type

```
@EdgeStyle Equals(Type(edge), "FRIENDS_WITH") {
  color: dodgerblue
  width: 2
  label: Type(edge)
}
```

## Validation

If the `validate-gss` tool is available, always run it after writing or
modifying GSS to catch syntax errors before applying the style in Memgraph Lab.

## Preview

If the `evaluate-gss` tool is available, run it after validation to see how
styles resolve against actual graph data. Pass custom nodes and relationships
to the tool and inspect the computed style properties (color, size, label, etc.)
for each node and edge. This catches logic errors that syntax validation
cannot - such as a `Property` call on a missing key, overlapping predicates
where the wrong rule wins, or a `Format` expression producing unexpected text.

## Additional resources

- For the complete built-in function reference (90+ functions), see
  [REFERENCE.md](references/REFERENCE.md)
- For more real-world GSS examples and patterns, see [EXAMPLES.md](references/EXAMPLES.md)
