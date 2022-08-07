# Script examples


### Recommend with text

```shell
./invoke-smr.py mathematics and trigonometry functions
```

```shell
./invoke-smr.py command line interface for searching patterns in files
```

### Recommend with file input

```shell
 ./invoke-smr.py --file ./Extracted-CLI.md --smr ZefEcosystem
```

### Recommend with parsing (*WLS*)

```shell
./simple-smr-qas.wls with ZefEcosystem: find 7 recommendations for the profile dataset, summary, and reshaping | ./invoke-smr.py --pipe
```

### Recommend with image text extraction (*Shortcuts*)

```shell
shortcuts run "Photo Text Extractor" -o ~/Desktop/Extracted-CLI.md && ./invoke-smr.py --file ~/Desktop/Extracted-CLI.md
```


### Recommend with image text extraction (*WLS*)

```shell
./extract-text-from-image.wls ~/Desktop/Raku.Land-Dan-page.png | tr '\n' ' ' | sed 's/^/ --nrecs 20 --smr ZefEcosystem /' | ./invoke-smr.py --pipe
```