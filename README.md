Kitkatch
===

### Install Mac OS:

1. `brew install ssdeep`
2. `python3 -m venv venv && . venv/bin/activate` 
3. `pip install -r requirements.txt`

### Run 1 URL

1. `python -m kitkatch -url http://localhost/foo/bar/baz/ -f text` 


### Run URLFile

1. `python -m kitkatch -url-file /path/to/urls.txt -f text`


### Notes

1. All data will be saved to a `./loot` directory from where you ran Kitkatch. You can specify a separate loot directory via `loot-dir`
2. `python -m kitkatch -h` for other flags
3. Files/paths will be saved in the URI. So, if a URL is `foobar.com/dir1/dir2/dir3/`, then Kitkatch will make a directory `loot/foobar.com` and put corresponding dir structures there. so `loot/foobar.com/dir1/dir2/dir3` with pages
4. As of now, it only finds compressed files and forms. 
5. Check out `loot/report TIME.json` for a report of the run at the time specified. I recommend using `jq` to parse -> `brew install jq; cat loot/report TIME.json | jq '.'`
