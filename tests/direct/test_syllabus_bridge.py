import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
COURSE_A = (ROOT / "fixtures" / "course_a.txt").read_text(encoding="utf-8")
COURSE_B = (ROOT / "fixtures" / "course_b.txt").read_text(encoding="utf-8")

URL_A = (
    "https://raw.githubusercontent.com/0xmojol/SyllabusBridge/"
    "refs/heads/main/fixtures/course_a.txt"
)
URL_B = (
    "https://raw.githubusercontent.com/0xmojol/SyllabusBridge/"
    "refs/heads/main/fixtures/course_b.txt"
)
HASH_A = hashlib.sha256(COURSE_A.encode("utf-8")).hexdigest()
HASH_B = hashlib.sha256(COURSE_B.encode("utf-8")).hexdigest()
PAIR_ID = "test-course-pair"


def register_example(contract, pair_id=PAIR_ID):
    return contract.register_pair(
        pair_id,
        "Introduction to Data Science",
        URL_A,
        HASH_A,
        "Applied Data Analytics",
        URL_B,
        HASH_B,
    )


def test_register_pair_and_read_open_state(direct_deploy):
    contract = direct_deploy("contracts/syllabus_bridge.py")

    result = register_example(contract)

    assert result == PAIR_ID
    pair = json.loads(contract.get_pair(PAIR_ID))

    assert pair["status"] == "OPEN"
    assert pair["pair"]["pair_id"] == PAIR_ID
    assert pair["pair"]["title_a"] == "Introduction to Data Science"
    assert pair["pair"]["title_b"] == "Applied Data Analytics"
    assert pair["pair"]["sha256_a"] == HASH_A
    assert pair["pair"]["sha256_b"] == HASH_B
    assert pair["result"] == ""


def test_duplicate_pair_id_is_rejected(direct_deploy):
    contract = direct_deploy("contracts/syllabus_bridge.py")
    register_example(contract)

    with pytest.raises(Exception, match="pair_id already exists"):
        register_example(contract)


def test_invalid_url_is_rejected_without_registration(direct_deploy):
    contract = direct_deploy("contracts/syllabus_bridge.py")

    with pytest.raises(Exception, match="HTTPS"):
        contract.register_pair(
            PAIR_ID,
            "Introduction to Data Science",
            "http://example.org/course-a.txt",
            HASH_A,
            "Applied Data Analytics",
            URL_B,
            HASH_B,
        )

    with pytest.raises(Exception, match="pair_id not found"):
        contract.get_pair(PAIR_ID)


def test_invalid_hash_is_rejected_without_registration(direct_deploy):
    contract = direct_deploy("contracts/syllabus_bridge.py")

    with pytest.raises(Exception, match="64 hexadecimal"):
        contract.register_pair(
            PAIR_ID,
            "Introduction to Data Science",
            URL_A,
            "not-a-sha256",
            "Applied Data Analytics",
            URL_B,
            HASH_B,
        )

    with pytest.raises(Exception, match="pair_id not found"):
        contract.get_pair(PAIR_ID)


def test_assessment_uses_consensus_and_stores_result(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/syllabus_bridge.py")
    register_example(contract)

    direct_vm.mock_web(
        r"https://raw\.githubusercontent\.com/0xmojol/SyllabusBridge/"
        r"refs/heads/main/fixtures/course_a\.txt",
        {"status": 200, "body": COURSE_A},
    )
    direct_vm.mock_web(
        r"https://raw\.githubusercontent\.com/0xmojol/SyllabusBridge/"
        r"refs/heads/main/fixtures/course_b\.txt",
        {"status": 200, "body": COURSE_B},
    )

    dimensions = {
        "subject": {
            "status": "OVERLAP",
            "course_a_quote": "Introduction to Data Science",
            "course_b_quote": "Applied Data Analytics",
        },
        "learning_outcomes": {
            "status": "OVERLAP",
            "course_a_quote": (
                "Students will clean datasets, apply descriptive statistics, "
                "and communicate findings using visualizations."
            ),
            "course_b_quote": (
                "Students will prepare datasets, perform statistical analysis, "
                "and present results through charts and reports."
            ),
        },
        "level": {
            "status": "OVERLAP",
            "course_a_quote": "Level: Undergraduate, intermediate",
            "course_b_quote": "Level: Undergraduate, intermediate",
        },
        "topics": {
            "status": "OVERLAP",
            "course_a_quote": (
                "Topics: Data collection, data cleaning, exploratory analysis, "
                "probability, and data visualization."
            ),
            "course_b_quote": (
                "Topics: Data preparation, exploratory analysis, applied "
                "statistics, and visualization of data."
            ),
        },
        "credits": {
            "status": "DIFFERENT",
            "course_a_quote": "Credits: 6 ECTS",
            "course_b_quote": "Credits: 5 ECTS",
        },
    }
    direct_vm.mock_llm(
        r".*",
        json.dumps({"dimensions": dimensions}),
    )

    result = json.loads(contract.assess_pair(PAIR_ID))

    assert result["pair_id"] == PAIR_ID
    assert result["outcome"] == "POTENTIAL_MATCH"
    assert result["dimensions"]["credits"]["status"] == "DIFFERENT"

    saved_pair = json.loads(contract.get_pair(PAIR_ID))
    assert saved_pair["status"] == "ASSESSED"
    assert json.loads(saved_pair["result"])["outcome"] == "POTENTIAL_MATCH"

    with pytest.raises(Exception, match="already been assessed"):
        contract.assess_pair(PAIR_ID)
