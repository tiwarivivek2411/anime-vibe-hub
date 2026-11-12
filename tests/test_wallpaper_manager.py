import builtins
import os
import sys
from unittest import mock

# Ensure the project root is in sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from wallpaper_manager import update_wallpaper, choose_image, download_image

# Mock get_anime_image to return deterministic URLs
@mock.patch('wallpaper_manager.get_anime_image')
@mock.patch('wallpaper_manager.set_wallpaper')
@mock.patch('wallpaper_manager.download_image')
def test_update_wallpaper_flow(mock_download, mock_set_wallpaper, mock_get_image, monkeypatch):
    # Prepare mock returns
    mock_get_image.side_effect = [
        'https://example.com/image1.jpg',
        'https://example.com/image2.jpg',
        'https://example.com/image3.jpg'
    ]
    mock_download.return_value = '/tmp/image1.jpg'
    mock_set_wallpaper.return_value = True

    # Simulate user choosing the second image
    monkeypatch.setattr(builtins, 'input', lambda _: '2')

    result = update_wallpaper()
    assert result is True
    # Ensure get_anime_image called three times
    assert mock_get_image.call_count == 3
    # Ensure download called with the selected URL (second one)
    mock_download.assert_called_once_with('https://example.com/image2.jpg')
    # Ensure wallpaper setter called with the downloaded path
    mock_set_wallpaper.assert_called_once_with('/tmp/image1.jpg')

def test_choose_image_invalid_input(monkeypatch, capsys):
    # Simulate invalid then valid input
    inputs = iter(['5', '0', '2'])
    monkeypatch.setattr(builtins, 'input', lambda _: next(inputs))
    options = ['a', 'b', 'c']
    choice = choose_image(options)
    captured = capsys.readouterr()
    assert choice == 'b'
    # Should have printed invalid choice messages twice
    assert captured.out.count('Invalid choice') == 2
