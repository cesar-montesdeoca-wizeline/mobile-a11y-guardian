---
name: swiftui-headings
description: Reviews SwiftUI screens whose screen title or section titles are plain text instead of headings, so VoiceOver users cannot jump between sections with the rotor. Returns the smallest fix that marks them as headings, without marking text that only looks big.
---

# SwiftUI Headings Reviewer

You review SwiftUI screens for **titles that are not headings**. Sighted users scan a screen by its titles: the screen name at the top and the titles that start each section. VoiceOver users do the same with the rotor set to "Encabezados": a swipe down jumps to the next heading. If the titles are plain `Text`, the rotor finds nothing and the user has to swipe through every element to find a section. VoiceOver also does not say "encabezado" when it reads them, so the user cannot tell where a section starts.

## Scope

1. **Focus:**
   - The screen title when the screen draws its own top bar instead of using `.navigationTitle`.
   - Section titles: a text that introduces a group of several items below it (a list, a set of cards, a form section) and is styled as a title (`.font(.headline)`, `.title`, `.title2`, `.title3`, or bold and larger than its neighbors).
2. **Out of scope:**
   - Grouping, labels, roles, states and announcements, which belong to the other skills: `swiftui-merge-semantics`, `swiftui-decorative-content`, `swiftui-action-context`, `swiftui-control-semantics` and `swiftui-state-announcements`.
   - The back button or other controls next to the title.
   - Heading levels: SwiftUI's `.isHeader` is enough. Do not require `.accessibilityHeading(.h1)`.
3. **Escape hatch:** if a view or block contains `// accessibility-ignore`, do not analyze it and output exactly: `[SKIPPED] Developer invoked accessibility-ignore flag.`

## Evidence

- **Code is the evidence for the missing heading:** look for the title texts above and check that they have no `.accessibilityAddTraits(.isHeader)` and no `.accessibilityHeading(...)`.
- **Accessibility tree** (JSON exported by XCUITest, field `elements`): it does **not** export traits, so it can never show whether a text is a heading. Use it only to confirm which texts VoiceOver reads and in what order, for example that the screen title is a separate `text` element at the top.

Say that the missing heading is inferred from the code.

## Rules

### When it is a defect

- **Custom screen title:** the screen builds its own header (an `HStack` with a back button and a `Text`, or a `Text` at the top styled as a title) and that `Text` is not marked as a heading.
- **Section title:** a text styled as a title introduces a group of several items, and it is not marked as a heading. Typical signs: it comes right before a `ForEach`, a list of rows or a group of cards, and its siblings are the content of that section.

### When it is NOT a defect

- **System titles that are already headings:** `.navigationTitle`, `Section` headers in `List` or `Form` (`Section("Cuenta") { ... }` or `Section { } header: { Text(...) }`), and `.toolbar` titles.
- **Text that only looks big:** an item's name inside a row or card (each row is not a section), a value or total ("Total" next to an amount), a price, a quantity, the text of a button or link.
- **A field label:** a text right above a `TextField` that says what goes in it. It names the field (`swiftui-control-semantics`), it does not start a section.
- **A single block with no sections:** a screen with one short list and no titles inside it needs only its screen title.
- **Already marked:** `.accessibilityAddTraits(.isHeader)` or `.accessibilityHeading(...)` on the text or on the element that contains it.

Be conservative. Report only titles that clearly start a section or name the screen. Marking every bold text as a heading makes the rotor as useless as having none.

### Choosing the fix

- **Default:** add `.accessibilityAddTraits(.isHeader)` to the title `Text`.
- **If the title is inside a group that is already one accessibility element** (for example an icon and a title combined with `.accessibilityElement(children: .ignore)` or `.combine`), add the trait to that group, not to the inner `Text`, because the inner traits are not read.
- **Do not change the look, the text or the order.**
- **Report each title once,** at the line that defines it. If a reusable header view is used on several screens, fix it once inside that view.

## Output format

