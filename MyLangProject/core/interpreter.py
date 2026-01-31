import re
from locales.manager import t


class Interpreter:
    def __init__(self, console_callback):
        self.console_callback = console_callback

    def execute(self, code):
        lines = code.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue

            success = self.process_line(stripped, i + 1, line)
            if not success:
                break

    def process_line(self, command, line_num, original_line):
        # 1. Простая проверка команды
        full_match = re.match(r'^текст\s*\((["\'])(.*?)\1\)$', command)

        if full_match:
            content = full_match.group(2)
            self.console_callback(content)
            return True

        # 2. Анализ ошибок
        return self.analyze_error(command, line_num, original_line)

    def analyze_error(self, command, line_num, original_line):
        error_msg = t.get("unknown_command")
        col_index = 0

        # Упрощенная логика анализа (как в прошлом примере)
        if command.startswith("текст"):
            if "(" not in command:
                col_index = len("текст")
                error_msg = "Expected '('"
            else:
                quote_match = re.search(r"['\"]", command)
                if not quote_match:
                    col_index = command.find("(") + 1
                    error_msg = "Expected quote"
                else:
                    quote_char = quote_match.group()
                    start_quote_idx = quote_match.start()
                    end_quote_idx = command.find(quote_char, start_quote_idx + 1)

                    if end_quote_idx == -1:
                        col_index = len(command)
                        error_msg = t.get("unterminated_string")
                    elif not command.endswith(")"):
                        col_index = len(command)
                        error_msg = t.get("expected_bracket")

        # --- ВОТ ТУТ ЛОКАЛИЗАЦИЯ ОШИБКИ ---
        indent_len = len(original_line) - len(original_line.lstrip())
        pointer = " " * (indent_len + col_index) + "^"

        # Используем t.get() для слов "Файл" и "строка"
        file_label = t.get("error_file")
        line_label = t.get("error_line")

        formatted_error = (
            f'\n  {file_label} "main.mylang", {line_label} {line_num}\n'
            f'    {original_line}\n'
            f'    {pointer}\n'
            f'{t.get("syntax_error")}: {error_msg}\n'
        )

        self.console_callback(formatted_error, is_error=True)
        return False