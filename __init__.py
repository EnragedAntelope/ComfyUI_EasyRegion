# Made by Davemane42#0042 for ComfyUI
# Modernized for ComfyUI 0.3.71+ compatibility
# Enhanced version with inline prompts - November 2025

from .MultiAreaConditioning import (
    MultiAreaConditioning,
    MultiAreaConditioningMask,
    ConditioningUpscale,
    ConditioningStretch,
    ConditioningDebug
)
from .MultiLatentComposite import MultiLatentComposite
from .RegionalPrompting import (
    RegionalPrompterSimple,
    RegionalPrompterFlux
)

NODE_CLASS_MAPPINGS = {
    # Original nodes (require external CLIP Text Encode)
    "MultiLatentComposite": MultiLatentComposite,
    "MultiAreaConditioning": MultiAreaConditioning,
    "MultiAreaConditioningMask": MultiAreaConditioningMask,
    "ConditioningUpscale": ConditioningUpscale,
    "ConditioningStretch": ConditioningStretch,

    # Enhanced all-in-one nodes (inline prompts - RECOMMENDED)
    "RegionalPrompterSimple": RegionalPrompterSimple,
    "RegionalPrompterFlux": RegionalPrompterFlux,
}

# Display names for the UI
NODE_DISPLAY_NAME_MAPPINGS = {
    # Original nodes
    "MultiLatentComposite": "Multi Latent Composite (Visual)",
    "MultiAreaConditioning": "Multi Area Conditioning (SD/SDXL - Advanced)",
    "MultiAreaConditioningMask": "Multi Area Conditioning (Flux/Chroma - Advanced)",
    "ConditioningUpscale": "Conditioning Upscale",
    "ConditioningStretch": "Conditioning Stretch",

    # Enhanced nodes
    "RegionalPrompterSimple": "🎨 Regional Prompter (SD/SDXL - Easy!)",
    "RegionalPrompterFlux": "🎨 Regional Prompter (Flux/Chroma - Easy!)",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

print('\033[34mDavemane42 Custom Nodes (Modernized): \033[92mLoaded\033[0m')
print('\033[90m  📦 Original Nodes (Advanced):\033[0m')
print('\033[90m    - Multi Area Conditioning: SD1.5, SD2.x, SDXL\033[0m')
print('\033[90m    - Multi Area Conditioning Mask: Flux, Chroma, SD3+\033[0m')
print('\033[90m    - Multi Latent Composite with feathering\033[0m')
print('\033[90m    - Conditioning utilities (Upscale, Stretch)\033[0m')
print('\033[92m  ✨ RECOMMENDED - Enhanced Easy Nodes:\033[0m')
print('\033[92m    - Regional Prompter (SD/SDXL) - Type prompts directly!\033[0m')
print('\033[92m    - Regional Prompter (Flux/Chroma) - Optimized for modern models!\033[0m')
