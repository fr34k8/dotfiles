# .zshrc

########## zsh options ##########

export LC_ALL=en_US.UTF-8
export LC_CTYPE=en_US.UTF-8
export LANG=en_US.UTF-8

setopt APPEND_HISTORY
setopt CORRECT
setopt EXTENDED_HISTORY
setopt HIST_ALLOW_CLOBBER
setopt HIST_REDUCE_BLANKS
setopt INC_APPEND_HISTORY
setopt ALL_EXPORT

setopt MENUCOMPLETE
setopt   notify globdots correct pushdtohome cdablevars autolist
setopt   correctall autocd recexact longlistjobs
setopt   autoresume histignoredups pushdsilent noclobber
setopt   autopushd pushdminus extendedglob rcquotes mailwarning
unsetopt bgnice autoparamslash

zmodload -a zsh/stat stat
zmodload -a zsh/zpty zpty
zmodload -a zsh/zprof zprof
zmodload -ap zsh/mapfile mapfile

HISTFILE=$HOME/.zhistory
HISTSIZE=10000
SAVEHIST=10000
PAGER='less'

# Colors
autoload colors zsh/terminfo
if [[ "$terminfo[colors]" -ge 8 ]]; then
colors
fi
for color in RED GREEN YELLOW BLUE MAGENTA CYAN WHITE; do
eval PR_$color='%{$terminfo[bold]$fg[${(L)color}]%}'
eval PR_LIGHT_$color='%{$fg[${(L)color}]%}'
(( count = $count + 1 ))
done
PR_NO_COLOR="%{$terminfo[sgr0]%}"

# right-hand prompt showing current dir and git branch (if in a git repo)
git_prompt_info() {
    echo `/usr/bin/ruby -e "print (%x{git branch 2> /dev/null}.grep(/^\*/).first || '').gsub(/^\* (.+)$/, '\1:')"`
}
setopt prompt_subst
PROMPT='%n@%m %# '
RPROMPT='$PR_YELLOW$(git_prompt_info)$PR_GREEN%~% $PR_NO_COLOR'

### tab autocomplete options ###
autoload -U compinit
compinit
bindkey '^r' history-incremental-search-backward
bindkey "^[[5~" up-line-or-history
bindkey "^[[6~" down-line-or-history
bindkey "^[[H" beginning-of-line
bindkey "^[[1~" beginning-of-line
bindkey "^[[F"  end-of-line
bindkey "^[[4~" end-of-line
bindkey ' ' magic-space    # also do history expansion on space
bindkey '^I' complete-word # complete on tab, leave expansion to _expand

zstyle ':completion::complete:*' use-cache on
zstyle ':completion::complete:*' cache-path ~/.zsh/cache/$HOST

zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS}
zstyle ':completion:*' list-prompt '%SAt %p: Hit TAB for more, or the character to insert%s'
zstyle ':completion:*' menu select=1 _complete _ignored _approximate
zstyle -e ':completion:*:approximate:*' max-errors \
    'reply=( $(( ($#PREFIX+$#SUFFIX)/2 )) numeric )'
zstyle ':completion:*' select-prompt '%SScrolling active: current selection at %p%s'
zstyle ':completion:*:processes' command 'ps -axw'
zstyle ':completion:*:processes-names' command 'ps -awxho command'
# Completion Styles
zstyle ':completion:*:*:kill:*:processes' list-colors '=(#b) #([0-9]#)*=0=01;31'
# list of completers to use
zstyle ':completion:*::::' completer _expand _complete _ignored _approximate

# allow one error for every three characters typed in approximate completer
zstyle -e ':completion:*:approximate:*' max-errors \
    'reply=( $(( ($#PREFIX+$#SUFFIX)/2 )) numeric )'
    
