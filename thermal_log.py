import subprocess
from time import sleep, time
from sys import argv
from os import path, getcwd, mkdir
from model import DEVICE_MODEL
from graphic import save_chart

if __name__ == '__main__':
    # 目录存在检查，不存在则创建
    if not path.exists(getcwd() + '/csv'):
        mkdir(getcwd() + '/csv')

    # 参数检查
    if len(argv) == 1:
        print('----AI lesson温度监控脚本----')
        print('    用法：')
        print('        python3 thermal_log.py 温度记录文件名 [-c]')
        print('        其中参数-c为可选，效果：activity结束时自动结束温度监控')

    # 文件名格式化以及路径拼接
    filename = argv[1]
    if filename[-4:] != '.csv':
        filename = filename + '.csv'
    filepath = getcwd() + '/csv/' + filename

    # 同名文件检查，存在则退出
    if path.exists(filepath):
        exit('文件已存在')

    # 机型监测
    adb_shell = 'adb shell {}'
    model = ''
    exist = False
    print('detecting model...', end='')
    for k, v in DEVICE_MODEL.items():
        type_path = v[0] + '/type'
        exec_obj = subprocess.Popen(adb_shell.format('cat ' + type_path),
                                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        get_model = exec_obj.stdout.readline().decode('utf-8').replace('\n', '')
        if v[1] == get_model:
            print('  {}'.format(k))
            model = k
            exist = True
            break

    if not exist:
        exit('不支持的机型')

    # 监控activity是否启动
    print('等待activity启动...')
    activiy = 'com.yiqizuoye.library.ailesson.AILessonActivity'
    activiyOK = False
    while 1:
        get_activity_cmd = adb_shell.format("dumpsys activity activities | sed -En -e '/Running activities/,/Run #0/p'")
        exec_obj = subprocess.Popen(get_activity_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while 1:
            get_line = exec_obj.stdout.readline().decode('utf-8')
            if activiy in get_line:
                activiyOK = True
                print('\n已发现：\ncom.yiqizuoye.library.ailesson.AILessonActivity')
                break
            if get_line == '':
                print('\ractivity未启动，等待中...', end='')
                break
        if activiyOK:
            break

    # 创建文件
    with open(filepath, 'w', encoding='utf  -8') as f:
        f.write('time,thermal\n')

    # 拼接查询activity的命令
    get_thermal_cmd = adb_shell.format('"cat {}/temp"'.format(DEVICE_MODEL[model][0]))
    print('Thermal file is {}/temp'.format(DEVICE_MODEL[model][0]))

    # 开始时间戳
    start_time = time()

    while 1:
        exec_obj = subprocess.Popen(get_thermal_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        temp = exec_obj.stdout.readline().decode('utf-8').replace('\n', '')
        return_code = exec_obj.wait()

        if return_code == 0:
            int_temp = str(int(temp)/1000.0)
            print('\r当前温度：{:<8} °C'.format(int_temp), end='')
            with open(filepath, 'a+', encoding='utf-8') as f:
                f.write(str(time() - start_time) + ',' + temp + '\n')
        elif 'error: no devices/emulators found' in temp:
            print('\n发生错误，可能是数据线没有插紧')
            print(temp)
            # 这个continue的目的是避免后面检查activity的命令执行失败误认为activity已退出
            sleep(2)
            continue

        # 检查activity是否退出，如果指定了-c参数，activity退出则测温结束
        if 'c' in argv[-1]:
            get_activity_cmd = adb_shell.format("dumpsys activity activities | sed -En -e '/Running activities/,/Run #0/p'")
            exec_obj = subprocess.Popen(get_activity_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            return_code = exec_obj.wait()
            out = exec_obj.stdout.readlines()
            if return_code != 0:
                print('\nactivity 状态获取错误！')
                continue
            activiyAlive = False
            for line in out:
                if 'com.yiqizuoye.library.ailesson.AILessonActivity' in line.decode('utf-8'):
                    activiyAlive = True
                    break
            if not activiyAlive:
                for line in out:
                    print(line.decode('utf-8').replace('\n', ''))
                print('\nactivity已退出，程序结束')
                break
        sleep(2)

    pic_path = getcwd() + '/pic/' + filename + '.svg'
    if not path.exists(getcwd() + '/pic/'):
        mkdir(getcwd() + '/pic/')
    save_chart(pic_path, filepath)
