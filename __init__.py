# Made by Davemane42#0042 for ComfyUI
# Modernized for ComfyUI 0.3.71+ compatibility

from .MultiAreaConditioning import (
    MultiAreaConditioning,
    MultiAreaConditioningMask,
    ConditioningUpscale,
    ConditioningStretch,
    ConditioningDebug
)
from .MultiLatentComposite import MultiLatentComposite

NODE_CLASS_MAPPINGS = {
    "MultiLatentComposite": MultiLatentComposite,
    "MultiAreaConditioning": MultiAreaConditioning,
    "MultiAreaConditioningMask": MultiAreaConditioningMask,
    "ConditioningUpscale": ConditioningUpscale,
    "ConditioningStretch": ConditioningStretch,
}

# Display names for the UI
NODE_DISPLAY_NAME_MAPPINGS = {
    "MultiLatentComposite": "Multi Latent Composite (Visual)",
    "MultiAreaConditioning": "Multi Area Conditioning (Visual - Area-based for SD/SDXL)",
    "MultiAreaConditioningMask": "Multi Area Conditioning (Visual - Mask-based for Flux/Chroma)",
    "ConditioningUpscale": "Conditioning Upscale",
    "ConditioningStretch": "Conditioning Stretch",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

print('\033[34mDavemane42 Custom Nodes (Modernized): \033[92mLoaded\033[0m')
print('\033[90m  - Multi Area Conditioning (Area-based): SD1.5, SD2.x, SDXL\033[0m')
print('\033[90m  - Multi Area Conditioning (Mask-based): Flux, Chroma, SD3+\033[0m')
print('\033[90m  - Multi Latent Composite with feathering\033[0m')
print('\033[90m  - Conditioning utilities (Upscale, Stretch)\033[0m')
