# @lam/protobuf Changelog

All notable changes to `@lam/protobuf` are documented here.

## [3.0.5] - 2026-11-14

### Tests

- `tests/test_pb_edge_cases.lam`: every `Pb` method given a value that is not
  a message or `None`; empty messages; truncated wire data and invalid UTF-8
  in a string field (`PbError`, while a bytes field accepts the bytes); a
  4 MiB bytes field; proto-JSON of int64, bytes, NaN/infinities, Duration,
  Timestamp and non-ASCII text, malformed JSON and unknown fields refused;
  text-format round trips; `equal` across types, unset vs. default and
  changed clones.
- `tests/test_pb_event_log_composed.lam`: an `EventLog` class encoding
  `structpb` events in 40 concurrent async tasks, replaying them with `?`,
  filtering with comprehensions, recovering from a corrupted record with
  `do/catch`, wire/JSON/text conversions and byte sizes, clones mutated in
  tasks.

## [3.0.4] - 2026-11-14

### Fixed

- Wire sizes are measured in bytes: the tests compared `Pb.size(msg)` and
  the hex length with `len(wire)`, which counts the characters of the `str`
  from lamc 4.14 on (strings are sequences of characters), so a wire whose
  bytes form multi-byte UTF-8 sequences looked shorter. They use
  `len(bytes(wire))`, the byte count with lamc 4.13 and 4.14; the README and
  the `marshal` documentation say so. No API change (`marshal` still returns
  the wire as a `str`).

### Testing

- `test_wire_bytes`: non-ASCII text fields and 50 random 64-byte binary
  fields (`Pb.size` equals `len(bytes(wire))`, two hex digits per byte,
  round trip); it fails with lamc 4.14 when the wire is measured with
  `len(wire)`.

## [3.0.3] - 2026-11-03

### Changed

- Compatible with `lamc` 4.x: `compatibility.lamc = ">=1.18, <5"` (test runner too).

## [3.0.2] - 2026-10-20

### Changed

- Compatible with `lamc` 3.x: `compatibility.lamc = ">=1.18, <4"` (test runner too).

## [3.0.1] - 2026-10-18

### Changed

- Compatible with `lamc` 2.x: `compatibility.lamc = ">=1.18, <3"` (the test
  runner accepts the same range). Tested with `lamc` 2.0.0; no API change.

## 3.0.0 - 2026-10-15

### Removed

- **Breaking:** removed the root `tag()` helper. The package name and version
  are declared in `lamlib.toml`, and the generic top-level function made this
  package impossible to link together with any other package (or application)
  that also declared `tag()`, because all Lam modules share one Go package.

## 2.0.0 - 2026-09-30

### Changed

- **Breaking:** Replaced the `marshal`/`tryMarshal` and
  `unmarshal`/`tryUnmarshal` twins with single `marshal -> Result[str]` and
  `unmarshal -> Result[bool]` APIs.
- Raised the minimum compatible Lammergeier compiler to 1.18 (`^1.18`).
- Updated package examples and consumer tests for typed `Result` handling.

### Testing

- Added an installed-package protobuf pipeline composing context metadata, core
  JSON, wire bytes, encryption, cloning, text conversion, and typed failures.

## 1.0.0 - 2026-09-13

### Added

- Initial standalone `@lam/protobuf` release.
- Binary protobuf encoding and decoding through `Pb.marshal`, `Pb.unmarshal`,
  `Pb.tryMarshal`, and `Pb.tryUnmarshal`.
- Standard protobuf JSON and text-format conversion helpers.
- Message equality, encoded-size calculation, and deep cloning helpers.
- Public package-root re-export for `from @lam/protobuf import Pb`.
- Consumer-style regression test using protobuf well-known types.
- `google.golang.org/protobuf v1.36.11` dependency pin and Lammergeier 1.16
  compatibility metadata.
