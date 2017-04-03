import textwrap

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = "\033[1m"


def print_bold(msg, end='\n'):
    """ print a string in 'bold' font """
    print("\033[1m" + msg + "\033[0m", end=end)

def print_welcome():
    str_welcome = '''
               AAA           UUUUUUUU     UUUUUUUUTTTTTTTTTTTTTTTTTTTTTTT     OOOOOOOOO     BBBBBBBBBBBBBBBBB        OOOOOOOOO     TTTTTTTTTTTTTTTTTTTTTTT
              A:::A          U::::::U     U::::::UT:::::::::::::::::::::T   OO:::::::::OO   B::::::::::::::::B     OO:::::::::OO   T:::::::::::::::::::::T
             A:::::A         U::::::U     U::::::UT:::::::::::::::::::::T OO:::::::::::::OO B::::::BBBBBB:::::B  OO:::::::::::::OO T:::::::::::::::::::::T
            A:::::::A        UU:::::U     U:::::UUT:::::TT:::::::TT:::::TO:::::::OOO:::::::OBB:::::B     B:::::BO:::::::OOO:::::::OT:::::TT:::::::TT:::::T
           A:::::::::A        U:::::U     U:::::U TTTTTT  T:::::T  TTTTTTO::::::O   O::::::O  B::::B     B:::::BO::::::O   O::::::OTTTTTT  T:::::T  TTTTTT
          A:::::A:::::A       U:::::D     D:::::U         T:::::T        O:::::O     O:::::O  B::::B     B:::::BO:::::O     O:::::O        T:::::T
         A:::::A A:::::A      U:::::D     D:::::U         T:::::T        O:::::O     O:::::O  B::::BBBBBB:::::B O:::::O     O:::::O        T:::::T
        A:::::A   A:::::A     U:::::D     D:::::U         T:::::T        O:::::O     O:::::O  B:::::::::::::BB  O:::::O     O:::::O        T:::::T
       A:::::A     A:::::A    U:::::D     D:::::U         T:::::T        O:::::O     O:::::O  B::::BBBBBB:::::B O:::::O     O:::::O        T:::::T
      A:::::AAAAAAAAA:::::A   U:::::D     D:::::U         T:::::T        O:::::O     O:::::O  B::::B     B:::::BO:::::O     O:::::O        T:::::T
     A:::::::::::::::::::::A  U:::::D     D:::::U         T:::::T        O:::::O     O:::::O  B::::B     B:::::BO:::::O     O:::::O        T:::::T
    A:::::AAAAAAAAAAAAA:::::A U::::::U   U::::::U         T:::::T        O::::::O   O::::::O  B::::B     B:::::BO::::::O   O::::::O        T:::::T
   A:::::A             A:::::AU:::::::UUU:::::::U       TT:::::::TT      O:::::::OOO:::::::OBB:::::BBBBBB::::::BO:::::::OOO:::::::O      TT:::::::TT
  A:::::A               A:::::AUU:::::::::::::UU        T:::::::::T       OO:::::::::::::OO B:::::::::::::::::B  OO:::::::::::::OO       T:::::::::T
 A:::::A                 A:::::A UU:::::::::UU          T:::::::::T         OO:::::::::OO   B::::::::::::::::B     OO:::::::::OO         T:::::::::T
AAAAAAA                   AAAAAAA  UUUUUUUUU            TTTTTTTTTTT           OOOOOOOOO     BBBBBBBBBBBBBBBBB        OOOOOOOOO           TTTTTTTTTTT
    '''
    info(str_welcome)


def info_green(msg, end='\n'):
    print(OKGREEN + msg + ENDC, end=end)

def info(msg, end='\n'):
    print(OKBLUE + msg + ENDC, end=end)

def warn(msg, end='\n'):
    print(WARNING + msg + ENDC, end=end)

def err(msg, end='\n'):
    print(FAIL + msg + ENDC, end=end)
