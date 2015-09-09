fpath=( ${0:a:h} "${fpath[@]}" )
compinit

autoload -U colors && colors

_venv=$(basename "$VIRTUAL_ENV")
PS1="%{$fg_bold[blue]%}$_venv${_venv:+ }$reset_color$PS1"

# be sure to disable promptinit if the prompt is not updated
