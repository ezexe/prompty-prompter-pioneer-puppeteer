# Instructions

>io

## Scope

A **platform that hosts specialized integrations** — external providers, third-party APIs, or self-contained subsystems — as interchangeable modules under `core/`. Any single integration serves as a reference implementation, not the sole use case.

**Core Principle:** Platform features (shared data, events, user/session handling, common UI) are integration-agnostic and live in the platform layer (`$lib/`).

**Design Intent:** As new integrations are added, patterns repeated across modules are extracted to the platform layer.

---

## Tool Protocols

### DaisyUI (MCP)

1. `fetch-daisyui-documentation` → ALWAYS call first
2. `search-daisyui-documentation` → Semantic search after fetch
3. `search-daisyui-code` → Implementation details only
4. `fetch-generic-url-content` → External references

### Svelte (MCP)

1. `list-sections` → ALWAYS call first for any Svelte query
2. `get-documentation` → Fetch ALL relevant sections (check `use_cases` field)
3. `svelte-autofixer` → MUST run on all Svelte code before responding; iterate until clean
4. `playground-link` → Ask user first; NEVER use if code written to project files

---

## Coding Conventions

### Declarations

- MUST use `const` arrow functions: `const fn = () => {}`
- OMIT obvious type annotations
- Prefer minimal atomic diffs

### Error Handling

- NEVER add pre-checks to prevent runtime errors from throwing
- Let errors throw naturally — built-in errors have better stack traces than manual replacements
- Do NOT wrap or swallow built-in errors with less traceable `error()` / `throw` alternatives
- If a function throws on bad input (e.g. `timingSafeEqual` on mismatched lengths), that throw is the correct behavior

### Interfaces vs Types

#### `interface I*` — Abstract Contracts (Polymorphism)

- Abstract contracts for polymorphic implementations

The `I` prefix signals cross-module abstraction. Multiple modules implement the same contract.

```typescript
// Abstract contracts with I prefix — polymorphism across modules
interface IRecord {
  id: string;
  name: string;
}

interface ISource {
  getStats(): Stats;
}

// Modules implement these contracts
class Invoice implements IRecord { ... }
class Contact implements IRecord { ... }
```

#### `interface` (no prefix) — TypeScript Convention Cases

- Object inheritance/composition via `extends`
- Publicly exposed API types (library/package boundaries)
- Class contracts using `implements`

Per TypeScript's [official guidance](https://www.typescriptlang.org/play/typescript/language-extensions/types-vs-interfaces.ts.html) and [Performance Wiki](https://github.com/microsoft/TypeScript/wiki/Performance), prefer `interface` over `type` in these scenarios:

**Object inheritance via `extends`** — TypeScript caches interface relationships by name. Intersections (`&`) are recomputed each time, so `extends` yields faster type-checking and better error messages in composed types.

```typescript
// ✅ Cached by name, faster type-checking, clearer errors
interface Timestamped {
  createdAt: Date;
  updatedAt: Date;
}

interface SoftDeletable extends Timestamped {
  deletedAt: Date | null;
}

// ❌ Recomputed each time, less informative errors
type SoftDeletable = Timestamped & {
  deletedAt: Date | null;
};
```

**Publicly exposed API types** — interfaces are open for declaration merging, making them suitable for library boundaries and package exports where consumers may need to augment definitions.

```typescript
// Public API boundary — consumers can extend
interface PluginConfig {
  name: string;
  version: string;
}
```

**Class contracts** — when a class uses `implements`, the implemented type reads most naturally as an `interface`.

```typescript
interface Serializable {
  serialize(): string;
  deserialize(data: string): void;
}

class JsonStore implements Serializable { ... }
```

#### `type` — Everything Else

Props, data shapes, unions, functions, intersections (when not composing object hierarchies), mapped types, and conditional types.

```typescript
type Props = { title: string; readonly?: boolean };
type Invoice = { id: string; amount: number; currency: string };
type Status = "pending" | "approved" | "rejected";
type Handler = (event: Event) => void;
type Nullable<T> = T | null;
```

**Rationale:** The `I` prefix signals abstraction/polymorphism intent — when multiple modules implement the same contract. Plain `interface` (no prefix) is used where TypeScript conventions recommend it for performance (cached `extends` vs recomputed `&`), better error messages, and extensibility at API boundaries. `type` handles everything else without ceremony.

### Variable Organization

**Default:** Tier 1 (flat grouping)

```typescript
// Tier 1: Simple flat grouping (default)
const settings = { maxRetries: 3, timeoutMs: 5000, enableCache: true };
```

**Opt-in:** Tier 2 (structured) ONLY when structure adds clarity

