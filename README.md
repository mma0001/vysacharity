# Vysacharity

Automatically add a book for sale to https://vysacharity.theshop.jp

## Setup and run

It is recommended to create a virtual environment and install requirements first:

```shell
python -m venv venv
pip install -r requirements.txt
```

Then run the program with:

```shell
python main.py books add
```

For the very first run, you will be prompted to add some credentials:

- _**Client Id**_: Your application's client id, can be created at [https://developers.thebase.in/apps]().
- _**Client Secret**_: Your application's client secret, can be found at the same place as _client id_.
- _**Google CSE Id**_: Your Google Custom Search Engine's Id, can be created at 
  [https://programmablesearchengine.google.com/cse/create/new]() using a Google account.
- _**Google CSE API key**_: Your Google Custom Search Engine's API key, can be created at 
  [https://developers.google.com/custom-search/v1/overview#api_key]()

Then, you will be prompted again to add input. The program will open your default text editor and ask you to put in a 
list of book isbn and id pairs. For example:

```text
978-604-1-13690-8,KNS183
4534054696,KT116
978-0804136662,TH223
234234234234,TH8888
```

The program will go through the books one by one. In the end, if there are unprocessed books because of errors, their 
id will be returned.
