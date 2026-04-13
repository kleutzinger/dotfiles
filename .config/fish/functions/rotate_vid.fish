function rotate_vid --description 'Rotate or flip a video using ffmpeg'
    if test (count $argv) -lt 1
        echo "Usage: rotate_vid <video_file>"
        return 1
    end

    set input $argv[1]

    if not test -f $input
        echo "File not found: $input"
        return 1
    end

    echo "Choose transformation:"
    echo "1) Rotate 90° clockwise"
    echo "2) Rotate 180°"
    echo "3) Rotate 270° clockwise"
    echo "4) Horizontal flip"
    echo "5) Vertical flip"

    read -P "Enter choice [1-5]: " choice

    switch $choice
        case 1
            set filter "transpose=1"
        case 2
            set filter "transpose=1,transpose=1"
        case 3
            set filter "transpose=2"
        case 4
            set filter hflip
        case 5
            set filter vflip
        case '*'
            echo "Invalid choice"
            return 1
    end

    set filename (basename $input)
    set ext (string split -r -m1 . $filename)[2]
    set name (string split -r -m1 . $filename)[1]

    set output "$name"_rotated."$ext"

    echo "Processing..."
    ffmpeg -i "$input" -vf "$filter" -c:a copy "$output"

    if test $status -eq 0
        echo "Done: $output"
    else
        echo "Error during processing"
    end
end
