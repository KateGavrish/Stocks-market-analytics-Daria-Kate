import schedule
from shutil import rmtree
from os.path import abspath
from os import mkdir


def clear_excel():
    rmtree(abspath('static/excel'))
    mkdir('static/excel')


schedule.every().hour.at(':00').do(clear_excel)
while True:
    schedule.run_pending()
