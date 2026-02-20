function kssh --description 'Select a Kubernetes pod with fzf (exec, logs, or describe)'
    set ns os-analytics-api-dev
    set mode exec

    # Parse arguments
    for arg in $argv
        switch $arg
            case --logs
                set mode logs
            case --describe
                set mode describe
            case '*'
                # Treat anything else as namespace
                set ns $arg
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
    $cmd
end
