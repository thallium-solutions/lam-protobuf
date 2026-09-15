# @lam/protobuf Changelog

All notable changes to `@lam/protobuf` are documented here.

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
