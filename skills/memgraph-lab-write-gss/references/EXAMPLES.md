# GSS Examples

Real-world Graph Style Script patterns and recipes.

## Basic node labels

Show node name as label, with label-per-label-type formatting:

```
@NodeStyle HasLabel(node, "Country") {
  label: Property(node, "name")
}

@NodeStyle HasLabel(node, "City") {
  label: Format("{}, {}",
                Property(node, "name"),
                Property(node, "country"))
}
```

## Show all labels as a joined string

```
@NodeStyle Greater(Size(Labels(node)), 0) {
  label: Format(":{}", Join(Labels(node), " :"))
}
```

## Basic edge labels

Show the relationship type as the edge label:

```
@EdgeStyle {
  label: Type(edge)
}
```

## Conditional node styling with predicates

Style nodes differently based on labels:

```
@NodeStyle HasLabel(node, "Country") {
  color: #ffd700
  color-hover: #ffa500
  color-selected: #dd2222
  size: 35
}

@NodeStyle HasLabel(node, "City") {
  color: dodgerblue
  size: 25
}
```

Compound conditions:

```
@NodeStyle And(HasLabel(node, "City"),
               Less(Property(node, "drinks_USD"), 5)) {
  size: 50
  shadow-color: red
  shadow-size: 10
  color: limegreen
}
```

## Specific node override (cascade)

Place more specific rules after general ones. Later directives win:

```
@NodeStyle HasLabel(node, "Country") {
  image-url: Format("https://cdn.countryflags.com/thumbs/{}/flag-800.png",
                    LowerCase(Property(node, "name")))
}

@NodeStyle Equals(Property(node, "name"), "England") {
  image-url: "https://upload.wikimedia.org/wikipedia/en/thumb/b/be/Flag_of_England.svg/2560px-Flag_of_England.svg.png"
}

@NodeStyle Equals(Property(node, "name"), "Scotland") {
  image-url: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Flag_of_Scotland.svg/1200px-Flag_of_Scotland.svg.png"
}
```

## Node with property-based label and conditional color

```
@NodeStyle HasProperty(node, "name") {
  label: AsText(Property(node, "name"))
}

@NodeStyle And(HasProperty(node, "name"),
               Equals(Property(node, "name"), "Tony Stark")) {
  color: gold
  shadow-color: red
  label: "You know who I am"
}
```

## Node images from properties

Use a node property as the image URL:

```
@NodeStyle HasProperty(node, "profile_image") {
  image-url: Property(node, "profile_image")
}
```

Or use base64-encoded images inline:

```
@NodeStyle {
  image-url: "data:image/png;base64,iVBOR..."
}
```

## Edge styling by relationship type

```
@EdgeStyle Equals(Type(edge), "FRIENDS_WITH") {
  color: dodgerblue
  width: 2
  label: "friends"
}

@EdgeStyle Equals(Type(edge), "WORKS_AT") {
  color: coral
  width: 3
  label: Type(edge)
  arrow-size: 10
}
```

## Thin edges with no arrows

```
@EdgeStyle {
  width: 1
  arrow-size: 0
  color: #6AA84F
  label: Type(edge)
}
```

## Shadow and hover effects

```
@NodeStyle {
  size: 35
  border-width: 5
  border-color: white
  shadow-color: #333333
  shadow-size: 20
  color: #dd2222
  color-hover: Darker(#dd2222)
}
```

## Node shapes

```
@NodeStyle HasLabel(node, "Alert") {
  shape: "triangle"
  color: red
}

@NodeStyle HasLabel(node, "Server") {
  shape: "square"
  color: steelblue
}

@NodeStyle HasLabel(node, "Star") {
  shape: "star"
  color: gold
}
```

## Custom function: simple utility

```
Define(square, Function(x, Mul(x, x)))

@NodeStyle {
  size: square(Property(node, "rank"))
}
```

## Custom function: recursive power

