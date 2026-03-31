# C Docs

Convert C documentation to JSON for easy lookup.

The contents of [data](./data) are from a
    [locally-hosted copy of DevDocs](https://github.com/freecodecamp/devdocs?tab=readme-ov-file#using-docker-recommended),
    which are then parsed into a JSON mapping each documented entity to its parsed documentation via
    [main.py](./main.py).

## Obtaining the Documentation JSON

Run the following:

```sh
% make run
% chmod +x main.py
% ./main.py data/index.json --exclude-type macro --exclude-type other --exclude-type type
```
