# Made by Davemane42#0042 for ComfyUI
# Updated: 2025-11-22
# Modernized for ComfyUI 0.3.71+ with comprehensive error handling and validation

import torch
from nodes import MAX_RESOLUTION

class MultiAreaConditioning:
    """
    Visual interface for area-based regional conditioning.

    Compatible with: SD1.5, SD2.x, SDXL

    Draw rectangular boxes and assign different prompts to each region.
    Perfect for composing images with multiple subjects in specific locations.

    Example: "photo of mountain" (background) + box with "tiger" + box with "berry bush"
    """

    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "conditioning0": ("CONDITIONING", {"tooltip": "Base/background conditioning (fullscreen if no box drawn)"}),
                "conditioning1": ("CONDITIONING", {"tooltip": "Conditioning for first region/box"})
            },
            "hidden": {"extra_pnginfo": "EXTRA_PNGINFO", "unique_id": "UNIQUE_ID"},
        }

    RETURN_TYPES = ("CONDITIONING", "INT", "INT")
    RETURN_NAMES = ("conditioning", "resolutionX", "resolutionY")
    FUNCTION = "apply_regional_conditioning"
    CATEGORY = "Davemane42"
    DESCRIPTION = """Visual area-based regional conditioning for SD1.5/SD2.x/SDXL.

Draw boxes on the canvas and connect different prompts to each region. Use right-click menu to add/remove/swap conditioning layers.

Features:
• Visual box drawing interface with color-coded regions
• Grid overlay (64px) for precise alignment
• Strength control per region (0.0-10.0)
• Fullscreen detection for background conditioning
• Automatic boundary clipping

Compatible Models: SD1.5, SD2.x, SDXL"""

    def apply_regional_conditioning(self, extra_pnginfo, unique_id, **kwargs):
        """Apply area-based conditioning to rectangular regions."""

        c = []
        values = []
        resolutionX = 512
        resolutionY = 512

        # Validate extra_pnginfo structure with helpful error messages
        try:
            if not extra_pnginfo:
                raise ValueError("Workflow metadata (extra_pnginfo) is missing. Please save and reload the workflow.")

            if "workflow" not in extra_pnginfo:
                raise ValueError("Workflow data not found in metadata. Please save and reload the workflow.")

            if "nodes" not in extra_pnginfo["workflow"]:
                raise ValueError("Node data not found in workflow metadata. Please save and reload the workflow.")

            # Find this node's properties in the workflow
            node_found = False
            for node in extra_pnginfo["workflow"]["nodes"]:
                if node["id"] == int(unique_id):
                    node_found = True
                    if "properties" not in node:
                        raise ValueError(f"Node {unique_id} is missing properties. Please recreate the node.")

                    values = node["properties"].get("values", [])
                    resolutionX = node["properties"].get("width", 512)
                    resolutionY = node["properties"].get("height", 512)
                    break

            if not node_found:
                raise ValueError(f"Node with ID {unique_id} not found in workflow. Please save and reload the workflow.")

        except Exception as e:
            print(f"\n❌ MultiAreaConditioning Error: {str(e)}")
            print(f"   Using fallback values - please check your workflow setup.\n")
            # Fallback: pass through first conditioning input
            if "conditioning0" in kwargs:
                return (kwargs["conditioning0"], 512, 512)
            raise

        # Validate resolution values
        if not isinstance(resolutionX, (int, float)) or resolutionX <= 0:
            print(f"⚠️  Warning: Invalid resolutionX ({resolutionX}), using 512")
            resolutionX = 512
        if not isinstance(resolutionY, (int, float)) or resolutionY <= 0:
            print(f"⚠️  Warning: Invalid resolutionY ({resolutionY}), using 512")
            resolutionY = 512

        # Process conditioning inputs
        k = 0
        for arg in kwargs:
            if k >= len(values):
                break

            # Validate conditioning input
            if not isinstance(kwargs[arg], list):
                print(f"⚠️  Warning: conditioning{k} is not a valid CONDITIONING type, skipping")
                k += 1
                continue

            if len(kwargs[arg]) == 0:
                print(f"⚠️  Warning: conditioning{k} is empty, skipping")
                k += 1
                continue

            # Check if conditioning contains valid tensors
            if not torch.is_tensor(kwargs[arg][0][0]):
                print(f"⚠️  Warning: conditioning{k} does not contain valid tensor data, skipping")
                k += 1
                continue

            # Parse region values with validation
            try:
                x, y = int(values[k][0]), int(values[k][1])
                w, h = int(values[k][2]), int(values[k][3])
            except (IndexError, ValueError, TypeError) as e:
                print(f"⚠️  Warning: Invalid region values for conditioning{k}: {values[k]}, skipping")
                k += 1
                continue

            # If fullscreen (background conditioning)
            if (x == 0 and y == 0 and w == resolutionX and h == resolutionY):
                for t in kwargs[arg]:
                    c.append(t)
                k += 1
                continue

            # Clip to canvas boundaries with validation
            if x + w > resolutionX:
                w = max(0, resolutionX - x)

            if y + h > resolutionY:
                h = max(0, resolutionY - y)

            # Skip zero-size regions
            if w == 0 or h == 0:
                print(f"⚠️  Warning: Region {k} has zero width or height after clipping, skipping")
                k += 1
                continue

            # Apply area-based conditioning to each element
            for t in kwargs[arg]:
                # Validate conditioning structure
                if not isinstance(t, (list, tuple)) or len(t) < 2:
                    print(f"⚠️  Warning: Invalid conditioning structure in conditioning{k}, skipping")
                    continue

                # Create new conditioning with area
                n = [t[0], t[1].copy()]

                # Convert to latent space coordinates (divide by 8 for VAE downscaling)
                n[1]['area'] = (h // 8, w // 8, y // 8, x // 8)

                # Parse strength with validation
                try:
                    strength = float(values[k][4]) if len(values[k]) > 4 else 1.0
                    strength = max(0.0, min(10.0, strength))  # Clamp to valid range
                except (IndexError, ValueError, TypeError):
                    strength = 1.0
                    print(f"⚠️  Warning: Invalid strength for region {k}, using 1.0")

                n[1]['strength'] = strength
                n[1]['min_sigma'] = 0.0
                n[1]['max_sigma'] = 99.0

                c.append(n)

            k += 1

        # Validate output
        if len(c) == 0:
            print("⚠️  Warning: No valid conditioning regions generated, returning empty conditioning")
            # Return empty conditioning with proper structure
            c = []

        return (c, int(resolutionX), int(resolutionY))


class MultiAreaConditioningMask:
    """
    Visual interface for mask-based regional conditioning.

    Compatible with: Flux, Chroma, SD3+, and any model supporting ConditioningSetMask

    Same visual box-drawing interface as MultiAreaConditioning, but automatically
    converts boxes to masks for models that require mask-based conditioning.

    Perfect for modern models like Flux and Chroma that don't support area-based conditioning.
    """

    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "conditioning0": ("CONDITIONING", {"tooltip": "Base/background conditioning"}),
                "conditioning1": ("CONDITIONING", {"tooltip": "Conditioning for first region/box"}),
                "width": ("INT", {"default": 1024, "min": 64, "max": MAX_RESOLUTION, "step": 64, "tooltip": "Output width in pixels"}),
                "height": ("INT", {"default": 1024, "min": 64, "max": MAX_RESOLUTION, "step": 64, "tooltip": "Output height in pixels"}),
            },
            "hidden": {"extra_pnginfo": "EXTRA_PNGINFO", "unique_id": "UNIQUE_ID"},
        }

    RETURN_TYPES = ("CONDITIONING",)
    RETURN_NAMES = ("conditioning",)
    FUNCTION = "apply_regional_conditioning_mask"
    CATEGORY = "Davemane42"
    DESCRIPTION = """Visual mask-based regional conditioning for Flux/Chroma/SD3+.

Same visual box-drawing interface as area-based version, but uses masks internally for compatibility with modern models.

Features:
• Draw boxes visually - automatically converted to masks
• Grid overlay (64px) for precise alignment
• Strength control per region (0.0-10.0)
• Full compatibility with Flux, Chroma, SD3, and other mask-based models

Compatible Models: Flux, Chroma, SD3, SD3.5, and any model supporting ConditioningSetMask

Note: Boxes are automatically converted to grayscale masks behind the scenes."""

    def apply_regional_conditioning_mask(self, width, height, extra_pnginfo, unique_id, **kwargs):
        """Apply mask-based conditioning by converting boxes to masks."""

        values = []

        # Validate extra_pnginfo structure
        try:
            if not extra_pnginfo:
                raise ValueError("Workflow metadata (extra_pnginfo) is missing. Please save and reload the workflow.")

            if "workflow" not in extra_pnginfo:
                raise ValueError("Workflow data not found in metadata. Please save and reload the workflow.")

            if "nodes" not in extra_pnginfo["workflow"]:
                raise ValueError("Node data not found in workflow metadata. Please save and reload the workflow.")

            # Find this node's properties in the workflow
            node_found = False
            for node in extra_pnginfo["workflow"]["nodes"]:
                if node["id"] == int(unique_id):
                    node_found = True
                    if "properties" not in node:
                        raise ValueError(f"Node {unique_id} is missing properties. Please recreate the node.")

                    values = node["properties"].get("values", [])
                    # Use properties width/height if available, otherwise use input parameters
                    prop_width = node["properties"].get("width", width)
                    prop_height = node["properties"].get("height", height)

                    # Validate property dimensions match input dimensions
                    if prop_width != width or prop_height != height:
                        print(f"ℹ️  Info: Canvas size ({prop_width}x{prop_height}) differs from output ({width}x{height})")
                        print(f"       Regions will be scaled proportionally")

                    break

            if not node_found:
                raise ValueError(f"Node with ID {unique_id} not found in workflow. Please save and reload the workflow.")

        except Exception as e:
            print(f"\n❌ MultiAreaConditioningMask Error: {str(e)}")
            print(f"   Using fallback - passing through first conditioning input.\n")
            # Fallback: pass through first conditioning input
            if "conditioning0" in kwargs:
                return (kwargs["conditioning0"],)
            raise

        # Validate dimensions
        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid dimensions: {width}x{height}. Width and height must be positive.")

        # Start with empty conditioning list
        combined_conditioning = []

        # Process each conditioning input
        k = 0
        for arg in sorted(kwargs.keys()):  # Process in order
            if k >= len(values):
                break

            # Validate conditioning input
            if not isinstance(kwargs[arg], list):
                print(f"⚠️  Warning: {arg} is not a valid CONDITIONING type, skipping")
                k += 1
                continue

            if len(kwargs[arg]) == 0:
                print(f"⚠️  Warning: {arg} is empty, skipping")
                k += 1
                continue

            # Parse region values
            try:
                x, y = int(values[k][0]), int(values[k][1])
                w, h = int(values[k][2]), int(values[k][3])
            except (IndexError, ValueError, TypeError) as e:
                print(f"⚠️  Warning: Invalid region values for {arg}: {values[k]}, skipping")
                k += 1
                continue

            # Get canvas dimensions from properties
            canvas_width = prop_width if 'prop_width' in locals() else width
            canvas_height = prop_height if 'prop_height' in locals() else height

            # Check if fullscreen (no mask needed)
            is_fullscreen = (x == 0 and y == 0 and w == canvas_width and h == canvas_height)

            if is_fullscreen:
                # Fullscreen: pass through without mask
                for t in kwargs[arg]:
                    combined_conditioning.append(t)
                k += 1
                continue

            # Clip to canvas boundaries
            x = max(0, min(x, canvas_width))
            y = max(0, min(y, canvas_height))
            w = max(0, min(w, canvas_width - x))
            h = max(0, min(h, canvas_height - y))

            # Skip zero-size regions
            if w == 0 or h == 0:
                print(f"⚠️  Warning: Region {k} has zero width or height, skipping")
                k += 1
                continue

            # Create mask for this region (in latent space for efficiency)
            latent_width = width // 8
            latent_height = height // 8

            # Scale region coordinates to match output dimensions
            if canvas_width != width or canvas_height != height:
                x = int(x * width / canvas_width)
                y = int(y * height / canvas_height)
                w = int(w * width / canvas_width)
                h = int(h * height / canvas_height)

            # Convert to latent space coordinates
            x_latent = x // 8
            y_latent = y // 8
            w_latent = max(1, w // 8)  # Ensure at least 1 pixel
            h_latent = max(1, h // 8)

            # Create binary mask
            mask = torch.zeros((1, latent_height, latent_width), dtype=torch.float32)

            # Ensure we don't go out of bounds
            x_end = min(x_latent + w_latent, latent_width)
            y_end = min(y_latent + h_latent, latent_height)

            # Fill the region
            mask[0, y_latent:y_end, x_latent:x_end] = 1.0

            # Parse strength with validation
            try:
                strength = float(values[k][4]) if len(values[k]) > 4 else 1.0
                strength = max(0.0, min(10.0, strength))
            except (IndexError, ValueError, TypeError):
                strength = 1.0
                print(f"⚠️  Warning: Invalid strength for region {k}, using 1.0")

            # Apply mask to conditioning
            for t in kwargs[arg]:
                if not isinstance(t, (list, tuple)) or len(t) < 2:
                    print(f"⚠️  Warning: Invalid conditioning structure in {arg}, skipping")
                    continue

                n = [t[0], t[1].copy()]
                n[1]['mask'] = mask
                n[1]['strength'] = strength
                n[1]['set_area_to_bounds'] = False

                combined_conditioning.append(n)

            k += 1

        if len(combined_conditioning) == 0:
            print("⚠️  Warning: No valid conditioning regions generated, returning empty conditioning")

        return (combined_conditioning,)


class ConditioningUpscale():
    """
    Upscale conditioning areas by a scalar factor.

    Useful for hi-res fix workflows where you want to scale up your
    regional conditioning along with the image resolution.
    """

    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": ("CONDITIONING", {"tooltip": "Conditioning to upscale"}),
                "scalar": ("INT", {"default": 2, "min": 1, "max": 100, "step": 0.5, "tooltip": "Scaling factor (2 = 2x resolution)"}),
            },
        }

    RETURN_TYPES = ("CONDITIONING",)
    CATEGORY = "Davemane42"
    FUNCTION = 'upscale'
    DESCRIPTION = """Upscale conditioning areas by a scalar factor.

Multiplies all area dimensions by the specified scalar. Useful for hi-res fix workflows.

Example: If you have 512x512 regions and use scalar=2, they become 1024x1024."""

    def upscale(self, conditioning, scalar):
        """Upscale conditioning areas by scalar factor."""

        if not isinstance(conditioning, list):
            raise ValueError("Invalid conditioning input - must be CONDITIONING type")

        if scalar <= 0:
            raise ValueError(f"Invalid scalar {scalar} - must be positive")

        c = []
        for t in conditioning:
            if not isinstance(t, (list, tuple)) or len(t) < 2:
                print("⚠️  Warning: Invalid conditioning structure, skipping entry")
                continue

            n = [t[0], t[1].copy()]

            # Only upscale if area exists
            if 'area' in n[1]:
                try:
                    # Scale and round to nearest 8 pixels (latent space alignment)
                    n[1]['area'] = tuple(map(lambda x: ((x * scalar + 7) >> 3) << 3, n[1]['area']))
                except Exception as e:
                    print(f"⚠️  Warning: Failed to upscale area: {e}")

            c.append(n)

        return (c,)


