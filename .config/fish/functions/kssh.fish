function kssh --description 'Select a Kubernetes pod with fzf (exec, logs, or describe)'
    set ns ""
    set mode exec
    set filter false

    # Parse arguments
    for arg in $argv
        switch $arg
            case --logs
                set mode logs
            case --describe
                set mode describe
            case --filter
                set filter true
            case '*'
                # Treat anything else as namespace
                set ns $arg
        end
    end

    # If no namespace given, pick env via fzf and set context + namespace
    if test -z "$ns"
        set env (printf "dev\nprod" | fzf --prompt="env> " --height=5)
        if test -z "$env"
            return
        end
        switch $env
            case dev
                kubectl config use-context $VST_NONPROD_CTX >/dev/null
                set ns os-analytics-api-dev
            case prod
                kubectl config use-context  $VST_PROD_CTX >/dev/null
                set ns os-analytics-api-prod
        end
    end

    # Select pod
    set pod (kubectl -n $ns get pods --no-headers \
        | fzf \
        | awk '{print $1}')

    if test -z "$pod"
        return
    end

    set -l cmd
    switch $mode
        case exec
            set cmd kubectl exec -it $pod -n $ns -- bash
        case logs
            set cmd kubectl logs -f $pod -n $ns
        case describe
            set cmd kubectl describe pod $pod -n $ns
    end

    echo $cmd
    if test "$filter" = true -a "$mode" = logs
        $cmd | grep -v -e /readyz/ -e /healthz/
    else
        $cmd
    end
end
