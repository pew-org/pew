_pew()
{
    local cur prev words cword args commands
    _init_completion || return
    args="--help --python -i -a -r"
    commands="ls add mkproject rm lssitepackages cp workon new mktmpenv setproject show wipeenv sitepackages_dir inall toggleglobalsitepackages"

    case $prev in
        ls|show|rm|workon|cp|setproject)
            COMPREPLY=( $(compgen -W "$(pew-ls)" -- ${cur}) )
            return 0
            ;;
        inall)
            _command_offset 2
            return 0
            ;;
        mktmpenv|new)
            COMPREPLY=( $(compgen -W "${args}" -- ${cur}) )
            return 0
            ;;
        mkproject)
            COMPREPLY=( $(compgen -W "${args} -t --list" -- ${cur}) )
            return 0
            ;;
        add)
            COMPREPLY=( $(compgen -W "--help -d" -- ${cur}) )
            return 0
            ;;
    esac
    
    COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )

} &&
complete -F _pew pew