```typescript
// Tier 2 Entity-centric: "Properties of X"
const connections = { max: 50, min: 1, default: 10, retry: 3 };

// Tier 2 Concern-centric: "All X in system"
const timeout = { database: 5000, api: 3000, cache: 1000 };
```

**Decision:** If "these go together" suffices → Tier 1. If "properties of X" or "all X in system" fits → Tier 2.

### Type Naming

| Rule                                            | Example                                       |
| ----------------------------------------------- | --------------------------------------------- |
| Export domain names, not generic                | `export type Invoice` not `export type Full`  |
| Short names OK in focused modules (≤15 exports) | `user.ts`: `Settings`, `Profile`              |
| Explicit prefixes in aggregation modules (20+)  | `types.ts`: `UserSettings`, `ProductCategory` |

```typescript
// ❌ Generic name forces renaming
// invoice.ts
export type Full = { id: string; amount: number };
// Consumer forced to: import { Full as Invoice } from './invoice'

// ✅ Domain name at export
export type Invoice = { id: string; amount: number };
// Consumer uses directly: import type { Invoice } from './invoice'
```

```typescript
// Small focused module (≤15 exports) — short names OK
// user.ts
export type User = { name: string };
export type Settings = { theme: string }; // Context: user settings
export type Profile = { bio: string }; // Context: user profile

// Large aggregation module (20+ exports) — explicit prefixes
// types.ts
export type User = { name: string };
export type UserSettings = { theme: string }; // Explicit
export type ProductCategory = { title: string }; // Explicit
```

---

# Integration Module Architecture

A general convention for organizing any **specialized integration** — an external provider, a third-party API, or a self-contained subsystem — as a self-contained module that mirrors the platform layer it sits on.

## Directory Convention

### Platform Layer (`$lib/`)

```
$lib/
├── core/                      # Integration modules — self-contained units, each a partial mirror of $lib/
├── svelted/                   # Platform runes + client functions
│   ├── ui/                    # Reusable components
│   │   └── actions/buttons/Button.svelte
│   └── store.svelte.ts        # Shared, integration-agnostic store
├── server/
│   └── db/                    # Database schemas
└── utilz/                     # Shared utilities
```

`core/` holds the project's integration modules. Everything beside it (`svelted/`, `server/`, `utilz/`) is cross-cutting platform that modules build on. The key property: **a module is a partial mirror of `$lib/` itself** — it carries its own scoped `svelted/`, `server/`, `utilz/` (plus `api/`) when it needs them.

### Integration Modules (`$lib/core/{INTEGRATION}/`)

Self-contained vertical slices with route-aligned internal organization. An **integration module** owns its external integration, its domain types, its rules, and its UI — everything needed to deliver one coherent slice of the product.

**Two tiers.** A **module** (`$lib/core/{INTEGRATION}/`) is the self-contained unit: it owns a `features/` collection, optionally an `api/` folder when it talks to an external provider, and may carry module-scoped `svelted/`, `server/`, `utilz/` mirroring the platform layer. Each **sub-feature** under `features/` is a lighter unit — feature-scoped logic plus a `svelted/` folder only where SvelteKit primitives are in play. Distinct names at each level (`core/{INTEGRATION}/features/{sub}/`) keep the tiers legible. Payments, a CRM connector, an analytics pipeline, an auth provider — each is a module following the identical pattern; none is a special category, just a set of modules.

```
core/{INTEGRATION}/
├── {integration}.ts          # Public API / initialization
├── {integration}.server.ts   # Server-only exports
├── api/                      # (optional) external integration — provider client, constants
├── svelted/                  # (optional) module-scoped runes/client — mirrors $lib/svelted/
├── server/                   # (optional) module-scoped server code — mirrors $lib/server/
├── utilz/                    # (optional) module-scoped utils + types — mirrors $lib/utilz/
└── features/                 # Route-aligned sub-features
    └── {route}/              # Route directory
        └── {subFeature}/     # Sub-feature directory
            ├── *.ts              # Sub-feature logic (rules, validators)
            └── svelted/          # SvelteKit archetypes (only when needed)
                ├── store.svelte.ts
                ├── data.remote.ts
                └── ui/
```

A module's bare minimum is `features/` + the entry files; `api/` appears only when the module talks to an external provider, and the mirrored `svelted/ server/ utilz/` appear only when something is shared across the module's sub-features.

#### Illustrative example: a `payments` integration

One module among many an app might host (CRM, analytics, auth, notifications all take the same shape):

