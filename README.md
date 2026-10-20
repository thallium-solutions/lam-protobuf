# @lam/protobuf

`@lam/protobuf` is a Protocol Buffers wire-format codec for the
[Lammergeier programming language](https://github.com/thallium-solutions/lammergeier-lang).
It wraps the official `google.golang.org/protobuf` Go implementation and exposes
binary, proto-JSON, text-format, equality, size, and cloning operations through
the static `Pb` API.

The package operates on generated Go protobuf messages. It deliberately does
not parse or compile `.proto` schemas at runtime: generate your Go message types
with `protoc`, check them into your application, and pass message pointers
through Lammergeier's `any`/`go!` boundary.

## Requirements

- `lamc` 1.18.0 or newer including 2.x (`>=1.18, <4`).
- Go and `protoc` for generating application message types.
- The package pins `google.golang.org/protobuf` to `v1.36.11`.

## Installation

Install directly from Git:

```bash
lamc install https://github.com/thallium-solutions/lam-protobuf.git@3.0.0
```

Install from a local checkout:

```bash
lamc install /path/to/lam-protobuf
```

Install the registry release:

```bash
lamc install '@lam/protobuf@2.0.0'
```

All installation methods use the manifest's canonical package name, so the
consumer import is always:

```lammergeier
from @lam/protobuf import Pb
```

## Generate message types

Given schemas under `proto/`, generate Go types as part of your normal build or
code-generation step:

```bash
protoc --go_out=. --go_opt=paths=source_relative proto/*.proto
```

The generated Go package must be importable by the Go module synthesized for
your Lammergeier application.

## Usage

The following example assumes `User` was generated from an application schema:

```lammergeier
from @lam/protobuf import Pb
from lamerrors import Result

go! {
    import myproto "github.com/me/app/proto/v1"
}

func main() {
    source: any = None
    target: any = None
    go! {
        source = &myproto.User{Name: "alice", Age: 30}
        target = &myproto.User{}
    }

    do {
        wire: str = Pb.marshal(source)?
        decoded: bool = Pb.unmarshal(wire, target)?
        print(Pb.equal(source, target))
        print(Pb.toJson(target))
        print(Pb.toText(target))
        print(Pb.size(target))
    } catch err {
        print(f"protobuf failed: {err}")
    }

    copied: any = Pb.clone(source)
    print(Pb.equal(source, copied))
}
```

Binary wire bytes are represented as a Lammergeier `str`. This preserves the
bytes across Lammergeier dictionaries and channels; use `[]byte(wire)` inside a
`go!` block when a Go byte slice is required.

## Result-aware encoding and decoding

`marshal` and `unmarshal` are the single error-aware binary codec APIs. They
work with Lammergeier's `?` and `do/catch` flow, without ambiguous empty-string
or `false` failure sentinels:

```lammergeier
from @lam/protobuf import Pb
from lamerrors import Result

go! {
    import myproto "github.com/me/app/proto/v1"
}

func main() {
    source: any = None
    target: any = None
    go! {
        source = &myproto.User{Name: "alice", Age: 30}
        target = &myproto.User{}
    }

    do {
        wire: str = Pb.marshal(source)?
        decoded: bool = Pb.unmarshal(wire, target)?
        print(decoded)
        print(Pb.equal(source, target))
    } catch err {
        print(f"protobuf failed: {err}")
    }
}
```

`marshal` returns `Result[str]` and `unmarshal` returns `Result[bool]`.
Invalid values and codec failures return a `PbError` through `Result.Err`.

## API

| Method | Behavior |
|---|---|
| `Pb.marshal(msg)` | Encodes a `proto.Message` to binary wire bytes as `Result[str]`. |
| `Pb.unmarshal(data, msg)` | Decodes into an allocated message pointer and returns `Result[bool]`. |
| `Pb.toJson(msg)` / `Pb.fromJson(json, msg)` | Uses protobuf's standard JSON mapping. |
| `Pb.toText(msg)` / `Pb.fromText(text, msg)` | Encodes and decodes protobuf text format. |
| `Pb.equal(a, b)` | Performs descriptor-aware deep message equality. |
| `Pb.size(msg)` | Returns the encoded wire size without serializing, or `-1` for an invalid value. |
| `Pb.clone(msg)` | Returns an independent deep copy, or `None` for an invalid value. |

The destination passed to `unmarshal`, `fromJson`, or `fromText`
must be an allocated pointer to the expected generated message type. Those
methods mutate the destination in place.

## Testing

The test runner checks the compiler version, stages this checkout at
`extlibs/@lam/protobuf`, compiles the migrated stdlib test as an external
consumer, runs it, and verifies every expected output line:

```bash
python3 tests/run_protobuf_tests.py --verbose
```

The manifest script provides the same command:

```bash
lamc lib run test
```

## License

`@lam/protobuf` is distributed under the Apache License, Version 2.0. See
`LICENSE`. Release notes are in `CHANGELOG.md`.
