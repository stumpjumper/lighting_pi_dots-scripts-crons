# lighting_pi_dots-scripts-crons
Dot files, scripts and crontabs for RaspberryPi's used for lighting controllers at [The National Museum of Nuclear 
Science and History](http://www.nuclearmuseum.org "Nuclear Museum home page")

## To use on Nucluear Museum's Raspberry PIs

```bash
cd $HOME
git clone git@github.com:stumpjumper/lighting_pi_dots-scripts-crons.git
test -f ".bash_aliases" && mv .bash_aliases .bash_aliases.orig
test -f ".emacs" && mv .emacs .emacs.orig
ln -s lighting_pi_dots-scripts-crons/.bash_aliases_simple .bash_aliases
ln -s lighting_pi_dots-scripts-crons/.emacs_simple .emacs
mkdir bin
cd bin
ln -s ../lighting_pi_dots-scripts-crons/bin/git_commit.py git_commit
cd $HOME
```