```
core/payments/
├── payments.ts
├── payments.server.ts
├── types.d.ts            # unified module types
├── api/
│   ├── enums.ts          # PLAN_TIERS, BILLING_INTERVALS, CURRENCIES
│   ├── client.ts         # Provider API calls
│   └── webhooks.ts       # Provider event ingestion
├── utilz/
│   └── {util}.ts         # named per concern — e.g. money.ts: formatAmount(), planFor()
└── features/
    └── billing/
        └── checkout/
            ├── rules.ts        # prorate(), applyCoupon()
            ├── validators.ts   # validateCart()
            └── svelted/
                ├── store.svelte.ts   # Uses $state, imports ../rules.ts
                └── ui/
                    ├── Checkout.svelte
                    └── Summary.svelte
```

### Naming Convention

- **Standard modules:** lowercase by service/domain (`payments`, `auth`, `analytics`, `notifications`).
- **Interchangeable instances** of the same kind, dispatched at runtime via a registry/enum, may use a short **2–4 uppercase code** (e.g. `STRP`, `PYPL`) so the lookup stays terse.

### Directory Rules

| Pattern                     | Criteria                                 | Location                                           |
| --------------------------- | ---------------------------------------- | -------------------------------------------------- |
| External API calls          | 3rd party integrations                   | `{INTEGRATION}/api/`                               |
| Integration constants/enums | From external sources                    | `{INTEGRATION}/api/enums.ts`                       |
| Module-wide types           | Unified per module                       | `{INTEGRATION}/types.d.ts`                         |
| Module-wide utils           | Shared across sub-features (per concern) | `{INTEGRATION}/utilz/{util}.ts`                    |
| Module-scoped runes/server  | Shared across sub-features               | `{INTEGRATION}/svelted/`, `{INTEGRATION}/server/`  |
| Sub-feature logic           | Route-specific (rules, validators)       | `{INTEGRATION}/features/{route}/{sub}/`            |
| `*.svelte.ts`               | Uses `$state`, `$derived`, `$effect`     | `{INTEGRATION}/features/{route}/{sub}/svelted/`    |
| `*.remote.ts`               | Uses `query` from `$app/server`          | `{INTEGRATION}/features/{route}/{sub}/svelted/`    |
| `*.svelte`                  | Coupled to a sub-feature's rune store    | `{INTEGRATION}/features/{route}/{sub}/svelted/ui/` |
| Generic components          | Reusable across modules                  | `$lib/svelted/ui/`                                 |

### Placement Decision Tree

```
Is it an external integration or a constant from an external source?
├── YES → `{INTEGRATION}/api/`
└── NO: Does it use Svelte runtime primitives — $state/$derived/$effect, `query`, or is it a `.svelte` component?
    ├── NO (logic/helpers — rules, validators, formatters):
    │   ├── Shared across sub-features? → `{INTEGRATION}/utilz/`
    │   └── Scoped to one sub-feature?  → `{INTEGRATION}/features/{route}/{sub}/`
    └── YES:
        ├── `$state` / `$derived` / `$effect`  → `{INTEGRATION}/features/{route}/{sub}/svelted/`
        ├── `query` from `$app/server`          → `{INTEGRATION}/features/{route}/{sub}/svelted/`
        └── `.svelte` component:
            ├── Reusable across modules?  → `$lib/svelted/ui/`
            └── Module / sub-feature only? → `{INTEGRATION}/features/{route}/{sub}/svelted/ui/`
```

**Examples** (within the `payments` module):

| Code                | Resolution              | Location                                                             |
| ------------------- | ----------------------- | -------------------------------------------------------------------- |
| `PLAN_TIERS` enum   | External source         | `core/payments/api/enums.ts`                                         |
| Provider API client | External integration    | `core/payments/api/client.ts`                                        |
| `Invoice` interface | Module-wide type        | `core/payments/types.d.ts`                                           |
| `formatAmount()`    | Module-wide helper      | `core/payments/utilz/{util}.ts`                                      |
| `checkoutRules`     | Checkout-only logic     | `core/payments/features/billing/checkout/rules.ts`                   |
| Checkout store      | Uses `$state`           | `core/payments/features/billing/checkout/svelted/store.svelte.ts`    |
| `Checkout.svelte`   | Component, not reusable | `core/payments/features/billing/checkout/svelted/ui/Checkout.svelte` |
| `Entity.svelte`     | Component, reusable     | `$lib/svelted/ui/Entity.svelte`                                      |

### Platform vs Module

