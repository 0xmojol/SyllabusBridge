# SyllabusBridge

SyllabusBridge is a GenLayer Intelligent Contract for comparing two public course descriptions and recording a consensus-based, preliminary assessment of their academic overlap.

It is an informational comparison tool. It does **not** make or replace an official university decision about credit transfer.

## How it works

1. A user registers two courses with their titles, HTTPS syllabus URLs, and SHA-256 hashes of the expected page contents.
2. A reviewer requests an assessment.
3. The contract independently fetches both pages and checks that their contents match the registered hashes.
4. The leader assesses the courses across subject matter, learning outcomes, academic level, topics, and credits where available.
5. Validators independently check the fetched content and assessment evidence. The contract records a result only when the GenLayer consensus process accepts it.

## Possible outcomes

- `POTENTIAL_MATCH` — strong overlap is indicated.
- `PARTIAL_MATCH` — some meaningful overlap is indicated.
- `NO_MATCH` — the available descriptions indicate little or no overlap.
- `UNCLEAR` — evidence is insufficient or the result cannot be established reliably.

## Scope and limitations

- The contract compares one pair of courses per assessment.
- It relies on the content available at the supplied HTTPS URLs and on the registered content hashes.
- A consensus result is a preliminary comparison, not accreditation, legal advice, or an official credit-transfer decision.
- If a syllabus page changes, its content hash must match the version being assessed.

## Development and deployment

This project is intended for deployment and testing as a GenLayer Intelligent Contract. The contract source and Studio instructions will be added as the implementation is prepared.

## Status

Early development. The contract has not yet been deployed or tested in GenLayer Studio.
