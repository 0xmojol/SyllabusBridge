# SyllabusBridge

SyllabusBridge is a GenLayer Intelligent Contract for comparing two public course descriptions and recording a preliminary, consensus-backed assessment of their academic overlap.

It is an informational comparison tool. It does **not** make or replace an official university decision about credit transfer.

## How it works

1. Register a pair of courses with titles, HTTPS URLs, and SHA-256 hashes of the exact page contents.
2. Call `assess_pair` for the registered pair.
3. The leader and validators independently fetch both pages.
4. The contract checks that the fetched bytes match the registered SHA-256 hashes.
5. The leader assesses the course descriptions across subject, learning outcomes, level, topics, and credits.
6. Validators independently assess the same source material and check that the leader's evidence quotes occur in the fetched documents.
7. The accepted assessment and its outcome are stored on-chain.

## Possible outcomes

- `POTENTIAL_MATCH` — at least four dimensions show overlap and none are unclear.
- `PARTIAL_MATCH` — one or more dimensions show overlap, but fewer than four.
- `NO_MATCH` — no dimensions show overlap and none are unclear.
- `UNCLEAR` — at least one dimension cannot be assessed reliably.

Each dimension is assessed as `OVERLAP`, `DIFFERENT`, or `UNCLEAR`. Evidence quotes must match text in the corresponding source document.

## Contract interface

- `register_pair(...)` — registers a unique pair of courses, their HTTPS URLs, and their SHA-256 hashes.
- `assess_pair(pair_id)` — fetches both hash-pinned documents, requests an independent semantic assessment, and stores the consensus result.
- `get_pair(pair_id)` — reads the registered pair, its status, and its assessment result.

## State design and validation

The contract stores registered course-pair records, assessment results, and each pair's status (`OPEN` or `ASSESSED`).

Input checks include unique pair identifiers, bounded title and URL lengths, HTTPS-only URLs, and 64-character hexadecimal SHA-256 values. Assessment checks include successful page fetches, matching content hashes, bounded document size, valid result labels, and exact evidence quotes grounded in each fetched document.

The assessment is informational. Consensus does not establish institutional accreditation, source authorship, or eligibility for credit transfer.

## Test fixtures

The repository includes two fixed text fixtures used for the Studio test:

- [Course A](fixtures/course_a.txt)
- [Course B](fixtures/course_b.txt)

The contract was tested with the registered pair `syllabus-test-001`. The result was `POTENTIAL_MATCH`; the credit dimension was `DIFFERENT` because the sample courses list 6 ECTS and 5 ECTS.

## Automated tests

The direct test suite covers pair registration and retrieval, duplicate ID rejection, invalid URL and hash rejection, and consensus assessment with result persistence.

Run locally with:

    python -m pip install -r requirements.txt
    pytest tests/direct/ -v

GitHub Actions runs the direct test suite automatically on pushes and pull requests targeting `main`. These direct-mode tests use mocked web and LLM responses; they complement, but do not replace, the successful GenLayer Studio end-to-end test documented below.

## GenLayer Studio deployment

- Contract: `SyllabusBridge`
- Contract address: [`0xE0271C8932A7A99A7857ab60F4979751f6Fc157D`](https://explorer-studio.genlayer.com/address/0xE0271C8932A7A99A7857ab60F4979751f6Fc157D)
- Deployment transaction: [Finalized deployment](https://explorer-studio.genlayer.com/tx/0x00d5d5a4fc9884770f94c67bde3db91243d8104e9149d4a1f3f6462a589ba48a)
- Code upgrade: [Finalized upgrade](https://explorer-studio.genlayer.com/tx/0xe482af4670bda4e41a4e44e809a7e63591bfcb5d1fca34fbadb8c7f2caf9f3bc)
- Pair registration: [Accepted transaction](https://explorer-studio.genlayer.com/tx/0x6503fe87578a6ddcbe1b1dc16361a582de2588e8600cc57998b493571500daca)
- Successful assessment: [Accepted transaction](https://explorer-studio.genlayer.com/tx/0x1ccb0e5c6c3a6b6f469e168b685e625ff8632963a0540f892f61f8f0889ce3f7)

## Limitations

- Results depend on the content available at the supplied HTTPS URLs and the registered content hashes.
- If a page changes, its hash must be updated by registering a new pair.
- A consensus-backed comparison is not an official university decision, legal advice, or a guarantee of credit transfer.
