#!/usr/bin/python
# print bash commands

print """
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxx Commands I often forget xxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

--- file without file ending ---
for i in *.end; do echo ${i%\.*}; done

--- list content in tar.gz file ---
tar -ztvf file.tar.gz

--- extract specific file ---
tar --extract --file=file.tar.gz filename 

--- add line after line ---
sed '/patternstring/ a\\
new line string' file1

--- replace only the first occurence in a file ---
sed '0,/replace/{s/replace/new_string/}' file

--- number of lines in a directory ---
ls -1 targetdir | wc -l

--- stdout and stderr during run is ---
--- located on the running node in  ---  
/var/spool/torque/spool/


xxxxxxxxxxxxxxxxxxxx
xxx git commands xxx
xxxxxxxxxxxxxxxxxxxx

git bisect start
git bisect bad
git bisect good
git bisect reset
git co master; git merge --squash --ff tmp_branch

--- create new branch ---
git push origin <new_branch>

--- delete branch remotely ---
git push origin --delete <branch-name>

--- if submodules has been moved ---
git submodule sync

--- rewrite last (unpushed) commit message ---
git commit --amend

"""

print "find . -type f -print0 | xargs -0 sed -i -c 's/\-lt/\-ne/g'"
print "sh -x 2013-05-28T*/*.check 2013-05-28T*/*.log"