# insert all expansions for expand completer
zstyle ':completion:*:expand:*' tag-order all-expansions
#
#NEW completion:
# 1. All /etc/hosts hostnames are in autocomplete
# 2. If you have a comment in /etc/hosts like #%foobar.domain,
#    then foobar.domain will show up in autocomplete!
zstyle ':completion:*' hosts $(awk '/^[^#]/ {print $2 $3" "$4" "$5}' /etc/hosts | grep -v ip6- && grep "^#%" /etc/hosts | awk -F% '{print $2}') 
# formatting and messages
zstyle ':completion:*' verbose yes
zstyle ':completion:*:descriptions' format '%B%d%b'
zstyle ':completion:*:messages' format '%d'
zstyle ':completion:*:warnings' format 'No matches for: %d'
zstyle ':completion:*:corrections' format '%B%d (errors: %e)%b'
zstyle ':completion:*' group-name ''

# match uppercase from lowercase
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'

# offer indexes before parameters in subscripts
zstyle ':completion:*:*:-subscript-:*' tag-order indexes parameters

# command for process lists, the local web server details and host completion
#zstyle ':completion:*:processes' command 'ps -o pid,s,nice,stime,args'
#zstyle ':completion:*:urls' local 'www' '/var/www/htdocs' 'public_html'
zstyle '*' hosts $hosts

# Filename suffixes to ignore during completion (except after rm command)
zstyle ':completion:*:*:(^rm):*:*files' ignored-patterns '*?.o' '*?.c~' \
    '*?.old' '*?.pro' '*?.pyc'
# the same for old style completion
#fignore=(.o .c~ .old .pro)

# ignore completion functions (until the _ignored completer)
zstyle ':completion:*:functions' ignored-patterns '_*'
zstyle ':completion:*:scp:*' tag-order \
   files users 'hosts:-host hosts:-domain:domain hosts:-ipaddr"IP\ Address *'
zstyle ':completion:*:scp:*' group-order \
   files all-files users hosts-domain hosts-host hosts-ipaddr
zstyle ':completion:*:ssh:*' tag-order \
   users 'hosts:-host hosts:-domain:domain hosts:-ipaddr"IP\ Address *'
zstyle ':completion:*:ssh:*' group-order \
   hosts-domain hosts-host users hosts-ipaddr
zstyle '*' single-ignored show

### /tab autocomplete ###

bindkey "^[[3~" delete-char
alias screen='screen -U'
bindkey '\e[1~' beginning-of-line
bindkey '\e[4~' end-of-line




########## misc ##########


alias lstree="ls -R | grep \":$\" | sed -e 's/:$//' -e 's/[^-][^\/]*\//–/g' -e 's/^/ /' -e 's/-/|/'"

site_packages() {
    python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"
}
patch_chrome() {
    pushd /Applications/Google\ Chrome.app/Contents/MacOS/
    #if [[ "`file Google\ Chrome`" == "*Mach-O*" ]]
    #then
        mv Google\ Chrome Chrome
        touch "Google Chrome"
        chmod +x Google\ Chrome
        echo "#!/bin/sh" >> "Google Chrome"
        echo "/Applications/Google\ Chrome.app/Contents/MacOS/Chrome --disable-enforced-throttling --disk-cache-dir=/dev/null --disk-cache-size=1" >> "Google Chrome"
    #fi
    popd
    ls /Applications/Google\ Chrome.app/Contents/MacOS/
    head -c 10 /Applications/Google\ Chrome.app/Contents/MacOS/Chrome
    echo
    head -c 10 /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome
    echo
}
cleanpyc() {
    # Deletes Python bytecode from common places and the current directory tree.
    sudo find /usr/local -name "*.pyc" -o -name "*.pyo" -delete
    find ~/Code -name "*.pyc" -o -name "*.pyo" -delete
    find . -name "*.pyc" -o -name "*.pyo" -delete
}
pack_code() {
    # Packs OS X sparseimage and sparsebundle files in a couple of places.
    # (I use 'em for encrypted storage.)
    for i in `find ~/Code -name "*.sparse*"`
    do
        print
        print $i
        hdiutil compact -batteryallowed $i
    done
    for i in `find ~/Backups -name "*.sparse*"`
    do
        print
        print $i
        hdiutil compact -batteryallowed $i
    done
    for i in `find ~/Dropbox/Documents -name "*.sparse*"`
    do
        print
        print $i
        hdiutil compact -batteryallowed $i
    done
    #for i in `find ~/Library/_LocalApps -name "*.sparse*"`
    #do
    #    print
    #    print $i
    #    hdiutil compact -verbose -batteryallowed $i
    #done
}
alias sloc="find . -name \"*.css\" -o -name \"*.php\" -o -name \"*.js\" -o -name \"*.py\" -o -name \"*.sh\" | xargs wc -l"
alias s3up=s3up.py

