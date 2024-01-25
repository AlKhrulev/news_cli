from __future__ import annotations
from argparse import ArgumentParser, ArgumentTypeError
from typing import Callable  # to indicate a function type hint
from os import environ
from sys import stderr
from pprint import pprint
import json
import requests

# consider checking https://github.com/public-apis/public-apis#news for other options
BASE_URL = "https://gnews.io/api/v4/search"


def verify_str_length(
    lower: int = 0, upper: int = 255
) -> Callable[[list[str]], list[str]]:
    """A wrapper that allows to specify the length bounds for every
    string in a list. Returns a wrapper function because the 'type'
    function in Argparse must accept only 1 argument.

    :param lower: lower len str bound, defaults to 0
    :type lower: int, optional
    :param upper: lower len str bound, defaults to 255
    :type upper: int, optional
    :return: a function that accepts a list of strs and validates them
        based on the specified bounds in the outer function
    :rtype: Callable[[list[str]], list[str]]
    """

    def inner(argument_value_list: list[str]) -> list[str]:
        """Either returns the same input if all strings in a list
        have the length between the specified bounds or raises
        an ArgumentTypeError if any of the checks fail.
        Kind of like list(filter(lambda x: x<=lower or x>= upper, argument_value_list))
        but raises the error if any of checks fails.

        :param argument_value_list: contains strings to validate
        :type argument_value_list: list[str]
        :raises ArgumentTypeError: if len of any str in argument_value_list<=lower bound
        :raises ArgumentTypeError: if len of any str in argument_value_list>=upper bound
        :return: unchanged list
        :rtype: list[str]
        """
        for raw_text in argument_value_list:
            if len(raw_text) <= lower:
                raise ArgumentTypeError(
                    f"Argument length can't be lower than {lower-1} chars but got \n\t{len(raw_text)} chars for {raw_text=!r}"
                )
            if len(raw_text) >= upper:
                raise ArgumentTypeError(
                    f"Argument length can't be higher than {upper+1} chars but got \n\t{len(raw_text)} chars for {raw_text=!r}"
                )
        return argument_value_list

    return inner


def verify_int_range(lower: int = 0, upper: int = 10) -> Callable[[str], int]:
    """Checks if an int represented by a string lies
    between lower and upper(inclusively). Returns a function that does
    checks based on the specified bound.
    upper defaults to 10 due to the free API topic limit. For other
    arguments, it makes sense to use different upper/lower limits.

    :param lower: lower bound to check(inclusively), defaults to 0
    :type lower: int, optional
    :param upper: upper bound to check(inclusively), defaults to 10
    :type upper: int, optional
    :return: a function that accept a str to be converted to int and
        have the bounds verified
    :rtype: Callable[[str], int]
    """

    def inner(raw_argument_value: str) -> int:
        # has to be done because we manually rewrite the default 'int' type definition
        # that would take care of the following try-except block
        try:
            count = int(raw_argument_value)
        except ValueError as e:
            raise ArgumentTypeError(
                f"Got the following error while converting from str to int:\n\t{e!r}"
            )

        if count <= lower:
            raise ArgumentTypeError(
                f"value must not be less than {lower-1} but you provided {raw_argument_value!r}"
            )
        if count >= upper:
            raise ArgumentTypeError(
                f"value must not be greater than to {upper+1} but you provided {raw_argument_value!r}"
            )

        return count

    return inner


def create_parser() -> ArgumentParser:
    """Create a parser with 3 arguments, --topic, --article_count, and --timeout.
    At least 1 topic is required.
    Topic(s) will be verified for length as we don't want to accept very long strings(by default
    from 1 to 255 characters), while article_count and timeout must be ints by default
    between 1 and 10(10 is a free API limit) or 0 and 60(i.e. 1 min), respectively.

    :return: initialized parser
    :rtype: ArgumentParser
    """
    description = """
A simple command line program to get current news for any topic of interest in a JSON format"""
    parser = ArgumentParser(prog="News Crawler", description=description)
    parser.add_argument(
        "--topic",
        "-t",
        action="append",
        type=verify_str_length(),  # if no error a list of strs
        help="the topic(s) to look for",
        required=True,
    )  # a list of topics
    parser.add_argument("--version", "-v", action="version", version="%(prog)s 1.0")
    parser.add_argument(
        "--article_count",
        "-c",
        type=verify_int_range(),  # if no error an int
        action="store",
        default=10,
        help="the number of articles to return. Defaults to 10.",
    )
    parser.add_argument(
        "--timeout",
        action="store",
        type=verify_int_range(upper=60),  # up to 60s of connection delay allowed
        default=10,
        help="delay in seconds to wait before termination if the connection can't be established. Defaults to 10 s",
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    print(f"args are {args}")

    if not "NEWS_KEY" in environ:
        print(
            """
              No API key "NEWS_KEY" set in the environment.
              Go to # https://gnews.io/ to get your key.
              Exiting...""",
            file=stderr,
        )
        exit(22)  # corresponds to errno 22 EINVAL

    query = " ".join(list(args.topic))

    payload = {
        "q": query,
        "lang": "en",
        "country": "us",  # 'ca' is supported as well
        "max": str(
            args.article_count
        ),  # 10 articles is a limit for free API(already set by default)
        "apikey": environ["NEWS_KEY"],
    }

    response = requests.get(url=BASE_URL, params=payload)
    # to view the url, simply access response.url

    # raise an error if status code is in 4XXs or 5XXs
    response.raise_for_status()

    data = response.json()
    pprint(data)
    # can pipe to whatever we want to and access via sys.stdin.read()


if __name__ == "__main__":
    main()
