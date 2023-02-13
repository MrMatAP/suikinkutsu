#  MIT License
#
#  Copyright (c) 2022 Mathieu Imfeld
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import pytest
import json
import yaml

from suikinkutsu.outputs import OutputSeverity, OutputEntry, HumanWaterOutput, JSONWaterOutput, YAMLWaterOutput


@pytest.mark.parametrize('severity', list(OutputSeverity))
def test_human_output_strings(severity: OutputSeverity, config, capsys):
    output = HumanWaterOutput(config)
    entry = OutputEntry(msg=f'Message at severity {severity.value}', severity=severity, code=201)
    output.print(entry)

    captured = capsys.readouterr()
    assert captured.out == f'* [{entry.code}] {entry.msg}\n', 'The rendered output matches the OutputEntry'
    assert captured.err == '', 'No stderr output is received'


@pytest.mark.parametrize('severity', list(OutputSeverity))
def test_human_output_obj(severity: OutputSeverity, config, capsys):
    output = HumanWaterOutput(config)
    entry = OutputEntry(msg=[['one', 'two'], ['four', 'five']],
                        columns=['col1', 'col2'],
                        title='Test',
                        severity=severity,
                        code=201)
    output.print(entry)
    captured = capsys.readouterr()
    assert f'[{entry.severity.value}] {entry.title} - {entry.code}' in captured.out
    for col in entry.columns:
        assert col in captured.out, 'Output contains desired column'
    for row in entry.msg:
        for cell in row:
            assert cell in captured.out, 'Output contains desired cell'
    assert captured.err == '', 'No stderr output is received'


@pytest.mark.parametrize('severity', list(OutputSeverity))
def test_json_output_strings(severity: OutputSeverity, config, capsys):
    output = JSONWaterOutput(config)
    entry = OutputEntry(msg=f'Message at severity {severity.value}', severity=severity, code=201)
    output.print(entry)

    captured = capsys.readouterr()
    json_out = json.loads(captured.out)
    assert json_out.get('code') == entry.code, 'The rendered code matches the OutputEntry'
    assert json_out.get('msg') == entry.msg, 'The rendered msg matches the OutputEntry'
    assert json_out.get('severity') == entry.severity.value, 'The rendered severity matches the OutputEntry'
    with pytest.raises(json.decoder.JSONDecodeError):
        json_err = json.loads(captured.err)


@pytest.mark.parametrize('severity', list(OutputSeverity))
def test_json_output_obj(severity: OutputSeverity, config, capsys):
    output = JSONWaterOutput(config)
    entry = OutputEntry(msg=[['one', 'two'], ['four', 'five']],
                        columns=['col1', 'col2'],
                        title='Test',
                        severity=severity,
                        code=201)
    output.print(entry)
    captured = capsys.readouterr()
    json_out = json.loads(captured.out)
    assert json_out['severity'] == entry.severity.value
    assert json_out['title'] == entry.title
    assert json_out['code'] == entry.code
    assert json_out['msg'] == dict(zip(entry.columns, entry.msg))
    with pytest.raises(json.decoder.JSONDecodeError):
        json_err = json.loads(captured.err)


@pytest.mark.parametrize('severity', list(OutputSeverity))
def test_yaml_output_strings(severity: OutputSeverity, config, capsys):
    output = YAMLWaterOutput(config)
    entry = OutputEntry(msg=f'Message at severity {severity.value}', severity=severity, code=201)
    output.print(entry)

    captured = capsys.readouterr()
    yaml_out = yaml.safe_load(captured.out)
    assert yaml_out['code'] == entry.code, 'The rendered code matches the OutputEntry'
    assert yaml_out['msg'] == entry.msg, 'The rendered msg matches the OutputEntry'
    assert yaml_out['severity'] == entry.severity.value, 'The rendered severity matches the OutputEntry'
    assert captured.err == '', 'There is no output on stderr'


@pytest.mark.parametrize('severity', list(OutputSeverity))
def test_yaml_output_obj(severity: OutputSeverity, config, capsys):
    output = JSONWaterOutput(config)
    entry = OutputEntry(msg=[['one', 'two'], ['four', 'five']],
                        columns=['col1', 'col2'],
                        title='Test',
                        severity=severity,
                        code=201)
    output.print(entry)
    captured = capsys.readouterr()
    yaml_out = yaml.safe_load(captured.out)
    assert yaml_out['severity'] == entry.severity.value
    assert yaml_out['title'] == entry.title
    assert yaml_out['code'] == entry.code
    assert yaml_out['msg'] == dict(zip(entry.columns, entry.msg))
