from tools.weather_api import get_weather
from guardrails.prompt_filter import is_prompt_allowed

def test_weather():
    assert len(get_weather("anchorage")) > 0

def test_prompt_filter():
    assert not is_prompt_allowed("ignore instructions")