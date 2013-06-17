#CONSTANTS:
dit = 1
dah = 2
#END CONSTANTS


class char():
    def __init__(self, name, left=None, right=None):
        self.name = name
        self.left = left
        self.right = right

#MORE CONSTANTS
tree = (
char('start',
    char('t',
        char('m',
            char('o',
                char('-',
                    char('0'),
                    char('9'),
                ),
                char('.',
                    None,
                    char('8'),
                ),
            ),
            char('g',
                char('q'),
                char('z',
                    None,
                    char('7'),
                ),
            ),
        ),
        char('n',
            char('k',
                char('y'),
                char('c'),
            ),
            char('d',
                char('x'),
                char('b',
                    None,
                    char('6'),
                ),
            ),
        ),
    ),
    char('e',
        char('a',
            char('w',
                char('j',
                    char('1'),
                    None,
                ),
                char('p'),
            ),
            char('r',
                None,
                char('l'),
            ),
        ),
        char('i',
            char('u',
                char('-',
                    char('2'),
                    None,
                ),
                char('f'),
            ),
            char('s',
                char('v',
                    char('3'),
                    None,
                ),
                char('h',
                    char('4'),
                    char('5'),
                ),
            ),
        ),
    ),
))
#END MORE CONSTANTS


def decode(characterList):
    #the error variable marks if the character is not known by the decoding program
    error = False
    #if the length of the 'letter' is more than five dits or dahs, it can't be right so it immediatly sets error to true
    if len(characterList) > 5:
        error = True
    #possible is a recursively narrowing down list of possible characters
    location = tree
    for character in characterList:
        #if there is any cause for error, error is true, so it immediately returns as unknown
        if error:
            return '?'
        if character == dit:
            location = location.right
        elif character == dah:
            location = location.left
        else:
            #if any character lacks a 'dit or 'dot', trigger an error. Other causes for error could be more than 5 characters, or 5 characters if they do not signify a character
            error = True
        if location is None:
            error = True
    if error:
        return '?'
    return location.name