alias 7z="/Applications/eZ\ 7z.app/Contents/Resources/7za"
alias 7za="/Applications/eZ\ 7z.app/Contents/Resources/7za"
alias 7z_make="7za a -ms=on -mx=9 -mmt=2 -t7z"

alias startmemcache="memcached -vv -m 1024 -l 127.0.0.1 -p 55838"
alias start_redis="redis-server /usr/local/etc/redis.conf"
alias start_redis_slave="redis-server /usr/local/etc/redis-slave.conf"
alias start_postgres="pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start"
alias stop_postgres="pg_ctl -D /usr/local/var/postgres stop -s -m fast"
alias start_mongo="sudo mongod run --config /usr/local/Cellar/mongodb/1.8.1-x86_64/mongod.conf"

tunnel1() {
    ssh -v2aNCD 14230 -c aes256-ctr -m hmac-ripemd160 108.59.4.65
}
tunnel2() {
    ssh -v2aNCD 14230 -c arcfour256 -m hmac-sha1 173.45.236.2
}
tunnel3() {
    ssh -v2aNCD 14230 -c aes256-ctr -m hmac-sha1 198.61.228.27
}
irctunnel() {
    ssh -v2aNCL 14240:irc.mozilla.org:6697 -c arcfour256,aes256-ctr -m hmac-sha1 173.45.236.2
}
chrome_proxied() {
    PROFTEMPDIR="/tmp/cprx-`date +\"%Y%m%d-%H%M\"`"

    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"\
    --proxy-server="socks5://127.0.0.1:9050"\
    --user-data-dir=$PROFTEMPDIR $@

    rm -fr PROFTEMPDIR
}
chrome_proxied2() {
    PROFTEMPDIR="/tmp/cprx-`date +\"%Y%m%d-%H%M\"`"

    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"\
    --proxy-server="socks5://127.0.0.1:9050"\
    --user-data-dir=$PROFTEMPDIR $@

    rm -fr PROFTEMPDIR
}
canary() {
    PROFTEMPDIR="/tmp/cprx-`date +\"%Y%m%d-%H%M\"`"

    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary"\
    --user-data-dir=$PROFTEMPDIR $@

    rm -fr PROFTEMPDIR
}
canary_proxied() {
    PROFTEMPDIR="/tmp/cprx-`date +\"%Y%m%d-%H%M\"`"

    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary"\
    --proxy-server="socks5://127.0.0.1:9050"\
    --user-data-dir=$PROFTEMPDIR $@

    rm -fr PROFTEMPDIR
}
chromium() {
    PROFTEMPDIR="/tmp/cprx-`date +\"%Y%m%d-%H%M\"`"

    "/Applications/Chromium.app/Contents/MacOS/Chromium"\
    --user-data-dir=$PROFTEMPDIR $@

    rm -fr PROFTEMPDIR
}
chromium_proxied() {
    PROFTEMPDIR="/tmp/cprx-`date +\"%Y%m%d-%H%M\"`"

    "/Applications/Chromium.app/Contents/MacOS/Chromium"\
    --proxy-server="socks5://127.0.0.1:9050"\
    --user-data-dir=$PROFTEMPDIR $@

    rm -fr PROFTEMPDIR
}
convert_x264() {
    ffmpeg -i $1 -f mp4 -threads 0 -vcodec h264 -vpre hqi -level 31 -crf 25 -acodec libfaac -ab 96k -ac 2 -async 30 -y $2
}
convert_x264_b() {
    ffmpeg -i $1 -f mp4 -threads 0 -vcodec h264 -level 31 -crf 25 -acodec libfaac -ab 96k -ac 2 -async 30 -y $2
}
pngup() {
	pngcrush -rem alla $1 $1.new &&\
	rm $1 &&\
	mv $1.new $1 &&\
	optipng -i1 -o7 $1 &&\
	s3up.py $1
}
pngcompress() {
	pngcrush -rem alla $1 $1.new &&\
	rm $1 &&\
	mv $1.new $1 &&\
	optipng -i1 -o7 $1
}
test_http_size() {
	echo "gzip"
    curl -ks -H "User-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2) Gecko/20100105 Firefox/3.6" -H "Accept-encoding: gzip, deflate" $*|wc -c
	echo "raw"
    curl -ks -H "User-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2) Gecko/20100105 Firefox/3.6" $*|wc -c
	echo "raw (headers only)"
    curl -ks -H "User-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2) Gecko/20100105 Firefox/3.6" -I $*|wc -c
}
write_signed_email() {
	cat /Users/mtigas/Documents/sig-raw.txt|mate_wait|gpg -a --clearsign|pbcopy
}
sign_clipboard() {
    echo "Signing contents of clipboard..."
    pbpaste|gpg -a --clearsign|pbcopy
}
write_email() {
	cat /Users/mtigas/Documents/sig-raw.html|mate_wait|pbcopy
}
slow_net() {
    sudo ipfw pipe 1 config bw 150KByte/s delay 200ms
    sudo ipfw add 1 pipe 1 src-port 80
}
slow_net_off() {
    sudo ipfw delete 1
}
imgup() {
    open -W -a /Applications/ImageOptim.app $1 && s3up.py $1 && rm $1
}
alias git=hub
alias imgopt="open -a /Applications/ImageOptim.app $1"