```
Define(pow, Function(x, n,
  If(Equals(n, 1), x, Mul(x, pow(x, Sub(n, 1))))
))

@NodeStyle {
  size: pow(Property(node, "level"), 2)
}
```

## Higher-order functions: Map, Filter, Reduce

Extract and filter property values across nodes:

```
Define(GetProps, Function(nodes, prop,
  Map(nodes, Function(n, Property(n, prop)))
))

Define(KeepNumbers, Function(vals,
  Filter(vals, Function(v, IsNumber(v)))
))

Define(allAges, KeepNumbers(GetProps(Nodes(graph), "age")))
```

Reduce to compute a sum:

```
Define(totalAge, Reduce(
  allAges,
  Function(prev, current, Add(prev, current)),
  0
))
```

## Value normalization with global caching

Cache expensive computations in the global scope so they run once,
not per-node:

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
  color: white
  size: NORM
  label: Format("Age: {}", AsText(Property(node, PROP)))
}
```

The `Define(NORM, ...)` inside `@NodeStyle` creates a local variable to
avoid calling `Normalize` twice per node.

## Dynamic color from property value

Use `If` chains or computed colors:

```
@NodeStyle {
  color: If(Greater(Property(node, "risk"), 80), red,
         If(Greater(Property(node, "risk"), 50), orange,
            green))
}
```

Or compute color dynamically:

```
@NodeStyle {
  color: HSL(
    Mul(Div(Property(node, "score"), 100), 120),
    80,
    50
  )
}
```

## Size by edge count (degree)

```
@NodeStyle {
  size: Add(10, Mul(Size(Edges(node)), 3))
}
```

## Edge label with start/end node info

```
@EdgeStyle {
  label: Format("{} -> {}",
    Property(StartNode(edge), "name"),
    Property(EndNode(edge), "name"))
}
```

## Tree view with auto-detection

```
@ViewStyle IsTreeStructure(graph) {
  view: "tree"
  tree-orientation: "horizontal"
  tree-node-gap: 50
  tree-level-gap: 100
}
```

## Map view

Requires nodes with `latitude` and `longitude` properties:

```
@ViewStyle {
  view: "map"
  map-tile-layer: "detailed"
}
```

## Force layout tuning

```
@ViewStyle {
  view: "force"
  force-collision-radius: 20
  force-repel-force: -200
  force-link-distance: 50
  force-physics-enabled: True
}

@ViewStyle Greater(NodeCount(graph), 100) {
  force-physics-enabled: False
}
```

## Dark background canvas

```
@ViewStyle {
  background-color: #1a1a2e
}

@NodeStyle {
  color: #e94560
  font-color: white
  border-color: #533483
  border-width: 2
}

@EdgeStyle {
  color: #533483
  font-color: #e94560
}
```

## Complete example: Europe backpacking dataset

```
@NodeStyle {
  size: 35
  border-width: 5
  border-color: #ffffff
  shadow-color: #333333
  shadow-size: 20
}

@NodeStyle Greater(Size(Labels(node)), 0) {
  label: Format(":{}", Join(Labels(node), " :"))
}

@NodeStyle HasLabel(node, "Country") {
  color: #ffd700
  color-hover: #ffa500
  color-selected: #dd2222
}

@NodeStyle HasProperty(node, "name") {
  label: AsText(Property(node, "name"))
}

@EdgeStyle {
  width: 1
  label: Type(edge)
  arrow-size: 0
  color: #6AA84F
}

@NodeStyle Equals(Property(node, "name"), "Russia") {
  image-url: "https://upload.wikimedia.org/wikipedia/en/thumb/f/f3/Flag_of_Russia.svg/320px-Flag_of_Russia.svg.png"
}

@NodeStyle Equals(Property(node, "name"), "Spain") {
  image-url: "https://upload.wikimedia.org/wikipedia/en/thumb/9/9a/Flag_of_Spain.svg/320px-Flag_of_Spain.svg.png"
}
```
