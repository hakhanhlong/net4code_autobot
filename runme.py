from os.path import join, dirname
from dotenv import load_dotenv
from ultils import stringhelpers
from fang.mega import MegaManager
from fang.ironman import IronManManager
from fang.flask import FlaskManager


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def main():



    stringhelpers.print_welcome()
    _mega_manager = MegaManager('MEGA-MANAGEMENT', False)
    _mega_manager.start()

    '''_flask_manager = FlaskManager('FLASK-MANAGEMENT', False)
    _flask_manager.start()

    _ironman_manager = IronManManager('IRONMAN-MANAGEMENT', False)
    _ironman_manager.start()'''


if __name__ == '__main__':
    main()
