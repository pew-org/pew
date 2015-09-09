. (dirname (status --current-filename))/complete.fish

function pew_prompt
    if [ -n "$VIRTUAL_ENV" ]
        echo -n (set_color --bold -b blue white) (basename "$VIRTUAL_ENV") (set_color normal)" "
    end
end