| Location                                                  | Contains                          | Examples                         |
| --------------------------------------------------------- | --------------------------------- | -------------------------------- |
| `$lib/svelted/`                                           | Platform runes + client functions | `store.svelte.ts`                |
| `$lib/svelted/ui/`                                        | Reusable components               | `Entity.svelte`, `Filter.svelte` |
| `$lib/server/`                                            | Platform server code              | DB schemas                       |
| `$lib/utilz/`                                             | Shared utilities                  | cross-module helpers             |
| `$lib/core/{INTEGRATION}/api/`                            | External integrations & constants | API clients, enums, webhooks     |
| `$lib/core/{INTEGRATION}/utilz/`                          | Module-wide utils                 | helpers, one file per concern    |
| `$lib/core/{INTEGRATION}/svelted/`, `/server/`            | Module-scoped runes/server        | shared across sub-features       |
| `$lib/core/{INTEGRATION}/features/{route}/{sub}/`         | Sub-feature logic                 | rules, validators                |
| `$lib/core/{INTEGRATION}/features/{route}/{sub}/svelted/` | Sub-feature archetypes            | store, remote, UI                |
| `routes/`                                                 | Integration-agnostic UI shells    | shared layouts, browsers         |
| `routes/{integration}/`                                   | Module-specific routes (rare)     | deep integrations                |

The line: if removing it would break an unrelated module, it's platform (`$lib/` root); if it only breaks itself, it lives in the module.

---

## Integration Module Contract

Every module follows the same contract. Modules that integrate external data provide `api/`, domain types, and an `init()`; the rest appear as the module needs them.

### 1. External Integration (`api/`)

```typescript
// api/enums.ts - integration constants (examples vary by integration)
// payments:   PLAN_TIERS, BILLING_INTERVALS, CURRENCIES
// CRM:        PIPELINE_STAGES, LEAD_SOURCES, OWNERS
// analytics:  EVENT_TYPES, CHANNELS, METRICS

// api/client.ts - 3rd party API calls
export const fetchRecords = async () => { ... };
export const fetchEvents  = async () => { ... };
```

### 2. Type Definitions (`types.d.ts`)

The module's domain entities — whatever the integration models. For `payments` that's `IPlan` / `IInvoice` / `ISubscription`; another module defines its own.

```typescript
interface IRecord {
  /* the primary entity the integration exposes */
}
interface IEvent {
  /* a state change / webhook payload */
}
interface IAction {
  /* an operation the user can perform */
}
```

### 3. Data Loading (`{integration}.ts`)

```typescript
export const status: { [key: string]: any } = {};

export const init = async (fetch?) => {
  // Load static data (records, events, reference data)
  // Return populated status
};
```

### 4. Rules (`features/{route}/{sub}/rules.ts`)

- Scoring / computation logic
- Validation constraints
- Domain-specific mechanics

### 5. UI (`features/{route}/{sub}/svelted/ui/`)

- Primary interface for the sub-feature
- Entity components
- Supporting displays

### Optional but Recommended

- `utilz/{util}.ts` — module helper functions, one file per concern
- `features/{route}/filters/` — data filtering/search
- Server functions for real-time data

---

## Schema Design: Colmon Pattern

Use `meta: pg.jsonb()` for module-specific data; keep the platform schema generic.

```typescript
// Platform schema (generic)
records: {
  userId: text,
  refId: text,
  meta: jsonb  // Integration-specific data here
}

meta.payments  = { planId, interval, currency }
meta.crm       = { contactId, stage, owner }
meta.analytics = { eventId, channel, ts }
```

**Rule:** Integration data goes in `meta.{integration}`; nested channel/sub-provider data goes in `meta.{channel}` — never a schema change.

---

## Reference Implementation

A first reference module (e.g. `payments`) establishes the pattern. When reviewing it:

- ✅ **Extract** patterns for documentation
- ✅ **Identify** platform features
- ❌ **Don't assume** its design decisions apply to every module
- ❌ **Don't couple** platform code to module-specific types/logic

**Example:** a module has `features/billing/checkout/svelted/store.svelte.ts` → ask:

- Integration-agnostic? → extract to `$lib/svelted/store.svelte.ts`
- Module-specific? → keep in `$lib/core/payments/features/billing/checkout/svelted/store.svelte.ts`

**Typical sub-features (reference shape):** a record browser with filtering, a stateful store with persistence, an event/webhook tracker, an entity manager.

---

## Adding a New Module: Checklist

1. **Create** `$lib/core/{INTEGRATION}/`:
   ```
   {INTEGRATION}/
   ├── {integration}.ts
   ├── {integration}.server.ts
   └── features/
   ```
   (add `api/` when integrating an external provider; add module-scoped `svelted/`, `server/`, `utilz/` as needed)
2. **Implement** the contract: api integration, domain types (`types.d.ts`), `init()` + `status`, rules, UI.
3. **Register** the module in platform config/enum (uppercase code if it's an interchangeable instance).
4. **Test** against existing routes and shared shells.
5. **Document** module-specific quirks.
6. **Extract** shared patterns to the platform layer (`$lib/`).
