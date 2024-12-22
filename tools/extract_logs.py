from datetime import datetime

from configs import settings

log_file_path = settings.BASE_DIR + '/logs/18.12-22.12.log'


class Bcolors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    GRAY = '\033[90m'
    RESET = '\033[0m'


def snowman_logs(user_id: int):
    previous_time = datetime.now()
    previous_delay = 0
    with (open(log_file_path, 'r+') as log_file):
        c = 0

        data = {
            'blocked_count': 0,
            'white_action': 0,
            'red_action': 0,
            'yellow_action': 0
        }

        for line in log_file:
            if f'tg_user_id:{user_id}' in line and 'snowman' in line:
                timestamp_str = line.split()[0] + " " + line.split()[1]
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")

                time_delta = timestamp - previous_time
                sec = float(f'{time_delta.seconds}.{time_delta.microseconds}')

                if 'updates the snowman with height_increased: -1' in line:
                    print(f'{Bcolors.GRAY}{c}. delay: {sec:.2f} | {line.strip()}{Bcolors.RESET}')
                    continue

                if abs(previous_delay - sec) <= 0.1:
                    str_delay = f'{Bcolors.RED}{sec:.2f}{Bcolors.RESET}'
                    data['red_action'] += 1

                elif 0.1 < abs(previous_delay - sec) < 0.2:
                    str_delay = f'{Bcolors.YELLOW}{sec:.2f}{Bcolors.RESET}'
                    data['yellow_action'] += 1

                else:
                    str_delay = f'{sec:.2f}'
                    data['white_action'] += 1

                if 'blocked' in line:
                    data['blocked_count'] += 1

                c += 1

                print(f'{c}. delay: {str_delay} | {line.strip()}')

                previous_time = timestamp
                previous_delay = sec

        data['total'] = c

        for i in ('white_action', 'red_action', 'yellow_action'):
            data[i] = [data[i], f'{(data[i] / data['total']):.0%}']

        print(
            f'\nTotal actions: {data["total"]}',
            f'\nBlocked actions: {data["blocked_count"]}',
            f'\nWhite actions: {data["white_action"][0]} ({data["white_action"][1]})',
            f'\nRed actions: {data["red_action"][0]} ({data["red_action"][1]})',
            f'\nYellow actions: {data["yellow_action"][0]} ({data["yellow_action"][1]})'
        )


telegram_user_id = 0
snowman_logs(telegram_user_id)
