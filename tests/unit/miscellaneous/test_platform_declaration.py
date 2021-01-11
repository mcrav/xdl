import pytest
from xdl.platforms.placeholder import PlaceholderPlatform

@pytest.mark.unit
def test_platform_declaration():
    """Test platform declaration generation runs without error."""
    return PlaceholderPlatform().declaration
