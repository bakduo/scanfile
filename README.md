Scan by thread with Python
=========================

# For example scan very large folder with different sizeof files

 * it's neccesary clamscan and python-concurrent.futures installed.
 * generate a list of files
 * run app.

```
listfile.txt

/x/y//z/a/b/c/1.pdf
/x/y//z/a/b/c/2.pdf
/x/y//z/a/b/c/3.pdf
/x/y//z/a/b/c/4.pdf
/x/y//z/a/b/c/5.pdf
/x/y//z/a/b/c/6.pdf
/x/y//z/a/b/c/7.pdf
/x/y//z/a/b/c/8.pdf

python scanfile.py -f listfile.txt -w n-thread

```

The scanner split the work by worker load.
