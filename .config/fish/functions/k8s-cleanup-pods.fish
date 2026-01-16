function k8s-cleanup-pods
    set pods (kubectl -n os-analytics-api-dev-namespace get pods --no-headers -o custom-columns=":metadata.name")
    if count $pods
        echo "Pods in os-analytics-api-dev-namespace:"
        printf '%s\n' $pods
        read -P "Delete ALL these pods? (y/N): " answer
        if test "$answer" = y
            kubectl -n os-analytics-api-dev-namespace delete pod $pods
        else
            echo "Aborted."
        end
    else
        echo "No pods found in the namespace."
    end
end