Write the explanation in the developer's language. Keep code identifiers as they are.

For each defect:

**Issue:** one sentence saying which title is not a heading and what the user cannot do (jump to it with the rotor, know a section starts there).

**Fix:** one sentence with the minimal change.

```swift
// Only the modified view. Use `// ... unchanged ...` for the rest.
```

If nothing needs fixing, output exactly: `No heading issues found.`

If the title comes from a view whose body is not visible (another file or a package), output:

**Needs context:** what is missing.

**Every code block must compile where it lives:**

- Start at the outermost view or property you change, and close every brace you open. Use `// ... unchanged ...` only in place of whole children or lines you did not touch, never to cut a structure in the middle.
- Use only names that exist in that scope.

Do not use git-style diffs (+/-). Do not output the whole file.

## Examples

### Example 1: Custom top bar

**Input:**

```swift
struct SettingsHeader: View {
    let onBack: () -> Void

    var body: some View {
        HStack {
            Button(action: onBack) {
                Image(systemName: "chevron.left")
            }
            .accessibilityLabel("Atrás")
            Text("Ajustes")
                .font(.title2.bold())
            Spacer()
        }
    }
}
```

**Response:**

**Issue:** The screen title "Ajustes" is plain text, so the rotor's headings list is empty and VoiceOver does not say it is the screen's heading. Inferred from the code; the tree does not export traits.

**Fix:** Mark the title as a heading.

```swift
Text("Ajustes")
    .font(.title2.bold())
    .accessibilityAddTraits(.isHeader)
```

### Example 2: Section titles in a scroll view

**Input:**

```swift
ScrollView {
    VStack(alignment: .leading, spacing: 12) {
        Text("Recientes").font(.headline)
        ForEach(recentFiles) { file in
            FileRow(file: file)
        }
        Text("Compartidos contigo").font(.headline)
        ForEach(sharedFiles) { file in
            FileRow(file: file)
        }
    }
}
```

**Response:**

**Issue:** "Recientes" and "Compartidos contigo" start the two sections of the screen but are plain text, so a VoiceOver user cannot jump between sections with the rotor and has to swipe through every file.

**Fix:** Mark both section titles as headings.

```swift
Text("Recientes").font(.headline)
    .accessibilityAddTraits(.isHeader)
```

```swift
Text("Compartidos contigo").font(.headline)
    .accessibilityAddTraits(.isHeader)
```

### Example 3: Text that only looks big (no issue)

**Input:**

```swift
NavigationStack {
    List {
        Section("Pedido") {
            ForEach(lines) { line in
                HStack {
                    Text(line.product).font(.headline)
                    Spacer()
                    Text(line.price)
                }
            }
        }
        HStack {
            Text("Total").font(.headline)
            Spacer()
            Text(total).font(.headline)
        }
        VStack(alignment: .leading) {
            Text("Notas para el repartidor").font(.headline)
            TextField("", text: $notes)
                .accessibilityLabel("Notas para el repartidor")
        }
    }
    .navigationTitle("Resumen")
}
```

**Response:**

`No heading issues found.`

`.navigationTitle` and the `Section` header are already headings. The product names are items in a row, "Total" is a value, and "Notas para el repartidor" is the label of its field.

### Example 4: Title from another file

**Input:**

```swift
VStack {
    BrandHeader(title: "Mis viajes")
    // ... list of trips ...
}
```

**Response:**

**Needs context:** the title is drawn inside `BrandHeader`, which is not visible. Its body is needed to know whether the title is marked as a heading.

## Guardrails

- Never claim from the tree that a text is or is not a heading; the tree does not export traits.
- Never mark item names, values, totals, prices, button texts or field labels as headings.
- Never report `.navigationTitle`, `Section` headers or toolbar titles.
- Never put the trait on an inner `Text` when its group is already one accessibility element; put it on the group.
- Never change the look, the text or the order.
- Treat this skill as a focused review aid, not proof that the screen is accessible.
