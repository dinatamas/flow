Gala Scheduler
==============

```
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.pip.txt
pip freeze > requirements.pip.txt
chmod +x scheduler.py
./scheduler.py --help
```

## Further Ideas

* add act starter / final criteria: S or F symbols
  * if not met: add something like 5 failure points

New swap heuristic:

Currently: if there is a mix between two consecutive groups,
it tries to swap the first group with another one. (We could
also extend this to check the second group..)

Another option: try to see if any other group could be inserted
inbetween them!

Also: in general we could extend these optimizations to consider
the repetitions as well, once no more mixes are found.

* Cache "good" schedules: instead of doing heuristic improvements
on completely random shuffles, we could also do random partial
shuffles of already known "close enough" schedules, and retry
heuristics after introducing those little changes.