export EDITOR="mvim -f --remote-wait"
export SVN_EDITOR="mvim -f --remote-wait"

# airport no longer lives in /usr/bin or /sbin as of OSX 10.8
alias airport=/System/Library/PrivateFrameworks/Apple80211.framework/Versions/A/Resources/airport

export GPG_TTY=`tty`

###################################

# Basic path + dotfiles scripts
export PATH=/usr/local/bin:/usr/local/sbin:$PATH
export PATH=$HOME/Code/dotfiles/bin:$HOME/bin:$PATH

# system libs via Homebrew
export PATH="/usr/local/pgsql/bin:$PATH"
export PATH=/Library/Frameworks/UnixImageIO.framework/Programs:$PATH
export PATH=/Library/Frameworks/PROJ.framework/Programs:$PATH
export PATH=/Library/Frameworks/GDAL.framework/Programs:$PATH

# go
# export PATH=$PATH:$HOME/Library/_LocalApps/depot_tools:$HOME/Library/_LocalApps/go

# node
#export PATH=/usr/local/Cellar/npm/0.2.2/share/npm/bin:$PATH
#export NODE_PATH=/usr/local/Cellar/npm/0.2.2/lib/node:$NODE_PATH

# rubby
export PATH="$HOME/.rbenv/bin:$PATH"
if which rbenv > /dev/null; then eval "$(rbenv init - zsh)"; fi

# pythons
export DJANGO_SETTINGS_MODULE=localdev.settings
export PIP_RESPECT_VIRTUALENV=true
export PYTHONPATH=$HOME/Code/dotfiles/bin:$HOME/bin:$PYTHONPATH
export PATH=/usr/local/share/python:$PATH
export PATH=/usr/local/Cellar/python/2.7.3/bin:$PATH
