"""
Auto-generated plugin 272
"""
from typing import Dict

def setup(context: Dict):
    """Plugin setup for generated plugin 272"""
    # harmless transform
    def on_page_render(page):
        return page
    context.setdefault('hooks', []).append(on_page_render)
    return True

def teardown():
    return None
