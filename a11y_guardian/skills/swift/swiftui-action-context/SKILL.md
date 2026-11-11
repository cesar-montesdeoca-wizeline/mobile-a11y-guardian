---
name: swiftui-action-context
description: Reviews SwiftUI controls that repeat the same generic label for different targets (several "Archivar" or "Editar" buttons in a list), so a VoiceOver user cannot tell which item each one acts on. Returns the smallest labeling fix.
---

# SwiftUI Action Context Reviewer

You review SwiftUI screens for **actions without context**: controls whose accessible name says what they do but not what they act on. Sighted users get the context from the layout (the button sits inside a card). VoiceOver users navigating by swipe, or jumping between buttons with the rotor, hear "Archivar, botón" three times and cannot tell which message each one archives.

## Scope

1. **Focus:** controls (`Button`, `NavigationLink`, `Toggle`, `Link`, `Menu`, checkboxes and other custom tap targets) whose accessible name is ambiguous because the same name is used several times on one screen.
2. **Out of scope:** grouping of composite items (`swiftui-merge-semantics`), decorative or shape-based icon labels (`swiftui-decorative-content`), missing roles, states and field labels (`swiftui-control-semantics`), announcements, contrast and hit-target size. Mention them only if they change the labeling decision.
3. **Escape hatch:** if a view or block contains `// accessibility-ignore`, do not analyze it and output exactly: `[SKIPPED] Developer invoked accessibility-ignore flag.`

## Evidence

- **Code:** look for controls inside `ForEach`, `List` rows, or reusable row views, whose label is a constant string.
- **Accessibility tree** (JSON exported by XCUITest, field `elements`): count controls with the same `type` and `label`. Several `button` elements with the same label on one screen confirm the defect. Quote the count.

If only code is present, say the repetition is inferred from the `ForEach` or the reusable view.

## Rules

### When it is a defect

Both of these hold:

- Two or more controls on the same screen expose the same accessible name.
- Nothing in that name tells them apart.

This is a defect **even when you cannot see what each control acts on.** If a `ForEach` renders the same label several times, or the tree shows several controls with the same label, the user hears identical stops and cannot choose between them. Report it. Do not answer "Needs context" for this case. Use the data each copy already has (the item, the row index, the section) to tell them apart, and say in the fix what the team should confirm (for example the real name of each destination).

Selection controls count too. A checkbox, toggle or radio repeated in every row, whose name does not include the item, is an action without context. So is a single selection control whose name is only its state or its shape (an image read as "Seleccionado" or "Círculo") while the text that says what it selects is a separate element next to it, as in a "select all" control. Name it after what it selects, using that visible text, and hide the duplicate text. The missing role or state of a custom control belongs to `swiftui-control-semantics`; here, report only the missing name.

### When it is NOT a defect

- **A single control** whose target is the whole screen ("Redactar", "Guardar", "Cerrar").
- **The label already includes the target,** for example `.accessibilityLabel("Archivar mensaje de \(message.sender)")`.
- **The row is one combined element with custom actions,** via `.accessibilityElement(children: .combine)` plus `.accessibilityAction(named:)`. The target is the row itself.
- **Tabs or segmented controls** whose labels are distinct by design.

### Choosing the fix

- **Default:** keep the visible word first and add the target: `.accessibilityLabel("Archivar mensaje de \(message.sender)")`. Starting with the visible word keeps Voice Control working, because users say what they see ("Toca Archivar").
- **Keep the value the control shows.** When the control's visible content is a value (a quantity, a size, the selected option), replacing the label hides it: VoiceOver would say "Cantidad de…, botón" without the number. Put the new name in `.accessibilityLabel` and the shown value in `.accessibilityValue`.
- **Do not rely on `.accessibilityHint`** to carry the target. Hints are optional, can be turned off, and are not used by the rotor.
- **Do not change the visible text** unless the developer asks.
- **Alternative, mention only when it fits:** if the row is already combined into one element, expose the action with `.accessibilityAction(named: "Archivar") { ... }` instead of a separate button.

## Output format

Write the explanation in the developer's language. Keep code identifiers as they are.

For each defect, report once per control definition, not once per rendered copy:

**Issue:** one sentence saying what VoiceOver reads, how many times (from the tree, if present), and why the user cannot tell the targets apart.

**Fix:** one sentence with the minimal change.

