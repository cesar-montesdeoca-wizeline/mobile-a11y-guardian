---
name: compose-liveregion-auditor
description: Audit Jetpack Compose code to suggest adding liveRegion = LiveRegionMode.Polite to dynamically appearing messages after user interaction. Use when developers want TalkBack announcements for dynamic status or confirmation text.
---
# Compose LiveRegion Auditor

Audit Jetpack Compose code to suggest adding `liveRegion = LiveRegionMode.Polite` to dynamic status messages, banners, and confirmation texts that appear after user interaction.

## When to Use

- When reviewing Jetpack Compose code for dynamic text changes or status messages triggered by user actions.
- When a user asks how to make TalkBack or screen readers announce dynamic feedback or verification messages in Compose.
- When auditing Compose elements specifically for `LiveRegionMode.Polite` semantics.

## Scope and Critical Constraint

- **STRICTLY LIMITED SCOPE**: This skill ONLY applies to dynamic message announcements via `liveRegion = LiveRegionMode.Polite`.
- Do NOT audit or suggest changes for other accessibility concerns such as color contrast, touch target sizes, general `contentDescription`, focus traversals, or heading semantics.

## Procedure

1. Inspect the Jetpack Compose composable for state variables that control conditional UI display (such as success, error, or confirmation messages shown after a button click or form submit).
2. Identify the dynamic text elements (e.g., `Text` composables) rendered conditionally based on that state.
3. Suggest attaching the `semantics` modifier with `liveRegion = LiveRegionMode.Polite` so TalkBack announces the message upon appearance.
4. Explain clearly why this is necessary: TalkBack does not automatically speak newly appeared UI elements unless focus explicitly shifts to them or they are marked as a live region.

## Few-Shot Example

### Input Code (Problematic Pattern)

```kotlin
@Composable
fun ZipCodeCoverageChecker(
  modifier: Modifier = Modifier,
  availableZipCodes: Set<String> = setOf("01000", "03100", "06700", "11000", "64000")
) {
  var zipCode by remember { mutableStateOf("") }
  var isCovered by remember { mutableStateOf<Boolean?>(null) }
  val focusManager = LocalFocusManager.current

  val verifyZipCode = {
    focusManager.clearFocus()
    if (zipCode.isNotBlank()) {
      isCovered = zipCode in availableZipCodes
    }
  }

  Column(
    modifier = modifier
      .fillMaxWidth()
      .padding(16.dp),
    horizontalAlignment = Alignment.CenterHorizontally,
    verticalArrangement = Arrangement.spacedBy(12.dp)
  ) {
    OutlinedTextField(
      value = zipCode,
      onValueChange = { input ->
        if (input.all { it.isDigit() } && input.length <= 5) {
          zipCode = input
          isCovered = null
        }
      },
      label = { Text("Código postal") },
      placeholder = { Text("Ej. 06700") },
      singleLine = true,
      keyboardOptions = KeyboardOptions(
        keyboardType = KeyboardType.Number,
        imeAction = ImeAction.Done
      ),
      keyboardActions = KeyboardActions(
        onDone = { verifyZipCode() }
      ),
      modifier = Modifier.fillMaxWidth()
    )

    Button(
      onClick = { verifyZipCode() },
      enabled = zipCode.length == 5,
      modifier = Modifier.fillMaxWidth()
    ) {
      Text("Verificar cobertura")
    }

    when (isCovered) {
      true -> {
        Text(
          text = "Entregamos en tu zona",
          color = Color(0xFF2E7D32),
          style = MaterialTheme.typography.bodyLarge,
          fontWeight = FontWeight.Bold
        )
      }
      false -> {
        Text(
          text = "No entregamos en tu zona",
          color = MaterialTheme.colorScheme.error,
          style = MaterialTheme.typography.bodyLarge,
          fontWeight = FontWeight.Bold
        )
      }
      null -> Unit
    }
  }
}
```

### Remediation Suggestion

Add `liveRegion = LiveRegionMode.Polite` inside `Modifier.semantics` for both dynamic outcome states:

```kotlin
    when (isCovered) {
      true -> {
        Text(
          text = "Entregamos en tu zona",
          color = Color(0xFF2E7D32), // Material Green 800
          style = MaterialTheme.typography.bodyLarge,
          fontWeight = FontWeight.Bold,
          modifier = Modifier.semantics {
            liveRegion = LiveRegionMode.Polite
          }
        )
      }
      false -> {
        Text(
          text = "No entregamos en tu zona",
          color = MaterialTheme.colorScheme.error,
          style = MaterialTheme.typography.bodyLarge,
          fontWeight = FontWeight.Bold,
          modifier = Modifier.semantics {
            liveRegion = LiveRegionMode.Polite
          }
        )
      }
      null -> Unit
    }
```