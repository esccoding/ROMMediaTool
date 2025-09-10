from common.Singleton import Singleton

class TextColor(metaclass=Singleton):
    # SGR color constants
    """ ANSI color codes """
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    WHITE = "\033[0;37m"
    BOLD_BLACK = "\033[1;30m"
    BOLD_RED = "\033[1;31m"
    BOLD_GREEN = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_BLUE = "\033[1;34m"
    BOLD_PURPLE = "\033[1;35m"
    BOLD_CYAN = "\033[1;36m"
    BOLD_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"

    def run_unit_test():
        print(f"{TextColor.BLACK}Text colored BLACK{TextColor.END}")
        print(f"{TextColor.RED}Text colored RED{TextColor.END}")
        print(f"{TextColor.GREEN}Text colored GREEN{TextColor.END}")
        print(f"{TextColor.YELLOW}Text colored YELLOW{TextColor.END}")
        print(f"{TextColor.BLUE}Text colored BLUE{TextColor.END}")
        print(f"{TextColor.PURPLE}Text colored PURPLE{TextColor.END}")
        print(f"{TextColor.CYAN}Text colored CYAN{TextColor.END}")
        print(f"{TextColor.WHITE}Text colored WHITE{TextColor.END}")
        print(f"{TextColor.BOLD_BLACK}Text colored BOLD_BLACK{TextColor.END}")
        print(f"{TextColor.BOLD_RED}Text colored BOLD_RED{TextColor.END}")
        print(f"{TextColor.BOLD_GREEN}Text colored BOLD_GREEN{TextColor.END}")
        print(f"{TextColor.BOLD_YELLOW}Text colored BOLD_YELLOW{TextColor.END}")
        print(f"{TextColor.BOLD_BLUE}Text colored BOLD_BLUE{TextColor.END}")
        print(f"{TextColor.BOLD_PURPLE}Text colored BOLD_PURPLE{TextColor.END}")
        print(f"{TextColor.BOLD_CYAN}Text colored BOLD_CYAN{TextColor.END}")
        print(f"{TextColor.BOLD_WHITE}Text colored BOLD_WHITE{TextColor.END}")
        print(f"{TextColor.BOLD}BOLD text{TextColor.END}")
        print(f"{TextColor.FAINT}FAINT text{TextColor.END}")
        print(f"{TextColor.ITALIC}ITALIC text{TextColor.END}")
        print(f"{TextColor.UNDERLINE}UNDERLINE text{TextColor.END}")
        print(f"{TextColor.BLINK}BLINK text{TextColor.END}")
        print(f"{TextColor.NEGATIVE}NEGATIVE text{TextColor.END}")
        print(f"{TextColor.CROSSED}CROSSED text{TextColor.END}")