# @lam/protobuf Changelog

All notable changes to `@lam/protobuf` are documented here.

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
