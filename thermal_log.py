import subprocess
from time import sleep, time
from sys import argv
from os import path, getcwd, mkdir
from model import DEVICE_MODEL
from graphic import save_chart


def check_activity_alive():
    get_activity_cmd = adb_shell.format("dumpsys activity activities | sed -En -e '/Running activities/,/Run #0/p'")
    get_activity_cmd2 = adb_shell.format("dumpsys activity | grep mFoc")
    activiy = 'com.yiqizuoye.library.ailesson.AILessonActivity'
    activiy2 = 'loader.a.ActivityN1STNTS'
    exec_obj = subprocess.Popen(get_activity_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    exec_obj2 = subprocess.Popen(get_activity_cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    exec_obj.wait()
    exec_obj2.wait()
    while 1:
        get_line = exec_obj.stdout.readline().decode('utf-8')
        get_line2 = exec_obj2.stdout.readline().decode('utf-8')
        if activiy in get_line or activiy2 in get_line:
            return True
        if activiy in get_line or activiy2 in get_line2:
            return True
        if get_line == '' and get_line2 == '':
            return False


def filename_check(name):
    """
    检查当前操作目录下的csv/目录下是否存在同名文件
    :param name: 文件名
    :return: 文件绝对路径
    """
    # 文件名格式化以及路径拼接
    filename = name
    if filename[-4:] != '.csv':
        filename = filename + '.csv'
    filepath = getcwd() + '/csv/' + filename

    # 同名文件检查，存在则退出
    if path.exists(filepath):
        exit('文件已存在')

    return filepath


if __name__ == '__main__':
    # 目录存在检查，不存在则创建
    if not path.exists(getcwd() + '/csv'):
        mkdir(getcwd() + '/csv')

    # 参数检查
    if len(argv) == 1:
        print('{:_^80}'.format(''))
        print('{:^80}'.format('AI lesson thermal monitor'))
        print('{:.^80}'.format(''))
        print('此脚本可以监控AILesson运行过程中的发热情况并导出csv文件到操作目录下的csv/目录下')
        print('在adb正确连接手机后启动此脚本')
        print('    用法：')
        print('        python3 thermal_log.py 要生成的温度记录文件名 [-c]')
        print('        其中参数-c为可选，效果：activity结束时自动结束温度监控')
        print('\n`此脚本需要adb并需要为adb正确配置环境变量')
        print('``保证正确连接一个设备且仅能连接一个目标设备后再启动脚本')
        print('_' * 80)
        exit(1)

    # 文件重名检测并生成输出文件的绝对路径
    filename = argv[1]
    filepath = filename_check(filename)

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
    while 1:
        if check_activity_alive():
            break
        sleep(1)

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
        temp = exec_obj.stdout.readline().decode('utf-8').replace('\n', '').replace('\r', '')
        return_code = exec_obj.wait()

        if return_code == 0:
            fmt_temp = '{:.3f}'.format(int(temp)/1000.0)
            print('\r当前温度：{:<8} °C'.format(fmt_temp), end='')
            with open(filepath, 'a+', encoding='utf-8') as f:
                f.write(str(time() - start_time) + ',' + temp + '\n')
        elif 'error: no devices/emulators found' in temp:
            print('\n发生错误，可能是数据线没有插紧')
            print(temp)
            sleep(2)
            # 这个continue的目的是避免后面检查activity的命令执行失败误认为activity已退出
            continue

        # 检查activity是否退出，如果指定了-c参数，activity退出则测温结束
        activity_alive = True
        if 'c' in argv[-1]:
            if not check_activity_alive():
                print('\nactivity已退出，程序结束')
                break

        sleep(2)

    pic_path = getcwd() + '/pic/' + filename + '.svg'
    if not path.exists(getcwd() + '/pic/'):
        mkdir(getcwd() + '/pic/')
    save_chart(pic_path, filepath)
