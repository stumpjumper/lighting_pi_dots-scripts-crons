# lighting_pi_dots-scripts-crons
Dot files, scripts and crontabs for RaspberryPi's used for lighting controllers at [The National Museum of Nuclear 
Science and History](http://www.nuclearmuseum.org "Nuclear Museum home page")

## To use on Nucluear Museum's Raspberry PIs

```bash
cd $HOME
mv .bash_aliases .bash_aliases.orig
mv .emacs .emacs.orig
ln -s lighting_pi_dots-scripts-crons/.bash_aliases_simple .bash_aliases
ln -s lighting_pi_dots-scripts-crons/.emacs_simple .emacs
```