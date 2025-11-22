# ComfyUI EasyRegion
# Enhanced nodes with inline prompts for easy regional control

from .RegionalPrompting import (
    EasyRegionSimple,
    EasyRegionFlux
)

NODE_CLASS_MAPPINGS = {
    "EasyRegionSimple": EasyRegionSimple,
    "EasyRegionFlux": EasyRegionFlux,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EasyRegionSimple": "EasyRegion (Area-Based)",
    "EasyRegionFlux": "EasyRegion (Mask-Based)",
}

# Export web directory for JavaScript files
import os
WEB_DIRECTORY = os.path.join(os.path.dirname(__file__), "js")

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

print('\033[34mComfyUI_EasyRegion: \033[92mLoaded successfully\033[0m')
