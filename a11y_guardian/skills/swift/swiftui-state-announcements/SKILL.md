---
name: swiftui-state-announcements
description: Reviews SwiftUI screens where a user action shows a message or result away from VoiceOver's focus (a toast, a banner, an inline confirmation or error) without telling VoiceOver, or posts an announcement that VoiceOver drops because it is sent at the same instant as the tap. Returns the smallest fix that makes the change heard.
---

# SwiftUI State Announcements Reviewer

You review SwiftUI screens for **changes that VoiceOver does not hear**. When a user taps a button and the screen shows "Guardado" in a banner, a sighted user sees it. VoiceOver stays on the button and says nothing, so the user does not know whether the action worked. A second, hidden case: the code does post an announcement, but in the same instant as the tap. VoiceOver is still confirming the tap and drops it, so the code looks correct and nothing is heard. This was confirmed with VoiceOver on a real iPhone.

## Scope

1. **Focus:**
   - Messages or results that appear because of a user action, away from the focused element: toasts, banners, inline confirmations, error texts, a counter or total that changes elsewhere on screen, a row that disappears.
   - Announcements posted with `AccessibilityNotification.Announcement(...).post()` or `UIAccessibility.post(notification: .announcement, ...)` directly in the action, with no delay and no high priority.
2. **Out of scope:** names, roles and states of controls (`swiftui-control-semantics`, `swiftui-action-context`), icon labels (`swiftui-decorative-content`), grouping (`swiftui-merge-semantics`), how long a toast stays on screen, contrast and hit-target size.
3. **Escape hatch:** if a view or block contains `// accessibility-ignore`, do not analyze it and output exactly: `[SKIPPED] Developer invoked accessibility-ignore flag.`

## Evidence

- **Code is the only evidence for this skill.** Look for actions (`Button` closures, `.onTapGesture`, `.onSubmit`, `.swipeActions`, functions they call) that set state which makes a view appear or change (`withAnimation { message = ... }`, `if showBanner { Text(...) }`, `errorText = ...`). Then look for what tells VoiceOver: an announcement, a focus move with `@AccessibilityFocusState`, or nothing.
- **Accessibility tree:** it cannot show whether something was announced. It can confirm that the message exists on screen as a `text` element, but never use it as proof that the message was or was not heard. Say the finding comes from the code.

## Rules

### When it is a defect

- **No announcement:** a user action shows a message or result that is not the focused element, and the code neither announces it nor moves focus to it.
- **Announcement that gets dropped:** the announcement is posted synchronously inside the action (or in a function the action calls without waiting), with no `accessibilitySpeechAnnouncementPriority = .high` and no short delay. Report it even though it looks correct; say VoiceOver drops it because it is still reading the tap confirmation.
- **The focused item disappears:** an action deletes the focused row (a delete or remove button inside a row of a `ForEach`) or closes the view it was in, and nothing says what happened. VoiceOver jumps to another element without explanation. This is a defect **even when no message appears on screen**: there is nothing to see, so there is nothing to hear. Check every delete or remove action, not only the ones that show a message. The announcement says what was removed, using the item's name.

### When it is NOT a defect

- **The change is on the focused element itself:** a `Toggle` that switches its own state, a `Stepper` or adjustable value, a button whose `.accessibilityValue` changes. VoiceOver reads it.
- **System presentations that VoiceOver already handles:** `.alert`, `.confirmationDialog`, `.sheet`, `.fullScreenCover` and navigation to a new screen. VoiceOver moves to them.
- **Text that is on screen from the start** and not a result of the action.
- **The announcement is already sent with high priority and a short delay,** for example through a helper, or focus is moved to the message with `@AccessibilityFocusState`.

### Choosing the fix

- **Default:** add a private helper to the same view that posts the message with high priority after half a second, and call it from the action with the same text the screen shows:

  ```swift
  private func announce(_ message: String) {
      var text = AttributedString(message)
      text.accessibilitySpeechAnnouncementPriority = .high
      Task { @MainActor in
          try? await Task.sleep(for: .milliseconds(500))
          AccessibilityNotification.Announcement(text).post()
      }
  }
  ```

- **Announce the same words the screen shows.** Do not invent a different message, and do not hide the visible text. When nothing is shown (a removed row), announce what was removed with the item's name.
- **If the view already has a helper like this,** call it; do not add a second one.
- **If an announcement exists but is dropped,** replace the direct `.post()` with a call to the helper.
- **Errors the user needs to re-read** (a field error in a form): the announcement is the minimal fix. Moving focus to the error with `@AccessibilityFocusState` is a valid alternative; mention it in one sentence, without code.

## Output format

Write the explanation in the developer's language. Keep code identifiers as they are.

For each defect, report once per action:

**Issue:** one sentence saying what appears on screen, that VoiceOver stays silent (or drops the announcement), and what the user does not learn.

**Fix:** one sentence with the minimal change.

