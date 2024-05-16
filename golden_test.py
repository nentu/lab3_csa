"""Golden тесты транслятора и машины.

Конфигурационнфе файлы: "golden/*_bf.yml"
"""

import contextlib
import io
import json
import logging
import os
import tempfile

import control_unit
import pytest
import translator


@pytest.mark.golden_test("golden/*.yml")
def test_translator_and_machine(golden, caplog):
    # Установим уровень отладочного вывода на DEBUG
    caplog.set_level(logging.DEBUG)

    # Создаём временную папку для тестирования приложения.
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Готовим имена файлов для входных и выходных данных.
        source = os.path.join(tmpdirname, "source.asm")
        input_stream = os.path.join(tmpdirname, "input.txt")
        target = os.path.join(tmpdirname, "target.za")

        # Записываем входные данные в файлы. Данные берутся из теста.
        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["in_source"])
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["in_stdin"])

        # Запускаем транслятор и собираем весь стандартный вывод в переменную
        # stdout
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main(source, target)
            control_unit.main(target, input_stream)

        # Выходные данные также считываем в переменные.
        with open(target, encoding="utf-8") as file:
            code = file.read()

        # Проверяем, что ожидания соответствуют реальности.
        assert json.loads(code) == json.loads(golden.out["out_code"])
        assert stdout.getvalue() == golden.out["out_stdout"]
        assert caplog.text == golden.out["out_log"]
