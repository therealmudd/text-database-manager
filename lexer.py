from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style
from prompt_toolkit.document import Document

# Define the style
style = Style.from_dict({
    'keyword': 'bold #ffffff',
    'text': '#ffffff',
})

# Define the lexer
class CustomLexer(Lexer):
    def __init__(self, keywords={}):
        super()
        self.keywords = keywords

    def lex_text(self, text: str):
        tokens = []
        words = text.split(' ')

        index = 0
        for word in words:
            if word.lower() in self.keywords:
                tokens.append(('class:keyword', word))
            else:
                tokens.append(('class:text', word))
            tokens.append(('class:text', ' '))
            index += len(word) + 1

        return lambda i: tokens

    def lex_document(self, document: Document):
        return self.lex_text(document.text)

# Prompt the user
def main():
    session = PromptSession(lexer=CustomLexer(), style=style)
    while True:
        user_input = session.prompt('> ')
        if user_input.lower() in {'exit', 'quit'}:
            break

if __name__ == '__main__':
    main()
