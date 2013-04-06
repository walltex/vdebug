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

    def test_place_breakpoint_sign_command(self):
        Vim.place_breakpoint_sign(110, 'the_file', 30)

        self.module.command.assert_called_with(\
            'sign place 110 name=breakpt line=30 file=the_file')

    def test_place_breakpoint_sign_returns_class(self):
        retval = Vim.place_breakpoint_sign(110, 'the_file', 30)
        self.assertIs(Vim, retval)
