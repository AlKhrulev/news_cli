# news_cli

A simple CLI that allows you to get top daily news for the topic of interest in json format

## Motivation

I needed a script that could allow me to get the news for any topic for free. For now, the priority was to write a parser, get the news, and then do processing later. For ex. , I am thinking about scheduling a `cron` job and piping the output to send it to my Telegram bot.

## Dependencies

I wanted to use a minimum number of dependencies, so its' only

1. `requests` (everyone should have it installed already anyway)
2. `pytest` (only if you want to run tests via `python -m pytest tests.py`)
3. `requests-cache` (optional, only if caching is desired)

## Sample Usage

```{shell}
usage: News Crawler [-h] --topic TOPIC [--version] [--article_count ARTICLE_COUNT] [--timeout TIMEOUT] [--cache]
```

Example:

`NEWS_KEY='your key' python news_cli.py -t 'topic one' -t 'topic 2...'`

or

`python news_cli.py -t 'topic one' -t 'topic 2...'` if `NEWS_KEY` is set already

## FAQ

### Q. Where to get the API key?

**A.** Go [here](https://gnews.io)

### Q. What if I want to use a different API?

**A.** Go [here](https://github.com/public-apis/public-apis#news) to choose a different one

### Q. Why do you just print the raw `json` output to `stdout`?

**A.** I want to do processing later, and this allows me to pipe the output to any command line script

### Q. Why overwrite the `type` arg in the parser?

**A.** The intention is to exit on parsing failure instead of parsing all args and do checks later. `type` allows you to do exactly that

### Q. Why are your custom functions for `type` look complicated?

**A.** `type` argument can be a function that accepts a single string argument. If you want to customize it for you liking, you have to wrap it up into a decorator or a different function. I went for a latter approach for ease of usage
