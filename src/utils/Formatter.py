from common.Singleton import Singleton


class Formatter(metaclass=Singleton):
    
    def generate_header(header_title: str, symbol: str="-", prefix_symbol: str="", postfix_symbol: str ="", max_header_len: int=100, capitalize: bool=True) -> str:
        '''
        Generates a String of `max_header_len` length, surrounded by the `prefix_symbol` on the left and `postfix_symbol` on the right of the `header_title`
        
        If `postfix_symbol` is empty String, `header_title` is surrounded by the `prefix_symbol` on both sides
        '''
        
        __padding = Formatter.__calculate_header_padding(header_title, max_header_len)
        # if symbol len > 1, adjust padding proportionally to adhere to `max_header_len`
        if len(symbol) > 1:
            __padding //= len(symbol)
        
        if capitalize:
            # force capitalize words in header title
            __formatted_title = header_title.title()
        
        else:
            # use casing passed in for `header_title`
            __formatted_title = header_title
            
        if prefix_symbol or postfix_symbol:
            __header = f"{(prefix_symbol * __padding)} {__formatted_title} {(postfix_symbol * __padding)}"
        else:
            __header = f"{(symbol * __padding)} {__formatted_title} {(symbol * __padding)}"
        
        return __header    
    
    def pad_field_label(field: str, longest_field_len: int, symbol: str ="->", alignment: str='left') -> str:
        '''
        Generates a String containing the `field` String prefixed or suffixed with whitepace padding based on the `alignment` parameter, followed by the designated `symbol`
        
        `label_alignment` can be "left", "right" or "center"
        '''
        __SEPARATING_SYMBOL = symbol
        __ALIGNMENT = alignment.lower()
        
        __padding = longest_field_len - len(field)
        # format label with whitespace padding, based on `label_alignment`
        match __ALIGNMENT:
            case "left":
                # add whitespace padding after `field` text, to align text to the left
                __label = field + f"{' ' * __padding}" + f" {__SEPARATING_SYMBOL}"
                
            case "center":
                # split whitespace padding into "left" and "right" halves, to align text in the center -- "left" padding prefixes `field` text, "right" suffixes
                __padding_left = __padding // 2
                __padding_right = __padding - __padding_left
                __label = f"{' ' * __padding_left}" + field + f"{' ' * __padding_right}" + f" {__SEPARATING_SYMBOL}"
                
            case "right":
                # add whitespace padding before `field` text, to align text to the right
                __label = f"{' ' * __padding}" + field + f" {__SEPARATING_SYMBOL}"
        
        return __label
    
    def __calculate_header_padding(header_title: str, max_header_len: int=100) -> int:
        '''
        Calculates the amount of padding that should exist around the `header_title` String to get to the `max_header_len`
        '''
        MAX_HEADER_LEN = max_header_len
        # add 2 to len for single whitespace padding around header
        __header_len = len(header_title) + 2
        
        # padding is half of difference, to account for repetition of header symbols on either side of header
        __padding = (MAX_HEADER_LEN - __header_len) // 2
        
        return __padding    