export PATH=/usr/local/bin:$PATH
##################################################
# Fancy PWD display function
##################################################
# The home directory (HOME) is replaced with a ~
# The last pwdmaxlen characters of the PWD are displayed
# Leading partial directory names are striped off
# /home/me/stuff          -> ~/stuff               if USER=me
# /usr/share/big_dir_name -> ../share/big_dir_name if pwdmaxlen=20
##################################################
bash_prompt_command() {
    # How many characters of the $PWD should be kept
    local pwdmaxlen=40
    # Indicate that there has been dir truncation
    local trunc_symbol=".."
    local dir=${PWD##*/}
    pwdmaxlen=$(( ( pwdmaxlen < ${#dir} ) ? ${#dir} : pwdmaxlen ))
    NEW_PWD=${PWD/#$HOME/\~}
    local pwdoffset=$(( ${#NEW_PWD} - pwdmaxlen ))
    if [ ${pwdoffset} -gt "0" ]
    then
        NEW_PWD=${NEW_PWD:$pwdoffset:$pwdmaxlen}
        NEW_PWD=${trunc_symbol}/${NEW_PWD#*/}
    fi
}

bash_prompt() {
    case $TERM in
     xterm*|rxvt*)
         local TITLEBAR='\[\033]0;\u:${NEW_PWD}\007\]'
          ;;
     *)
         local TITLEBAR=""
          ;;
    esac
    local NONE="\[\033[0m\]"    # unsets color to term's fg color
    
    # regular colors
    local K="\[\033[0;30m\]"    # black
    local R="\[\033[0;31m\]"    # red
    local M="\[\033[0;35m\]"    # magenta
    local C="\[\033[0;36m\]"    # cyan
    local W="\[\033[0;37m\]"    # white
    local P="\[\033[0;35m\]"	# purple
    
    # emphasized (bolded) colors
    local EMB="\[\033[1;34m\]"
    local EMC="\[\033[1;36m\]"
        
    local UC=$W                 # user's color
    [ $UID -eq "0" ] && UC=$R   # root's color
    
    # prompt: colored. If you are in a git repository, the branch's name appears inside {}. Truncated to pwdmaxlen
    PS1="$TITLEBAR\n ${UC}\u${C}@${UC}\h ${EMB}\${NEW_PWD}${UC}\$(git branch 2> /dev/null | grep -e '\* ' | sed 's/^..\(.*\)/ ${M}{${W}\1${M}}/') ${EMC}\\$ ${NONE}"
}

PROMPT_COMMAND=bash_prompt_command
bash_prompt
unset bash_prompt

####################################################################################################