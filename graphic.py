import pandas as pd
from os import getcwd
from sys import argv
import matplotlib.pyplot as plt


def save_chart(save_path, data_path, annotate=None):
    data = pd.read_csv(data_path)
    data['thermal'] = data['thermal'] / 1000.0

    highest_index = data['thermal'].idxmax()
    highest_point = (data['time'].iloc[highest_index], data['thermal'].iloc[highest_index])
    start_point = (data['time'].iloc[0], data['thermal'].iloc[0])

    data.plot.line(x=data.columns[0], y=data.columns[1], linewidth=1.0)
    title = 'Temperature chart'
    if annotate:
        title += ' ({})'.format(annotate)
    plt.title(title)
    plt.xlabel('{:<40}time/s{:>40} s'.format('', 'Totally:{:.1f}'.format(data['time'].iloc[-1])))
    plt.ylabel('temperature/°C')
    plt.ylim(32, 65)
    plt.annotate(
        'highest\n{:.1f}°C'.format(highest_point[1]),
        xy=highest_point,
        xytext=(highest_point[0] - data['time'].iloc[-1] * 0.05, highest_point[1] * 0.93),
        bbox=dict(boxstyle="round", fc="w", ec="r"),
        arrowprops=dict(arrowstyle="<-", connectionstyle="arc"),
    )
    plt.annotate(
        'start\n{:.1f}°C'.format(start_point[1]),
        xy=start_point,
        xytext=(start_point[0] + data['time'].iloc[-1] * 0.15, start_point[1]),
        bbox=dict(boxstyle="round", fc="w", ec="blue"),
        arrowprops=dict(arrowstyle="<-", connectionstyle="arc"),
    )
    plt.grid()
    plt.savefig(save_path)
    print(save_path)
    plt.close()


if __name__ == '__main__':
    if len(argv) < 2:
        exit('参数错误')

    cur_path = getcwd()
    filename = argv[1]

    # fig = plt.figure()
    # ax = fig.add_subplot(1, 1, 1)
    # ax.set_xlabel('time/s')
    # ax.set_ylabel('temperature/°C')
    if len(argv) == 3:
        if argv[2] == '-r':
            print('实时模式')
            plt.ion()
            plt.title('最近一分钟内的记录')
            count = 0
            while(1):
                data = pd.read_csv(cur_path + '/' + filename).tail(30)
                data['thermal'] = data['thermal'] / 1000.0
                plt.cla()
                plt.plot(data['time'].values, data['thermal'].values, linewidth=1.0)
                last_point = (data['time'].values[-1], data['thermal'].values[-1])
                plt.annotate(
                    'current:\n{:.1f}°C'.format(last_point[1]),
                    xy=last_point,
                    xytext=(last_point[0] + 3, last_point[1]),
                    bbox=dict(boxstyle="round", fc="w", ec="r"),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc"),
                )
                print('\r第{}次刷新'.format(count), end='')
                count += 1
                plt.show()
                plt.pause(2)

    elif len(argv) == 4 and argv[2] == '-a':
        save_path = getcwd() + '/pic/' + argv[1].split('/')[-1] + '.svg'
        save_chart(save_path, argv[1], argv[3])

    elif len(argv) == 2:
        save_path = getcwd() + '/pic/' + argv[1].split('/')[-1] + '.svg'
        print('pic saved at ' + save_path)
        save_chart(save_path, argv[1])
