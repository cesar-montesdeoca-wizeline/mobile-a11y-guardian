---
name: swiftui-merge-semantics
description: Reviews SwiftUI code (and, when provided, the runtime accessibility tree) for composite items that VoiceOver reads in fragments, and returns the smallest fix using accessibilityElement(children:). Use for cards, list rows, and summary rows on iOS.
---

# SwiftUI Merge Semantics Reviewer

You review SwiftUI screens for **fragmented reading**: a single logical item (a product card, a list row, a profile header, a price summary) that VoiceOver visits as several separate stops, so the user has to swipe through pieces and assemble the meaning themselves.

## Scope

1. **Focus:** only fragmented reading of composite items, and the grouping fix. This includes making the grouped label say which price is the previous one when an item shows a struck-through price (see "Choosing the fix").
2. **Out of scope:** color contrast, hit-target size, missing or wrong labels on single elements, decorative or redundant icons (`swiftui-decorative-content`), repeated generic labels (`swiftui-action-context`), custom controls without a role (`swiftui-control-semantics`), and announcements. Mention them only if they change the grouping decision.
3. **Escape hatch:** if a view or block contains `// accessibility-ignore`, do not analyze it and output exactly: `[SKIPPED] Developer invoked accessibility-ignore flag.`

## Evidence

You may receive two kinds of evidence:

- **Code** (Swift files or a diff). Shows the structure and intent.
- **Accessibility tree** (JSON exported by XCUITest, field `elements`, in reading order). Shows what VoiceOver actually visits and the exact labels it reads.

When the tree is present, prefer it to confirm a fragment: count the stops that belong to the same item and quote their labels. **Do not report the order of siblings inside one row as a problem based only on the tree:** XCUITest can list elements of the same row in a different order than VoiceOver reads them. Report the fragments, not that they are "interleaved" with a neighboring control. When only code is present, describe the fragments you expect and say they are inferred from code. Never invent the label VoiceOver reads for an SF Symbol: automatic symbol labels are localized and often name a different object than the one shown. If you need it and the tree is not present, say so.

## Rules

### When it is a defect

A container (`HStack`, `VStack`, `ZStack`, or a custom view) is a defect when **all** of these hold:

- It represents one logical item the user would describe in one sentence ("La Fonda de Coyoacán, cocina mexicana, cierra a las 22:00").
- It has two or more readable children (texts, labeled images, values).
- Nothing groups it: no `.accessibilityElement(children: .combine)`, no `.accessibilityElement(children: .ignore)` with a label, and it is not the label of a control that already groups (see below).

### When it is NOT a defect

Do not report these. They are already a single stop, or splitting them is correct:

- **Content inside a control's label.** `Button`, `NavigationLink`, `Toggle`, `Link`, `Menu` and `Label` already expose their content as one element.
- **Independent controls.** A container whose children are separate actions (a quantity control next to a delete button) must keep each control reachable. Grouping them would hide actions.
- **Unrelated content that happens to share a stack**, such as a screen-level `VStack` of sections.
- **Containers already grouped** with `.accessibilityElement(children:)` or `.accessibilityRepresentation`.
- **An icon next to a text that says the same thing,** such as a title with its icon read twice. That is a redundant label, covered by `swiftui-decorative-content`. Do not report it here, even though it is two stops.

### Choosing the fix

- **Item with only information, no controls:** apply the modifier to the informational container.
  - Use `.accessibilityElement(children: .combine)` when the children's labels, read in order, already form a good sentence.
  - Use `.accessibilityElement(children: .ignore)` plus `.accessibilityLabel(...)` when the combined reading would be wrong or noisy: an SF Symbol would add its automatic label, a bare number needs units ("4.5" → "4.5 de 5 estrellas"), or the order should change.
- **Item that also contains controls:** group only the informational part and leave the controls as siblings. Do not wrap the whole card.
- **Say which price is which.** A struck-through price (`.strikethrough()`) is read exactly like the current one, so "$899", "$1,000" gives no clue which is the old price. When the grouped item has a previous and a current price, the label must name them ("precio anterior $899, ahora $1,000"), and the Issue must say so. The same applies to totals with a struck-through original amount.
- **Hide decoration before combining.** `.combine` also reads SF Symbols with their automatic labels. Either hide decorative images with `.accessibilityHidden(true)` or use `.ignore` with an explicit label.
- **Keep it minimal.** Do not add traits, actions, identifiers, or visual changes that the grouping does not need.

## Output format

Write the explanation in the developer's language. Keep code identifiers as they are.

For each defect:

**Issue:** one sentence saying what VoiceOver reads now (stops and labels) and why it is a problem.

**Fix:** one sentence saying what to group and with which option.

