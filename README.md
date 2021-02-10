# PokerPro
Simulations - Poker Simulation

By Chris Kottmyer and Shahin Shirazi

## Set-up instructions 

## Github

Install Github from this link: 
[! https://gitforwindows.org/](github.link)

Create a directory somewhere on your computer (maybe poker_pros), I do desktop usually.  I'll reference this
folder as <poker_pros_folder>.  Short cut for creating would be commandline: ``` mkdir ~/Desktop/poker_pros ```.

Go to commandline and cd into the folder.  Than create a repository local to your computer (git init) and add this online repository to 
the list of code your willing to accept (git remote add origin <url>).  You can do this using the following commands: 

```
cd <poker_pros_folder>
git init
git remote add origin https://github.com/Silber8806/PokerPro.git
```

You can download the code to the local computer using this command (git pull origin main -> download the main copy of the code):

```
git pull origin main
```

You can now use your favorite code editor inside <poker_pros_folder> to edit code and run it locally.  I like 
Visual Studio Code: https://code.visualstudio.com/.  Typically, I don't like working on the main copy of the code,
so I'll make a copy of it and work on it instead (since overwriting your main code branch is frowned upon).  
You can do this using the git checkout -b <new code name> command (note code names are unique):
  
```
git checkout -b new_code_copy
```

You can switch between any code copies (called branches) using the git checkout command without the -b flag.  To go back
to the main branch you do this:

```
git checkout main
```

If you are ever worried about what branch you are on or chnages in code, just use git status, which gives you all those details:

```
git status
```

Once you are on your code copy "new_code_copy", you can add files for github to track using the following command (you can use git status to
get the name of new files in general):

```
git add <file_name>
```

Once you have files tracked, you can change them and save changes locally using the git commit -am <message> command.  Where -m flag is just a message
describing the code change on github.  Explains the change to people viewing your code.
  
```
git commit -am "adding new feature, shuffling poker deck"
```

git commit only saves the changes locally to your active branch.  If you want to push the changes to github.com, you have to use the git push command
(below new_code_copy is the branch you are working on.  I typically use git status to make sure I'm on the right branch):

```
git push origin new_code_copy
```

In rare cases, github might complain about changes that have happened online that aren't on your local computer, you can fix this with a git pull request.

```
git pull origin new_code_copy
```

You can than just push afterwards without much problem.  To see your changes on github, just login to github.com and press the pull requests button.  You
will see your branch: new_code_copy.  If you want the new_code_copy changes to be combined with main code copy (branch) press the create pull request button
and than press merge.  Before pressing merge, you have a panel that shows all changes.  It's often good practice to make sure the changes are what you want.

Most people follow this workflow in github.  They first git pull origin main to get the most recent changes to the main branch locally.  They than create a 
new copy of the main branch: git checkout -b "my_new_code".  They make their changes incrementally, using git commit -am "message" when they are certain of
changes they want to commit and using git add <file_name> whne new files need to be added to the online repository.  They than use git push origin <new_code_name>
to push that specific branch to github.com.  They will than open a pull request, review the changes and than merge it into main.  

# Why Git?
Git tracks every file you add and change you made to your code via a set of saved points called merges.  When you merge code, it creates a SHA-256 hash representing
a unique value for that change.  At any time, you can revisit any of the save points using git checkout <hash>.  This is useful when you accidently delete useful code,
introduce a bug into production that needs to be backed out of or want to review old code you wrote to steal ideas.  Github also has markdown language and allows you
to read jupyter notebooks online in a shared environment.  Most importantly, github let's a team of 15 people work together by having each of them work on their 
own copy of code and than selectively choosing/reviewing the code that gets merged into main, which typically gets used on actual production servers. 
