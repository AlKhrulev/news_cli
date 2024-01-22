from __future__ import annotations
from news_cli import create_parser
from argparse import Namespace  # the class of parsed args
import pytest

# defaults for reference
sample_article_count = 10
sample_timeout = 10
sample_topic = "test"  # must provide at least 1 topic; the name has to be a valid non-empty str

# P.S. A little bit tricky to test ArgumentParser as even when ArgumentTypeError is raised
# manually it is caught internally and SystemExit is raised instead


class TestClass:
    parser = create_parser()  # no point in recreating the same parser multiple times

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            (
                "1",
                Namespace(
                    topic=[sample_topic], article_count=sample_article_count, timeout=1
                ),
            ),
            (
                "20",
                Namespace(
                    topic=[sample_topic], article_count=sample_article_count, timeout=20
                ),
            ),
        ],
    )
    def test_timeout_parsing(self, test_input: str, expected: Namespace):
        to_compare: Namespace = TestClass.parser.parse_args(
            f"-t {sample_topic} --timeout {test_input}".split()
        )
        assert to_compare == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            (
                "1",
                Namespace(
                    topic=[sample_topic], article_count=1, timeout=sample_timeout
                ),
            ),
            (
                "5",
                Namespace(
                    topic=[sample_topic], article_count=5, timeout=sample_timeout
                ),
            ),
        ],
    )
    def test_count_parsing(self, test_input: str, expected: Namespace):
        to_compare: Namespace = TestClass.parser.parse_args(
            f"-t {sample_topic} -c {test_input}".split()
        )
        assert to_compare == expected

    @pytest.mark.parametrize("test_input", [("a"), ("a1"), ("1a")])
    def test_timeout_non_int(self, test_input: str):
        """tests trying to pass non-int timeout(should fail)"""
        with pytest.raises(SystemExit):
            TestClass.parser.parse_args(
                f"-t {sample_topic} --timeout {test_input}".split()
            )

    @pytest.mark.parametrize("test_input", [("a"), ("a1"), ("1a")])
    def test_count_non_int(self, test_input: str):
        """tests trying to pass non-int counts(should fail)"""
        with pytest.raises(SystemExit):
            TestClass.parser.parse_args(f"-t {sample_topic} -c {test_input}".split())

    @pytest.mark.parametrize("test_input", [("61"), ("1000"), ("-200")])
    def test_timeout_bounds_exception(self, test_input: str):
        """tests passing timeouts that are not in the allowed bounds
        (ex. too large or negative)"""
        # if an exception is raised, the bounds are rejected
        with pytest.raises(SystemExit):
            TestClass.parser.parse_args(
                f"-t {sample_topic} --timeout {test_input}".split()
            )

    @pytest.mark.parametrize("test_input", [("26"), ("1000"), ("-200")])
    def test_count_bounds_exception(self, test_input: str):
        """tests passing counts that are not in the allowed bounds
        (ex. too large or negative)"""
        # if an exception is raised, the bounds are rejected
        with pytest.raises(SystemExit):
            TestClass.parser.parse_args(f"-t {sample_topic} -c {test_input}".split())

    def test_no_topic_provided(self):
        """tests if a required arg is not provided"""
        with pytest.raises(SystemExit):
            TestClass.parser.parse_args([])

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            (
                "-t a -t b",
                Namespace(
                    topic=["a", "b"],
                    article_count=sample_article_count,
                    timeout=sample_timeout,
                ),
            ),
            (
                "--topic a -t b",
                Namespace(
                    topic=["a", "b"],
                    article_count=sample_article_count,
                    timeout=sample_timeout,
                ),
            ),
            (
                "-t a --topic b",
                Namespace(
                    topic=["a", "b"],
                    article_count=sample_article_count,
                    timeout=sample_timeout,
                ),
            ),
            (
                "--topic a --topic b",
                Namespace(
                    topic=["a", "b"],
                    article_count=sample_article_count,
                    timeout=sample_timeout,
                ),
            ),
        ],
    )
    def test_multiple_topic_provided(self, test_input: str, expected: Namespace):
        """tests if the parse can accurately parse multiple topics"""
        to_compare: Namespace = TestClass.parser.parse_args(test_input.split())
        assert to_compare == expected
