# todotxt-py

This is a loose, evolving collection of scripts for manipulating text todo lists in the [todotxt](http://todotxt.com) format.
I currently use it along with Dropbox and Gina Trapani's (Todotxt Touch iOS app](https://itunes.apple.com/us/app/todo.txt-touch/id491342186?ls=1&mt=8), which lets me capture todos on the go.

The way I work differs slightly from the standard todo.sh setup in that I am keeping separate text files for non-immediate items, called `next-week.txt` and `someday-maybe.txt`. I also keep a `waiting.txt` for things I need to track but aren't currently in my court.

## Motivation and Plans

I'm happy to discuss these scripts and plans for their improvement, but I don't anticipate making this an active ongoing Project with all the work that implies. I will continue to update them as I use them, but may not respond to requests about them with much speed.

# todotxt module and scripts

This stuff is not currently packaged, I just use it directly from the source dir.

There is a 'todotxt' module that supports reading and writing the file format. It does not attempt to reproduce items exactly - it always writes out projects and contexts at the end of the line regardless of where they originally occur.

Each of the scripts in this repo that use the module are referenced by simple wrapper scripts in 'actions.d' in my todo.sh setup. This is necessary if you want to use them without the `--dir` arg, since they look for `$TODO_DIR`.

## review

review.py is a simple interactive shell for reviewing your todos, one at a time. It lets you edit them, mark them as done, change priority or move them between files. 

It has two modes, 'daily', which goes through todo.txt and waiting.txt, and 'weekly', which goes through all the files.

## recap

This is a simple script that shows you what got done in the last 7 days, each day grouped by project for readability.

## archive

This is a version of the todo.sh archive action that knows about files other than todo.txt.



