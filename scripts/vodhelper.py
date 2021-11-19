#!/usr/bin/python3

import shutil
import datetime
import os
import sys
import subprocess


def replaceExtension(filename, new_ext):
    basename, _ = os.path.splitext(filename)
    return basename + new_ext


def convert_bytes(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


def get_ts_files(_dir='./'):
    ts_files = list(filter(lambda x: x[-3:] == '.ts', os.listdir(_dir)))
    ts_files = sorted(ts_files)
    return(ts_files)


def get_ts_paths(_dir='./'):
    ts_files = list(filter(lambda x: x[-3:] == '.ts', os.listdir(_dir)))
    ts_files = sorted(ts_files)
    return[os.path.join(_dir, t) for t in ts_files]


def get_ts_mp4_paths(_dir='./'):
    video_paths = list(
        filter(lambda x: x[-3:] == '.ts' or x[-4:] == '.mp4', os.listdir(_dir)))
    video_paths = sorted(video_paths)
    return [os.path.join(_dir, v) for v in video_paths]


def promptTsFiles(ts_paths):
    skipConversion = False
    for idx, ts_path in enumerate(ts_paths):
        if skipConversion:
            break
        ts = os.path.basename(ts_path)
        # print(ts_path)
        size = file_size(ts_path)
        while not skipConversion:
            prompt = f'#{idx+1}/{len(ts_paths)}\n'
            prompt += f'{ts} \nsize: {size}\n'
            prompt += 'cmds:(v)preview (r)ename (n)ext (d)elete (l)ist (s)kipConversion: '
            print('\n\n\n')
            cmd = input(prompt)
            if cmd == 'v':  # view preview in vlc
                subprocess.call(f'/usr/bin/mplayer "{ts_path}"', shell=True)
            elif cmd == 'r':  # rename
                no_extension, ext = os.path.splitext(ts)
                append_to_filename = input(f'rename to: {no_extension}')
                new_filename = no_extension + append_to_filename + ext
                os.rename(ts_path, new_filename)
                print('renamed: ', new_filename)
                ts = new_filename
                ts_path = os.path.abspath(ts)
            elif cmd == 'd':  # move to delete folder
                os.makedirs('del', exist_ok=True)
                source = ts_path
                destination = os.path.join(os.path.curdir, "del", ts)
                os.rename(source, destination)
                break
            elif cmd == 'n':  # continue to next file
                break
            elif cmd == 'l':
                print("\n".join(get_ts_files()))
            elif cmd == 's':
                skipConversion = True
            else:
                continue
    return get_ts_paths()


def addBrackets(str_):
    return f'({str_})'
    # return '[' + _str + ']'


def generateTitleString(ts_basename, tournament_name=''):
    try:
        leading_nums = ts_basename[:15]
        year = leading_nums[:4]
        month = leading_nums[4:6]
        num2month = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun',
                     '07': 'Jul', '08': 'Aug', '09': 'Sept', '10': 'Oct', '11': 'Nov', '12': 'Dec'}
        month = num2month[month]
        day = leading_nums[6:8]
        date_str = ' '.join([year, month, day])
        # if len(ts_basename) > 18:  # filename has added title
        # date_str = ' ' + date_str
        date_str = addBrackets(date_str)
        filename, ext = os.path.splitext(ts_basename)
        # if len(batch_idx) > 0:
        #     batch_idx = addBrackets(batch_idx)
        if len(tournament_name) > 0:
            tournament_name = addBrackets(tournament_name)
        return f'{filename[15:]} {date_str} {tournament_name}{ext}'
    except Exception as e:
        print(e)
        return ts_basename


# if input('do not copy+convert? x to cancel: ') != 'x':


def copyTS(ts_paths=get_ts_paths()):
    now = datetime.datetime.today()
    nTime = now.strftime("%Y-%m-%d-%f")
    customFolderName = input('output folder name?: ')
    outputFolder = f'/home/kevin/output/{" ".join([nTime, customFolderName])}'
    os.makedirs(outputFolder, exist_ok=True)
    print(nTime)
    for ts_path in ts_paths:
        source = ts_path
        destination = outputFolder
        shutil.copy(source, destination)
        print('done copying ', ts_path)
    return outputFolder
    # goto new folder and covnert c


def convert(ts_paths=get_ts_paths(), append_to_filename=''):  # makes file.mp4 in mp4 folder
    outputMP4s = []
    for idx, ts_path in enumerate(ts_paths):
        ts_dirname = os.path.dirname(ts_path)
        os.makedirs(os.path.join(ts_dirname, 'mp4'), exist_ok=True)
        # idx_no = str(idx+1).zfill(2)
        basename = os.path.basename(ts_path)
        # mp4name = generateTitleString(
        #     basename, f'{idx_no}_{len(ts_paths)}')
        mp4name = generateTitleString(
            basename, append_to_filename)

        mp4name = replaceExtension(mp4name, '.mp4')
        # figure out why not mp4 folder?
        outputPath = os.path.join(ts_dirname, 'mp4', mp4name)
        outputMP4s.append(outputPath)
        subprocess.call(
            f'ffmpeg -y -i "{ts_path}" -preset veryfast -vf scale=1280:-2 "{outputPath}"', shell=True)
    return outputMP4s


def uploadFolder(_dir='./', desc='', vis=''):
    video_paths = get_ts_mp4_paths(_dir)
    for v in video_paths:
        uploadVideo(v, desc=desc, vis=vis)


example_ts_path = '/home/kevin/test/202001251759330.ts'


print(generateTitleString(os.path.basename(example_ts_path)))


def uploadVideo(videoPath, title='', desc='', vis=''):
    if vis == 'p':
        vis = 'public'
    else:
        vis = 'unlisted'
    if len(title) == 0:
        title = os.path.splitext(os.path.basename(videoPath))[0]
    uploadCmd = f'~/scripts/youtubeuploader -oe -op "{vis}" -od "{desc}" -ot "{title}" -l -v "{videoPath}"'
    subprocess.call(uploadCmd, shell=True)


def getGlobalFlags():
    flags = dict()
    flags['doOneThing'] = False
    #flags['doOneThing'] = input('justDo [N/A]rompt [u]pload: ')
    flags['tournament_name'] = input('Tournament Name?: ')
    #flags['bracketURL'] = input('Bracket URL?: ')
    #flags['visibility'] = input('[p]ublic [u]nlisted: ')
    return flags


if __name__ == '__main__':
    print("\n".join(os.listdir()))

    flags = getGlobalFlags()
    if flags['doOneThing'] == 'u':
        uploadFolder('./', desc=flags['bracketURL'], vis=flags['visibility'])
        exit(0)
    ts_paths = get_ts_files()  # current folder ts paths
    renamed_ts_paths = promptTsFiles(ts_paths)
    copied_output_folder = copyTS(renamed_ts_paths)
    output_mp4_paths = convert(get_ts_paths(
        copied_output_folder), flags['tournament_name'])
    subprocess.call(
        f'notify-send -u critical "conversion complete {copied_output_folder}/mp4"', shell=True)

    # Disable uploads (api rate-limited too heavily)
    """
    for mp4_path in output_mp4_paths:
        uploadVideo(
            mp4_path, desc=flags['bracketURL'], vis=flags['visibility'])
    """
