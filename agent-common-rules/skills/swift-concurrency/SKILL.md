---
name: swift-concurrency
description: Use when working on Swift code involving async/await, Swift Concurrency, UIKit or SwiftUI ViewModels, Combine bindings, loading state, MainActor, networking, or I/O.
---

# Swift Concurrency

Apply only when working on Swift code.

## Async Boundaries

- Prefer `async`/`await` for asynchronous work.
- Public methods that perform network or I/O should generally be `async`.
- Create async boundaries from UIKit synchronous entry points such as `viewDidLoad`, `@objc` actions, and button taps with `Task { await ... }`.

## Main Actor

- Do not wrap work in `Task { @MainActor in ... }` from an existing `@MainActor` type or context.
- Keep UI state mutations on the main actor.
- Mark ViewModels or UI-facing types `@MainActor` when their state is consumed by UIKit or SwiftUI views.

## Loading State

- Set loading state inside the async function body.
- Use `defer` inside the async body to reset loading state.
- Do not use a synchronous outer function with `defer { isLoading = false }` while the actual work runs inside an inner `Task`.

## Combine And UIKit MVVM

- Use Combine mainly for ViewModel-to-View binding in UIKit.
- Keep domain asynchronous flows in `async`/`await`, not `Future` or publisher chains.
- In UIKit, `@Published` does not update views automatically. ViewControllers must subscribe manually with `$property.sink`.
- Expose ViewModel output state as `@Published private(set)`.