```swift
// Only the modified control. Use `// ... unchanged ...` for the rest.
```

If nothing needs fixing, output exactly: `No action-context issues found.`

If you cannot tell whether controls share a name (for example the label comes from a parameter you cannot see and there is no tree), output:

**Needs context:** what is missing.

**Every code block must compile where it lives:**

- Start at the outermost view, property or function you change, and close every brace you open. Use `// ... unchanged ...` only in place of whole children or lines you did not touch, never to cut a structure in the middle.
- Use only names that exist in that scope. If the fix needs data the view does not have (for example the item's name inside a subview), show every change: one complete block that adds the property to the subview, and one for the call site that passes it.
- Do not force-unwrap (`!`) a value that is not optional.

Do not use git-style diffs (+/-). Do not output the whole file.

## Examples

### Example 1: Archive button repeated in every row

**Input:**

```swift
ForEach(messages) { message in
    HStack {
        Text(message.sender)
        Spacer()
        Button(action: { archive(message) }) {
            Label("Archivar", systemImage: "archivebox")
        }
    }
}
```

Tree excerpt: three elements `{"type": "button", "label": "Archivar"}`.

**Response:**

**Issue:** VoiceOver reads "Archivar, botón" three times, once per message, and the user cannot tell which message each button archives.

**Fix:** Add the sender to the label and keep "Archivar" first.

```swift
Button(action: { archive(message) }) {
    Label("Archivar", systemImage: "archivebox")
}
.accessibilityLabel("Archivar mensaje de \(message.sender)")
```

### Example 2: Single screen-level action (no issue)

**Input:**

```swift
VStack {
    // ... list of messages ...
    Button("Redactar", action: compose)
}
```

**Response:**

`No action-context issues found.`

"Redactar" appears once and acts on the whole screen.

### Example 3: Identical rows with unknown destinations

**Input:**

```swift
ForEach(orders) { order in
    NavigationLink(value: order) {
        HStack {
            Text("Ver detalles")
            Spacer()
            Image(systemName: "chevron.right")
        }
    }
}
```

Tree excerpt: three elements `{"type": "button", "label": "Ver detalles"}`.

**Response:**

**Issue:** VoiceOver reads "Ver detalles, botón" three times in a row, so the user cannot tell which order each one opens.

**Fix:** Add what identifies each row, keeping the visible text first. `order.number` is the only identifier visible in the code; the team should confirm it is what users recognize.

```swift
NavigationLink(value: order) {
    // ... unchanged ...
}
.accessibilityLabel("Ver detalles del pedido \(order.number)")
```

### Example 4: Selection control repeated in every row

**Input:**

```swift
ForEach($addresses) { $address in
    HStack {
        Text(address.street)
        Spacer()
        Image(systemName: address.isDefault ? "checkmark.circle.fill" : "circle")
            .onTapGesture { makeDefault(address) }
    }
}
```

Tree excerpt: three elements `{"type": "image", "label": "Círculo"}`.

**Response:**

**Issue:** The selection control in each address is read as "Círculo", the same in every row, so the user cannot tell which address it selects.

**Fix:** Name the control after its address. Its missing role and state are covered by `swiftui-control-semantics`.

```swift
Image(systemName: address.isDefault ? "checkmark.circle.fill" : "circle")
    .onTapGesture { makeDefault(address) }
    .accessibilityLabel("Usar \(address.street) como predeterminada")
```

### Example 5: The subview does not know its item

**Input:**

```swift
ForEach($recipes) { $recipe in
    HStack {
        Text(recipe.title)
        Spacer()
        SaveButton(isSaved: $recipe.isSaved)
    }
}

struct SaveButton: View {
    @Binding var isSaved: Bool
    var body: some View {
        Button("Guardar") { isSaved.toggle() }
    }
}
```

Tree excerpt: three elements `{"type": "button", "label": "Guardar"}`.

**Response:**

**Issue:** VoiceOver reads "Guardar, botón" three times, and the user cannot tell which recipe each button saves.

**Fix:** `SaveButton` does not know which recipe it belongs to, so pass the title in and use it in the label. Two changes, one per location.

```swift
struct SaveButton: View {
    @Binding var isSaved: Bool
    let recipeTitle: String

    var body: some View {
        Button("Guardar") { isSaved.toggle() }
            .accessibilityLabel("Guardar \(recipeTitle)")
    }
}
```

```swift
SaveButton(isSaved: $recipe.isSaved, recipeTitle: recipe.title)
```

### Example 6: Menu that shows its current value

**Input:**

```swift
ForEach($shirts) { $shirt in
    HStack {
        Text(shirt.model)
        Spacer()
        Menu {
            ForEach(Size.allCases) { size in
                Button(size.name) { shirt.size = size }
            }
        } label: {
            Text(shirt.size.name)
        }
    }
}
```

Tree excerpt: three elements `{"type": "button", "label": "M"}`.

**Response:**

**Issue:** VoiceOver reads "M, botón" in every row, so the user cannot tell which shirt each size menu changes, and hears the size with no name.

**Fix:** Name the menu after its shirt and keep the size as its value, so VoiceOver still says it.

```swift
Menu {
    // ... unchanged ...
} label: {
    Text(shirt.size.name)
}
.accessibilityLabel("Talla de \(shirt.model)")
.accessibilityValue(shirt.size.name)
```

### Example 7: Label comes from outside

**Input:**

```swift
struct RowActionButton: View {
    let title: String
    let action: () -> Void
    var body: some View { Button(title, action: action) }
}
```

**Response:**

**Needs context:** the label comes from `title` and there is no tree. The call sites are needed to know whether several rows pass the same title.

## Guardrails

- Never answer "Needs context" when the tree or a `ForEach` already shows the same label repeated. Report it.
- Never replace the label of a control that shows a value without moving that value to `.accessibilityValue`.
- Never put the target only in `.accessibilityHint`.
- Never remove the visible verb from the accessible name.
- Report a repeated control once, at its definition, with the count from the tree when available.
- Treat this skill as a focused review aid, not proof that the screen is accessible.
