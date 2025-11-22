# Made by Davemane42#0042 for ComfyUI
# Updated: 2025-11-22
# Modernized for ComfyUI 0.3.71+ with bounds checking and comprehensive error handling

import torch

class MultiLatentComposite:
    """
    Visual interface for compositing multiple latents with positioning.

    Draw boxes to position latent images on a canvas.
    Supports feathering for smooth blending between latent regions.

    Perfect for composing multiple generated elements into a single image.
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "samples_to": ("LATENT", {"tooltip": "Base/destination latent canvas"}),
                "samples_from0": ("LATENT", {"tooltip": "First latent to composite onto canvas"}),
            },
            "hidden": {"extra_pnginfo": "EXTRA_PNGINFO", "unique_id": "UNIQUE_ID"},
        }

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "composite"
    CATEGORY = "Davemane42"
    DESCRIPTION = """Visual latent compositing with positioning and feathering.

Features:
• Visual interface showing composite layout
• Position multiple latents on a canvas
• Feathering support for smooth blending
• Auto-detects source dimensions
• Interactive positioning controls

Use this to compose multiple generated latents into a single image with precise control over placement."""

    def composite(self, samples_to, extra_pnginfo, unique_id, **kwargs):
        """Composite multiple latents with visual positioning and feathering."""

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
                    break

            if not node_found:
                raise ValueError(f"Node with ID {unique_id} not found in workflow. Please save and reload the workflow.")

        except Exception as e:
            print(f"\n❌ MultiLatentComposite Error: {str(e)}")
            print(f"   Using fallback - returning base latent unchanged.\n")
            # Fallback: return destination latent unchanged
            return (samples_to,)

        # Validate samples_to structure
        if not isinstance(samples_to, dict):
            raise ValueError("samples_to must be a LATENT dict")

        if "samples" not in samples_to:
            raise ValueError("samples_to is missing 'samples' tensor")

        if not torch.is_tensor(samples_to["samples"]):
            raise ValueError("samples_to['samples'] must be a tensor")

        # Create output latent (copy to avoid modifying input)
        samples_out = samples_to.copy()
        s = samples_to["samples"].clone()
        samples_to_tensor = samples_to["samples"]

        # Get destination dimensions
        dest_shape = samples_to_tensor.shape
        if len(dest_shape) != 4:
            raise ValueError(f"Invalid samples_to shape: {dest_shape}. Expected 4D tensor (batch, channels, height, width)")

        dest_batch, dest_channels, dest_height, dest_width = dest_shape

        print(f"ℹ️  Destination latent: {dest_width*8}x{dest_height*8}px ({dest_width}x{dest_height} latent)")

        # Process each source latent
        k = 0
        for arg in sorted(kwargs.keys()):  # Process in order
            if k >= len(values):
                break

            # Validate source latent
            if not isinstance(kwargs[arg], dict):
                print(f"⚠️  Warning: {arg} is not a valid LATENT dict, skipping")
                k += 1
                continue

            if "samples" not in kwargs[arg]:
                print(f"⚠️  Warning: {arg} is missing 'samples' tensor, skipping")
                k += 1
                continue

            samples_from_tensor = kwargs[arg]["samples"]

            if not torch.is_tensor(samples_from_tensor):
                print(f"⚠️  Warning: {arg}['samples'] is not a tensor, skipping")
                k += 1
                continue

            # Validate source dimensions
            src_shape = samples_from_tensor.shape
            if len(src_shape) != 4:
                print(f"⚠️  Warning: {arg} has invalid shape {src_shape}, skipping")
                k += 1
                continue

            src_batch, src_channels, src_height, src_width = src_shape

            # Validate channel compatibility
            if src_channels != dest_channels:
                print(f"⚠️  Warning: {arg} has {src_channels} channels, destination has {dest_channels}. Skipping.")
                k += 1
                continue

            # Parse position values
            try:
                x = int(values[k][0]) // 8  # Convert to latent space
                y = int(values[k][1]) // 8
                feather = int(values[k][2]) // 8 if len(values[k]) > 2 else 0
            except (IndexError, ValueError, TypeError) as e:
                print(f"⚠️  Warning: Invalid position values for {arg}: {values[k]}, skipping")
                k += 1
                continue

            # Validate feather value
            feather = max(0, feather)

            print(f"ℹ️  Compositing {arg}: {src_width*8}x{src_height*8}px at position ({x*8}, {y*8})px, feather={feather*8}px")

            # Check bounds and clip if necessary
            if x < 0:
                print(f"⚠️  Warning: x position {x*8}px is negative, clipping to 0")
                x = 0

            if y < 0:
                print(f"⚠️  Warning: y position {y*8}px is negative, clipping to 0")
                y = 0

            if x >= dest_width:
                print(f"⚠️  Warning: x position {x*8}px is beyond canvas width {dest_width*8}px, skipping")
                k += 1
                continue

            if y >= dest_height:
                print(f"⚠️  Warning: y position {y*8}px is beyond canvas height {dest_height*8}px, skipping")
                k += 1
                continue

            # Calculate available space and clip source if necessary
            available_width = dest_width - x
            available_height = dest_height - y

            # Clip source to fit available space
            src_width_clipped = min(src_width, available_width)
            src_height_clipped = min(src_height, available_height)

            if src_width_clipped != src_width or src_height_clipped != src_height:
                print(f"ℹ️  Info: Source clipped to {src_width_clipped*8}x{src_height_clipped*8}px to fit canvas")

            # Extract clipped region from source
            samples_from_clipped = samples_from_tensor[:, :, :src_height_clipped, :src_width_clipped]

            # Composite without feathering (fast path)
            if feather == 0:
                s[:, :, y:y+src_height_clipped, x:x+src_width_clipped] = samples_from_clipped
            else:
                # Composite with feathering (creates smooth blend at edges)
                # Validate feather doesn't exceed dimensions
                max_feather = min(src_width_clipped, src_height_clipped) // 2
                if feather > max_feather:
                    print(f"ℹ️  Info: Feather {feather*8}px reduced to {max_feather*8}px (max for this region)")
                    feather = max_feather

                # Create feather mask
                try:
                    mask = torch.ones_like(samples_from_clipped)

                    # Apply gradient feathering on each edge
                    for t in range(feather):
                        gradient_val = (t + 1) / feather

                        # Top edge
                        if y != 0 and t < src_height_clipped:
                            mask[:, :, t:t+1, :] *= gradient_val

                        # Bottom edge
                        if y + src_height_clipped < dest_height and t < src_height_clipped:
                            bottom_idx = src_height_clipped - 1 - t
                            if bottom_idx >= 0:
                                mask[:, :, bottom_idx:bottom_idx+1, :] *= gradient_val

                        # Left edge
                        if x != 0 and t < src_width_clipped:
                            mask[:, :, :, t:t+1] *= gradient_val

                        # Right edge
                        if x + src_width_clipped < dest_width and t < src_width_clipped:
                            right_idx = src_width_clipped - 1 - t
                            if right_idx >= 0:
                                mask[:, :, :, right_idx:right_idx+1] *= gradient_val

                    # Apply masked composite
                    rev_mask = torch.ones_like(mask) - mask
                    dest_region = s[:, :, y:y+src_height_clipped, x:x+src_width_clipped]
                    s[:, :, y:y+src_height_clipped, x:x+src_width_clipped] = (
                        samples_from_clipped * mask + dest_region * rev_mask
                    )

                except Exception as e:
                    print(f"⚠️  Warning: Feathering failed for {arg}: {e}. Using non-feathered composite.")
                    s[:, :, y:y+src_height_clipped, x:x+src_width_clipped] = samples_from_clipped

            k += 1

        samples_out["samples"] = s
        return (samples_out,)