class ConditioningStretch():
    """
    Stretch/resize conditioning areas to fit new dimensions.

    Proportionally transforms conditioning regions when changing image resolution.
    More flexible than ConditioningUpscale - specify exact target dimensions.
    """

    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": ("CONDITIONING", {"tooltip": "Conditioning to resize"}),
                "resolutionX": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 64, "tooltip": "Current/original width"}),
                "resolutionY": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 64, "tooltip": "Current/original height"}),
                "newWidth": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 64, "tooltip": "Target width"}),
                "newHeight": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 64, "tooltip": "Target height"}),
            },
        }

    RETURN_TYPES = ("CONDITIONING",)
    CATEGORY = "Davemane42"
    FUNCTION = 'upscale'
    DESCRIPTION = """Stretch/resize conditioning areas to fit new dimensions.

Proportionally transforms regions from one resolution to another. Perfect for when you change canvas size mid-workflow.

Example: Transform regions from 512x512 to 1024x768 - regions are scaled proportionally to fit."""

    def upscale(self, conditioning, resolutionX, resolutionY, newWidth, newHeight, scalar=1):
        """Stretch conditioning areas to new resolution."""

        if not isinstance(conditioning, list):
            raise ValueError("Invalid conditioning input - must be CONDITIONING type")

        if resolutionX <= 0 or resolutionY <= 0:
            raise ValueError(f"Invalid original resolution: {resolutionX}x{resolutionY}")

        if newWidth <= 0 or newHeight <= 0:
            raise ValueError(f"Invalid target resolution: {newWidth}x{newHeight}")

        c = []
        for t in conditioning:
            if not isinstance(t, (list, tuple)) or len(t) < 2:
                print("⚠️  Warning: Invalid conditioning structure, skipping entry")
                continue

            n = [t[0], t[1].copy()]

            # Only stretch if area exists
            if 'area' in n[1]:
                try:
                    newWidth_scaled = newWidth * scalar
                    newHeight_scaled = newHeight * scalar

                    # Calculate new coordinates proportionally
                    # area format: (height, width, y, x) in latent space
                    x = ((n[1]['area'][3] * 8) * newWidth_scaled / resolutionX) // 8
                    y = ((n[1]['area'][2] * 8) * newHeight_scaled / resolutionY) // 8
                    w = ((n[1]['area'][1] * 8) * newWidth_scaled / resolutionX) // 8
                    h = ((n[1]['area'][0] * 8) * newHeight_scaled / resolutionY) // 8

                    # Round to nearest 8 pixels (latent space alignment)
                    n[1]['area'] = tuple(map(lambda x: (((int(x) + 7) >> 3) << 3), [h, w, y, x]))
                except Exception as e:
                    print(f"⚠️  Warning: Failed to stretch area: {e}")

            c.append(n)

        return (c,)