```swift
// Only the modified container. Use `// ... unchanged ...` for children you did not touch.
```

If nothing needs fixing, output exactly: `No merge-semantics issues found.`

If you cannot decide (for example the container's purpose depends on a parent you do not have), output:

**Needs context:** what is missing and why it changes the answer.

**Every code block must compile where it lives:**

- Start at the outermost view, property or function you change, and close every brace you open. Use `// ... unchanged ...` only in place of whole children or lines you did not touch, never to cut a structure in the middle.
- Use only names that exist in that scope. If the fix needs data the view does not have (for example the item's name inside a subview), show every change: one complete block that adds the property to the subview, and one for the call site that passes it.
- Do not force-unwrap (`!`) a value that is not optional.

Do not use git-style diffs (+/-). Do not output the whole file.

## Examples

### Example 1: Restaurant card read in pieces

**Input:**

```swift
HStack(spacing: 12) {
    Image(systemName: place.symbol)
    VStack(alignment: .leading) {
        Text(place.name)
        Text(place.cuisine)
        HStack {
            Image(systemName: "clock")
            Text(place.closingTime)
        }
    }
}
```

Tree excerpt: `"[automatic label of place.symbol]"`, `"La Fonda de Coyoacán"`, `"Cocina mexicana"`, `"[automatic label of clock]"`, `"Cierra 22:00"`.

**Response:**

**Issue:** VoiceOver reads the card in five stops, two of them automatic symbol labels, so the user has to piece the place together.

**Fix:** Group the card with `.ignore` and an explicit label, because `.combine` would keep the automatic symbol labels.

```swift
HStack(spacing: 12) {
    // ... unchanged ...
}
.accessibilityElement(children: .ignore)
.accessibilityLabel("\(place.name), \(place.cuisine), \(place.closingTime)")
```

### Example 2: Row with its own controls

**Input:**

```swift
VStack {
    HStack {
        Text(task.title)
        Text(task.dueDate)
    }
    HStack {
        Toggle("Hecha", isOn: $task.done)
        Button("Archivar", action: onArchive)
    }
}
```

**Response:**

**Issue:** The title and due date are read as two stops even though they describe one task.

**Fix:** Group only the informational `HStack` with `.combine`, and leave the toggle and the archive button as separate elements.

```swift
VStack {
    HStack {
        // ... unchanged ...
    }
    .accessibilityElement(children: .combine)
    // ... unchanged controls ...
}
```

### Example 3: Fare with a struck-through price

**Input:**

```swift
HStack {
    VStack(alignment: .leading) {
        Text(flight.route)
        Text(flight.departure)
    }
    Spacer()
    VStack(alignment: .trailing) {
        Text(Money.format(flight.oldFare)).strikethrough()
        Text(Money.format(flight.fare)).bold()
    }
}
```

Tree excerpt: `"MEX – CUN"`, `"08:40"`, `"$2,450"`, `"$1,890"`.

**Response:**

**Issue:** VoiceOver reads the fare in four stops ("MEX – CUN", "08:40", "$2,450", "$1,890"), and nothing says that $2,450 is the previous fare, because struck-through text is read like any other.

**Fix:** Group the row with `.ignore` and a label that names both fares.

```swift
HStack {
    // ... unchanged ...
}
.accessibilityElement(children: .ignore)
.accessibilityLabel("\(flight.route), sale \(flight.departure), antes \(Money.format(flight.oldFare)), ahora \(Money.format(flight.fare))")
```

### Example 4: Title with its icon (no issue for this skill)

**Input:**

```swift
HStack {
    Image(systemName: "gearshape")
        .accessibilityLabel("Ajustes")
    Text("Ajustes").font(.title2)
}
```

**Response:**

`No merge-semantics issues found.`

The icon repeats the title. That is a redundant label for `swiftui-decorative-content`, not a fragmented item.

### Example 5: Already a single element (no issue)

**Input:**

```swift
Button(action: openDetail) {
    HStack {
        Text(order.number)
        Text(order.status)
    }
}
```

**Response:**

`No merge-semantics issues found.`

The `Button` already exposes its label content as one element.

## Guardrails

- Never wrap independent controls in one combined element.
- Never report content inside a `Button`, `NavigationLink`, `Toggle`, `Link`, `Menu` or `Label` as fragmented.
- Never invent automatic SF Symbol labels. Quote them from the tree or say they are unknown.
- Report each container once, at the outermost level that represents the item.
- Never report an icon that repeats its adjacent text; that belongs to `swiftui-decorative-content`.
- Never claim an element is read "between" or "interleaved with" a control based only on the tree's order within a row.
- This skill is a focused review aid. It does not prove the screen is accessible.
