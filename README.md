# RSS Parser

This is a CLI application which can parse RSS items from given source.

## Installation

After downloading it ,you can install it by running the following command:

    pip install .

Now, you can run the utility by this command:

    rss_reader (*arguments*)

*OR*

1. Clone github repository:

       git clone https://github.com/Boburshoh-oss/Final_task

2. Install necessary dependencies:

       pip install -r requirements.txt
3. Now, you can run the utility by this command:

   python rss_reader.py (*arguments*)

## How to Run

To run the script you can choose from 2 ways to type in console:

1. python rss_reader.py (*arguments*)
2. rss_reader (*arguments*)

### usage:

**rss_reader** [-h] [-v] [-j] [-d DATE] [-V] [-l LIMIT] [--to-pdf] [--to-html] [source]

### positional arguments:

source RSS feed URL

### options:

      -h, --help              show this help message and exit                                   
      -v, --verbose           Show all program logs to the user.                                
      -j, --json              Print the result of the program in JSON format.                   
      -d DATE, --date DATE    Get cached news by this date.                                     
      -V, --version           Will output current version of the program and exit.              
      -l LIMIT, --limit LIMIT Specify the amount of articles shown.                             
     --to-pdf TO_PDF       Convert the results to PDF and save.
     --to-html TO_HTML     Convert the results to HTML and save.


## Logging

If `--verbose` argument is passed, then all `rss_reader` logs are printed console.

## How to Test

To test the program you need to run the following command, which will run all unit tests of the application:
```python -m unittest```

## Test Results

| Name                                        | Stmts    | Miss   | Cover    |
|---------------------------------------------|----------|--------|----------|
| rss_reader_pckg\__init__.py                 | 0        | 0      | 100%     |
| rss_reader_pckg\rss\__init__.py             | 0        | 0      | 100%     |
| rss_reader_pckg\rss\helpers.py              | 33       | 5      | 85%      |
| rss_reader_pckg\rss\html_converter.py       | 45       | 39     | 13%      |
| rss_reader_pckg\rss\pdf_converter.py        | 8        | 4      | 50%      |
| rss_reader_pckg\rss\rss_cache.py            | 62       | 35     | 44%      |
| rss_reader_pckg\rss\rss_classes.py          | 82       | 39     | 52%      |
| rss_reader_pckg\rss\rss_exception.py        | 4        | 0      | 100%     |
| rss_reader_pckg\rss\rss_parser.py           | 169      | 95     | 44%      |
| rss_reader_pckg\tests\__init__.py           | 0        | 0      | 100%     |
| rss_reader_pckg\tests\test_rss_date.py      | 21       | 1      | 95%      |
| rss_reader_pckg\tests\test_rss_parser.py    | 37       | 1      | 97%      |
| ------------------------------------------- | -------- | ------ | -------- |
| TOTAL                                       | 461      | 219    | 52%      |