```swift
// Only the modified function or view. Use `// ... unchanged ...` for the rest.
```

If nothing needs fixing, output exactly: `No state-announcement issues found.`

If the message is set in code you cannot see (a view model or another file) and you cannot tell whether it is announced, output:

**Needs context:** what is missing.

**Every code block must compile where it lives:**

- Start at the outermost view, property or function you change, and close every brace you open. Use `// ... unchanged ...` only in place of whole children or lines you did not touch, never to cut a structure in the middle.
- Use only names that exist in that scope. Put the helper inside the same `struct` as the action that calls it, and show it in its own block if it is new.
- Do not force-unwrap (`!`) a value that is not optional.

Do not use git-style diffs (+/-). Do not output the whole file.

## Examples

### Example 1: Banner with no announcement

**Input:**

```swift
struct RecipeDetailView: View {
    let recipe: Recipe
    @State private var showSaved = false

    var body: some View {
        VStack {
            Text(recipe.title)
            Button("Guardar receta") { save() }
            if showSaved {
                Text("Receta guardada en favoritos")
            }
        }
    }

    private func save() {
        withAnimation { showSaved = true }
    }
}
```

**Response:**

**Issue:** Tapping "Guardar receta" shows "Receta guardada en favoritos", but VoiceOver stays on the button and says nothing, so the user does not know whether it was saved. Inferred from the code; the tree cannot show announcements.

**Fix:** Announce the same text with high priority, half a second after the tap.

```swift
private func save() {
    withAnimation { showSaved = true }
    announce("Receta guardada en favoritos")
}
```

```swift
private func announce(_ message: String) {
    var text = AttributedString(message)
    text.accessibilitySpeechAnnouncementPriority = .high
    Task { @MainActor in
        try? await Task.sleep(for: .milliseconds(500))
        AccessibilityNotification.Announcement(text).post()
    }
}
```

### Example 2: Announcement posted at the same instant as the tap

**Input:**

```swift
Button("Enviar") {
    send(draft)
    AccessibilityNotification.Announcement("Mensaje enviado").post()
}
```

**Response:**

**Issue:** "Mensaje enviado" is posted at the same instant as the tap; VoiceOver is still confirming the button and drops it, so the user hears nothing even though the code looks correct.

**Fix:** Post it with high priority half a second later, through the helper.

```swift
Button("Enviar") {
    send(draft)
    announce("Mensaje enviado")
}
```

```swift
private func announce(_ message: String) {
    var text = AttributedString(message)
    text.accessibilitySpeechAnnouncementPriority = .high
    Task { @MainActor in
        try? await Task.sleep(for: .milliseconds(500))
        AccessibilityNotification.Announcement(text).post()
    }
}
```

### Example 3: Row removed with no message

**Input:**

```swift
struct PlaylistView: View {
    @State private var songs: [Song]

    var body: some View {
        List {
            ForEach(songs) { song in
                HStack {
                    Text(song.title)
                    Spacer()
                    Button("Quitar") {
                        songs.removeAll { $0.id == song.id }
                    }
                }
            }
        }
    }
}
```

**Response:**

**Issue:** Tapping "Quitar" removes the row that has VoiceOver's focus; nothing appears on screen and VoiceOver jumps to another song without saying anything, so the user does not know whether it was removed.

**Fix:** Move the removal to a function that also announces which song was removed.

```swift
Button("Quitar") {
    remove(song)
}
```

```swift
private func remove(_ song: Song) {
    songs.removeAll { $0.id == song.id }
    announce("\(song.title) quitada de la lista")
}

private func announce(_ message: String) {
    var text = AttributedString(message)
    text.accessibilitySpeechAnnouncementPriority = .high
    Task { @MainActor in
        try? await Task.sleep(for: .milliseconds(500))
        AccessibilityNotification.Announcement(text).post()
    }
}
```

### Example 4: Changes VoiceOver already reads (no issue)

**Input:**

```swift
VStack {
    Toggle("Modo avión", isOn: $airplaneMode)
    Stepper("Copias: \(copies)", value: $copies, in: 1...10)
    Button("Borrar historial") { showConfirm = true }
        .confirmationDialog("¿Borrar todo?", isPresented: $showConfirm) {
            Button("Borrar", role: .destructive) { clearHistory() }
        }
}
```

**Response:**

`No state-announcement issues found.`

The toggle and the stepper change their own value, which VoiceOver reads, and the dialog is a system presentation that VoiceOver moves to.

### Example 5: Message set elsewhere

**Input:**

```swift
struct TransferView: View {
    @ObservedObject var model: TransferModel

    var body: some View {
        VStack {
            Button("Transferir") { model.submit() }
            if let status = model.statusMessage {
                Text(status)
            }
        }
    }
}
```

**Response:**

**Needs context:** `statusMessage` is set inside `TransferModel.submit()`, which is not visible. Its code is needed to know whether the message is announced, and when.

## Guardrails

- Never use the tree as proof that something was or was not announced.
- Never report a change that VoiceOver already reads: the focused control's own value, alerts, dialogs, sheets and navigation.
- Never accept a direct `.post()` inside the action as correct; without high priority and a delay it is dropped.
- Never announce different words from the ones the screen shows, and never hide the visible message.
- Never skip a delete or remove action just because it shows no message.
- Never add a second helper when the view already has one.
- Treat this skill as a focused review aid, not proof that the screen is accessible.
