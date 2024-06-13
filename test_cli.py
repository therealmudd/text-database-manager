import unittest
from unittest.mock import patch, MagicMock
import cli
updated: 2024-06-11 21:39:40

class TestCLI(unittest.TestCase):
    @patch('cli.PromptSession')
    @patch('cli.tbm.TextDatabase')
    def test_help_command(self, MockTextDatabase, MockPromptSession):
        # Mocking the PromptSession to simulate user input
        MockPromptSession.return_value.prompt.return_value = 'help'
        
        with patch('builtins.print') as mocked_print:
            cli.main()
            mocked_print.assert_any_call(cli.help_text)

    @patch('cli.PromptSession')
    @patch('cli.tbm.TextDatabase')
    def test_tables_command(self, MockTextDatabase, MockPromptSession):
        # Mocking the PromptSession to simulate user input
        MockPromptSession.return_value.prompt.return_value = 'tables'
        
        # Mocking the TextDatabase.list_tables method
        MockTextDatabase.return_value.list_tables.return_value = 'table1\ntable2'

        with patch('builtins.print') as mocked_print:
            cli.main()
            mocked_print.assert_any_call('table1\ntable2')

    @patch('cli.PromptSession')
    @patch('cli.tbm.TextDatabase')
    def test_create_command(self, MockTextDatabase, MockPromptSession):
        # Mocking the PromptSession to simulate user input
        MockPromptSession.return_value.prompt.side_effect = ['create test with col1,col2', 'tables', 'quit']
        
        mock_db = MockTextDatabase.return_value
        mock_db.check_table_exists.return_value = False

        with patch('builtins.print') as mocked_print:
            cli.main()
            mock_db.add_table.assert_called_with('test', 'col1,col2')
            mocked_print.assert_any_call(mock_db.list_tables())

    @patch('cli.PromptSession')
    @patch('cli.tbm.TextDatabase')
    def test_view_command(self, MockTextDatabase, MockPromptSession):
        # Mocking the PromptSession to simulate user input
        MockPromptSession.return_value.prompt.side_effect = ['view test', 'quit']

        mock_db = MockTextDatabase.return_value
        mock_db.check_table_exists.return_value = True
        mock_db.view_table.return_value = 'row1\nrow2'

        with patch('builtins.print') as mocked_print:
            cli.main()
            mock_db.view_table.assert_called_with('test')
            mocked_print.assert_any_call('row1\nrow2')

    @patch('cli.PromptSession')
    @patch('cli.tbm.TextDatabase')
    def test_delete_command(self, MockTextDatabase, MockPromptSession):
        # Mocking the PromptSession to simulate user input
        MockPromptSession.return_value.prompt.side_effect = ['delete test', 'quit']

        mock_db = MockTextDatabase.return_value
        mock_db.check_table_exists.return_value = True

        cli.main()
        mock_db.delete_table.assert_called_with('test')

    @patch('cli.PromptSession')
    @patch('cli.tbm.TextDatabase')
    def test_insert_command(self, MockTextDatabase, MockPromptSession):
        # Mocking the PromptSession to simulate user input
        MockPromptSession.return_value.prompt.side_effect = ['insert row into test', 'quit']

        mock_db = MockTextDatabase.return_value

        cli.main()
        mock_db.add_row_to_table.assert_called_with('test', 'row')

if __name__ == '__main__':
    unittest.main()
