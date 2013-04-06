import helper
import unittest2 as unittest
from vdebug.ui.vimui.api import Vim
from mock import Mock

class VimTest(unittest.TestCase):
    def setUp(self):
        self.module = self.mock_vim()

    def mock_vim(self):
        vim_module = Mock()
        Vim.vim = vim_module
        vim_module.eval = Mock()
        vim_module.command = Mock()
        vim_module.current = Mock()
        vim_module.current.buffer = Mock()
        vim_module.current.window = Mock()
        return vim_module

    def test_current_buffer_return(self):
        self.module.eval.return_value = 3
        self.assertEqual(3, Vim.current_buffer())

    def test_current_tab_return(self):
        self.module.eval.return_value = 10
        self.assertEqual(10, Vim.current_tab())

    def test_current_buffer_name_return(self):
        self.module.current.buffer.name = "a buffer name"
        self.assertEqual("a buffer name", Vim.current_buffer_name())

    def test_current_buffer_name_call(self):
        Vim.current_buffer_name()
        self.module.current.buffer.name.assert_called()

    def test_current_buffer_eval(self):
        Vim.current_buffer()
        self.module.eval.assert_called_with("bufname('%')")

    def test_current_tab_eval(self):
        Vim.current_tab()
        self.module.eval.assert_called_with("tabpagenr()")

    def test_create_tab_command(self):
        retval = Vim.create_tab('my_buffer')
        self.module.command.assert_called_with("silent tabnew my_buffer")
        self.assertIs(Vim, retval)

    def test_create_tab_return_class(self):
        retval = Vim.create_tab('my_buffer')
        self.assertIs(Vim, retval)

    def test_current_cursor_row(self):
        self.module.current.window.cursor = [20, 50]
        self.assertEqual(20, Vim.current_cursor_row())

    def test_current_line_return(self):
        self.module.current.window.cursor = [20, 50]
        self.module.eval.return_value = 'this is the line'
        self.assertEqual('this is the line', Vim.current_line())

    def test_current_line_gets_current_cursor(self):
        self.module.current.window.cursor = [20, 50]
        Vim.current_line()
        self.module.eval.assert_called_with("getline(20)")

    def test_line_at_row_return(self):
        self.module.eval.return_value = 'this is the line'
        self.assertEqual('this is the line', Vim.line_at_row(10))

    def test_line_at_row_eval(self):
        Vim.line_at_row(10)
        self.module.eval.assert_called_with("getline(10)")

    def test_place_sign_command(self):
        Vim.place_sign(110, 'breakpt', 'the_file', 30)

        self.module.command.assert_called_with(\
            'sign place 110 name=breakpt line=30 file=the_file')

    def test_place_sign_returns_class(self):
        retval = Vim.place_sign(110, 'breakpt', 'the_file', 30)
        self.assertIs(Vim, retval)

    def test_remove_sign_command(self):
        Vim.remove_sign(110)

        self.module.command.assert_called_with('sign unplace 110')

    def test_remove_sign_command_with_string_arg(self):
        Vim.remove_sign("150")

        self.module.command.assert_called_with('sign unplace 150')

    def test_signs_of_type_breakpt(self):
        self.module.eval.return_value = """ --- Signs ---
Signs for plugin/python/vdebug/ui/vimui/ui.py:
    line=23  id=5009  name=SyntasticError
Signs for plugin/python/vdebug/ui/vimui/api.py:
    line=30  id=11000  name=breakpt
    line=38  id=11001  name=breakpt
Signs for tests/test_ui_vimui_api.py:
    line=96  id=5010  name=SyntasticError"""

        signs = Vim.signs_of_type('breakpt')
        self.assertEqual('30', signs['11000'])
        self.assertEqual('38', signs['11001'])

    def test_signs_of_type_syntastic(self):
        self.module.eval.return_value = """ --- Signs ---
Signs for plugin/python/vdebug/ui/vimui/ui.py:
    line=23  id=5009  name=SyntasticError
Signs for plugin/python/vdebug/ui/vimui/api.py:
    line=30  id=11000  name=breakpt
    line=38  id=11001  name=breakpt
Signs for tests/test_ui_vimui_api.py:
    line=96  id=5010  name=SyntasticError"""

        signs = Vim.signs_of_type('SyntasticError')
        self.assertEqual('23', signs['5009'])
        self.assertEqual('96', signs['5010'])

    def test_signs_of_type_command(self):
        Vim.signs_of_type('blargh')
        self.module.command.assert_any_call('sign place')
        self.module.eval.assert_called_with('_vdebug')

    def test_command_calls_commands(self):
        Vim.command('blargh')
        self.module.command.assert_any_call('redir => _vdebug')
        self.module.command.assert_any_call('blargh')
        self.module.command.assert_any_call('redir END')
        self.module.eval.assert_called_with('_vdebug')

    def test_error(self):
        Vim.error('this is an error')
        self.module.command.assert_called_with(\
            'echohl Error | echo "this is an error" | echohl None')

    def test_error_handles_quotes(self):
        Vim.error('this is an "error"')
        self.module.command.assert_called_with(\
            'echohl Error | echo "this is an \\"error\\"" | echohl None')

    def test_close_tab(self):
        Vim.close_tab(3)
        self.module.command.assert_called_with('silent! 3tabc!')

    def test_change_tab(self):
        Vim.change_tab(2)
        self.module.command.assert_called_with('tabn 2')

    def test_is_buffer_modified_return(self):
        self.module.eval.return_value = "1"
        self.assertEqual(True, Vim.is_buffer_modified())

    def test_is_buffer_modified_eval(self):
        self.module.eval.return_value = 0
        ret = Vim.is_buffer_modified()
        self.module.eval.assert_called_with('&mod')
        self.assertEqual(False, ret)
