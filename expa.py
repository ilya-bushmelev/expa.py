#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# *   _____  ___ __   __ _   _ __  _   _ 
# *  / _ \ \/ / '_ \ / _` | | '_ \| | | |
# * |  __/>  <| |_) | (_| |_| |_) | |_| |
# *  \___/_/\_\ .__/ \__,_(_) .__/ \__, |
# *           |_|           |_|    |___/


#   +-----------<(EN)>------------+ +-----------<(RU)>------------+
#   | Simple EXpression PArser    | | Простой парсер выражений    |
#   | "eval, but safe"            | | "eval, но безопасный"       |
#   |                             | |                             |
#   | Created by: Ilya Bushmelev  | | Создано: Илья Бушмелев      |
#   +-----------------------------+ +-----------------------------+

# -- Imports --
import re
import sys

# -- Main class --
class Expa:
    """
    Simple EXpression PArser
    Простой парсер выражений
    """
    def __init__(self):
        self._pos = 0
        self._tokens: list[str|int] = []
        self._re_tokens = r'\d+\.\d*|\.\d+|\d+|//|\*\*|[-+*/^()]'
    def tokenize(self, expression):
        """
        Convert expression into tokens (letter and other symbol will be ignored)
        Превратить пример в токены (буквы и др. символы игнорируются)
        """
        token_pattern = re.compile(self._re_tokens)
        tokens = token_pattern.findall(expression)
        return tokens
    def _is_at_end(self) -> bool: 
        return self._pos >= len(self._tokens)
    def peek(self):
        """
        View the current token
        Посмотреть текущий токен
        """
        if self._is_at_end():
            return None
        return self._tokens[self._pos]
    def consume(self,expected_token=None):
        """
        Consume current token and go to next
        Съесть текущий токен и перейти на следующий
        """
        token = self.peek()
        if expected_token and token != expected_token:
            raise SyntaxError(f"Unexpected token | Неожиданный токен: {self.peek()}")
        self._pos += 1
        return token
    # Anonymous functions
    # Анонимные функции
    def _parse_expression(self):
        if not self._tokens: return None
        left = self._parse_term()
        while self.peek() in ['+','-']:
            op = self.consume()
            right = self._parse_term()
            left = ('OP',op,left,right)
        return left
    def _parse_term(self):
        left = self._parse_unary()
        while self.peek() in ['*','/','//']:
            op = self.consume()
            right = self._parse_unary()
            left = ('OP',op,left,right)
        return left
    def _parse_unary(self):
        if self.peek() == '-':
            self.consume('-')
            factor = self._parse_unary()
            return ('UN', '-', factor)
        else:
            return self._parse_power()
    def _parse_power(self):
        left = self._parse_factor()
        if self.peek() in ['**','^']:
            op = self.consume()
            right = self._parse_power()
            left = ('OP',op,left,right)
        return left
    def _parse_factor(self):
        if self.peek() == '(':
            self.consume('(')
            result = self._parse_expression()
            self.consume(')')
            return result
        elif self.peek() is not None:
            try:
                value = float(self.peek())
                self.consume()
                return ('NUM', value)
            except ValueError:
                raise SyntaxError(f"Неожиданный токен: {self.peek()}")
        else:
            raise SyntaxError(f"Unexpected token | Неожиданный токен: {self.peek()}")
    def parse(self, tokens: list[str|int]):
        """
        Parse tokens into the tree
        Парсит токены в дерево
        """
        self._pos = 0
        self._tokens = tokens
        tree = self._parse_expression()
        if not self._is_at_end():
            raise SyntaxError(f"Unexpected token | Лишний токен: {self.peek()}")
        return tree
    def evaluate(self,node):
        """
        Evaluate result using tree
        Вычислить результат используя дерево
        """
        if node is None: return None
        if node[0] == 'NUM':
            return node[1]
        if node[0] == 'UN':
            op = node[1]
            factor = self.evaluate(node[2])
            if op == '-':
                return -factor
        if node[0] == 'OP':
            op = node[1]
            left = self.evaluate(node[2])
            right = self.evaluate(node[3])
            if op == '+': return left + right
            if op == '-': return left - right
            if op == '*': return left * right
            if op == '/':
                if right == 0: raise ZeroDivisionError() 
                return left / right
            if op == '//':
                if right == 0: raise ZeroDivisionError()
                return left // right
            if op in ['^','**']: 
                if abs(right) > 100:
                    raise OverflowError("Exponent too large | Показатель слишком большой")
                return left ** right
    def format_result(self, result):
        """
        Convert 10.0 into 10, while leaving 10.123 as is.
        Превращает 10.0 в 10, а 10.123 оставляет как есть.
        """
        if isinstance(result, float) and result.is_integer():
            return int(result)
        return float(f"{result:.10g}") if isinstance(result, float) else result
    def __call__(self, expression:str, force: bool=False):
        if expression is None:
            return
        if len(expression) > 50_000:
            raise ValueError("Expression too long, force execute impossible. | Выражение слишком длинное, выполнение невозможно.")
        elif len(expression) > 10_000 and not force:
            raise ValueError("Expression too long, to force execute set force to True. | Выражение слишком длинное, установите флаг force на True для принудительного выполнения")
        token = self.tokenize(expression)
        if len(token) > 20_000:
            raise ValueError("Too many tokens. | Слишком много токенов")
        try:
            tree = self.parse(token)
            pre_result = self.evaluate(tree)
        except RecursionError:
            raise SyntaxError("Expression too deeply nested. | Выражение слишком глубоко вложено.")
        
        result = self.format_result(pre_result)
        return result
    def interactive(self):
        """
        Start interctive shell
        Запустить интерактивную оболочку
        """
        print("Type 'exit' to leave. | Введите 'exit' чтобы выйти")
        while True:
            try:
                expression = input(">>> ")
                # RESERVED
                # before = expression.split(maxsplit=1)[0].lower().strip()
                # after = expression.split(maxsplit=1)[1]
                try:
                    if expression == 'exit':
                        break
                    # elif before == "token":
                    #     print(self.tokenize(after))
                    # elif before == "tree":
                    #     print(self.parse(list(after)))
                    # elif before == "evaluate":
                    #     print(self.format_result(self.evaluate(after)))
                    else:
                        result = self(expression)
                        if result is None: continue
                        print(result)
                except IndexError:
                    print("token/tree/evaluate require expression,tokens,tree after")
            except (KeyboardInterrupt, EOFError):
                return
            except Exception as e:
                print(type(e).__name__ + (": " + str(e) if str(e) else ''))

# Creating an instance from template (class)
# Создаём экземпляр с шаблона (класса)
expa = Expa()

# Starts if executed main file (expa.py)
# Запускается если запущен главный файл (expa.py)
def main():
    if sys.argv[1:]:
        print(expa(' '.join(sys.argv[1:])))
    else:
        expa.interactive()
if __name__ == '__main__':
    main()