class ConditioningDebug():
    """
    Debug node to print conditioning area information.

    Useful for troubleshooting regional conditioning setups.
    Displays all region coordinates, dimensions, and strength values.
    """

    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": ("CONDITIONING", {"tooltip": "Conditioning to inspect"}),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "debug"
    OUTPUT_NODE = True
    CATEGORY = "Davemane42"
    DESCRIPTION = """Debug conditioning by printing region information to console.

Displays:
• Region coordinates (x, y)
• Region dimensions (width, height)
• Strength values
• Fullscreen vs regional status

Check the console/terminal for output."""

    def debug(self, conditioning):
        """Print conditioning information for debugging."""

        print("\n" + "="*50)
        print("🔍 Conditioning Debug Output")
        print("="*50)

        if not isinstance(conditioning, list):
            print("❌ Error: conditioning is not a valid list")
            return (None,)

        if len(conditioning) == 0:
            print("⚠️  Warning: conditioning is empty")
            return (None,)

        for i, t in enumerate(conditioning):
            print(f"\nRegion {i}:")

            if not isinstance(t, (list, tuple)) or len(t) < 2:
                print("  ❌ Invalid structure")
                continue

            if "area" in t[1]:
                # area format: (height, width, y, x) in latent space (divided by 8)
                area = t[1]['area']
                print(f"  📍 Position: x={area[3]*8}, y={area[2]*8}")
                print(f"  📐 Size: width={area[1]*8}, height={area[0]*8}")

                if 'strength' in t[1]:
                    print(f"  💪 Strength: {t[1]['strength']}")

                if 'min_sigma' in t[1] or 'max_sigma' in t[1]:
                    print(f"  🎚️  Sigma range: {t[1].get('min_sigma', 'N/A')} - {t[1].get('max_sigma', 'N/A')}")
            else:
                print("  🖼️  Fullscreen (no area restriction)")

            # Check for mask
            if 'mask' in t[1]:
                mask = t[1]['mask']
                if torch.is_tensor(mask):
                    print(f"  🎭 Mask: shape={list(mask.shape)}, coverage={mask.sum().item()/(mask.numel()) * 100:.1f}%")
                else:
                    print("  🎭 Mask: present")

        print("\n" + "="*50 + "\n")

        return (None,)
