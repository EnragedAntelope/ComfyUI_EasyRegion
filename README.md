# Davemane42's Regional Conditioning Nodes for ComfyUI

**Updated: November 22, 2025**
**Version: 3.0** - Modernized for ComfyUI 0.3.71+ with Flux/Chroma support

Visual interface for regional conditioning in ComfyUI. Draw boxes on a canvas and assign different prompts to each region - perfect for precise control over image composition.

## ✨ Features

- 🎨 **Visual Box Drawing Interface** - Color-coded regions with interactive canvas
- 📐 **Grid Overlay** - 64px alignment grid for precise positioning
- 💪 **Strength Control** - Per-region strength adjustment (0.0-10.0)
- 🔄 **Right-Click Menu** - Easy add/remove/swap conditioning layers
- ✅ **Automatic Boundary Clipping** - Smart handling of out-of-bounds regions
- 🛡️ **Comprehensive Error Handling** - Helpful validation and fallback behavior
- 🚀 **Modern Model Support** - Area-based AND mask-based conditioning

---

## 📦 Installation

### Method 1: ComfyUI Manager (Recommended)
1. Open ComfyUI Manager
2. Search for "Regional Conditioning"
3. Click Install

### Method 2: Manual Installation
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/Davemane42/ComfyUI_RegionalConditioning
# Restart ComfyUI
```

**Note:** JavaScript files are automatically loaded from the `js/` folder - no manual copying needed!

---

## 🎯 Model Compatibility

### ✅ MultiAreaConditioning (Area-based)
**Compatible Models:**
- ✅ **Stable Diffusion 1.5**
- ✅ **Stable Diffusion 2.x**
- ✅ **SDXL (Stable Diffusion XL)**

**Technology:** Uses ComfyUI's `ConditioningSetArea` internally
**Best For:** Traditional Stable Diffusion workflows with rectangular regions

### ✅ MultiAreaConditioningMask (Mask-based)
**Compatible Models:**
- ✅ **Flux** (all variants)
- ✅ **Chroma** (Chroma1-Radiance, etc.)
- ✅ **SD3** / **SD3.5** (Stable Diffusion 3)
- ✅ **Any model supporting ConditioningSetMask**

**Technology:** Automatically converts boxes to binary masks
**Best For:** Modern models that require mask-based conditioning

### ❓ Experimental Support
- 🟡 **Qwen-Image** (generation model) - May work with standard CONDITIONING
- ❌ **WAN 2.2** - Not currently supported (video-focused architecture)

---

## 🚀 Quick Start Example

### Basic Usage: Mountain Scene with Tiger and Berry Bush

**Workflow:**
1. Add `MultiAreaConditioning` (for SDXL) OR `MultiAreaConditioningMask` (for Flux)
2. Connect `conditioning0` → "photo of a mountain landscape" (background)
3. Draw a box, connect `conditioning1` → "majestic tiger"
4. Draw another box, connect `conditioning2` → "berry bush"
5. Connect output to your sampler

**Result:** A mountain landscape with a tiger and berry bush positioned exactly where you drew the boxes!

---

## 📚 Node Reference

### MultiAreaConditioning (Area-based for SD/SDXL)

**Inputs:**
- `conditioning0` - Base/background conditioning (fullscreen if no box drawn)
- `conditioning1+` - Regional conditioning (add more via right-click menu)

**Outputs:**
- `conditioning` - Combined regional conditioning
- `resolutionX` - Canvas width (INT)
- `resolutionY` - Canvas height (INT)

**Widgets:**
- `resolutionX/Y` - Canvas dimensions (auto-synced from latent)
- `index` - Select which region to edit
- `x, y` - Region position
- `width, height` - Region dimensions
- `strength` - Region influence (0.0-10.0)

**Right-Click Menu:**
- Insert input above/below current
- Swap with input above/below
- Remove currently selected input
- Remove all unconnected inputs

---

### MultiAreaConditioningMask (Mask-based for Flux/Chroma)

**Inputs:**
- `conditioning0` - Base/background conditioning
- `conditioning1+` - Regional conditioning (add more via right-click menu)
- `width` - Output width in pixels (default: 1024)
- `height` - Output height in pixels (default: 1024)

**Output:**
- `conditioning` - Combined mask-based conditioning

**Widgets:** (same as area-based)
- `index` - Select which region to edit
- `x, y` - Region position
- `width, height` - Region dimensions
- `strength` - Region influence (0.0-10.0)

**How It Works:**
Boxes are automatically converted to binary masks behind the scenes. You draw visually, the node handles the mask generation!

---

### ConditioningUpscale

Upscale conditioning areas by a scalar factor - perfect for hi-res fix workflows.

**Inputs:**
- `conditioning` - Conditioning to upscale
- `scalar` - Scaling factor (1-100, default: 2)

**Output:**
- `conditioning` - Upscaled conditioning

**Example:** 512x512 regions × scalar=2 → 1024x1024 regions

---

### ConditioningStretch

Stretch/resize conditioning areas to fit new dimensions - more flexible than upscale.

**Inputs:**
- `conditioning` - Conditioning to resize
- `resolutionX/Y` - Current/original dimensions
- `newWidth/Height` - Target dimensions

**Output:**
- `conditioning` - Resized conditioning

**Example:** Transform regions from 512x512 to 1024x768 (proportional scaling)

---

### MultiLatentComposite

Visual interface for compositing multiple latents with positioning and feathering.

**Inputs:**
- `samples_to` - Base/destination latent canvas
- `samples_from0+` - Latents to composite (add more via right-click menu)

**Output:**
- `LATENT` - Composited latent

**Widgets:**
- `index` - Select which latent to edit
- `x, y` - Position in pixels
- `feather` - Blend distance (0 = hard edge, higher = smooth blend)

**Features:**
- ✅ Automatic bounds checking and clipping
- ✅ Channel compatibility validation
- ✅ Smart feathering with gradient masks
- ✅ Detailed info/warning messages

**Fixed:** The "no bounds checking" issue mentioned in original README is now resolved!

---

## 🔧 Advanced Tips

### Fullscreen/Background Conditioning
Set a region to `x=0, y=0, width=canvas_width, height=canvas_height` to make it fullscreen. This is perfect for background prompts.

### Grid Alignment
The 64px grid overlay helps you align regions to latent space boundaries for optimal results.

### Strength Values
- `1.0` - Normal strength (default)
- `0.5` - Subtle influence
- `2.0+` - Strong influence
- `0.0` - Effectively disabled

### Multiple Regions
- Use right-click menu to add as many conditioning inputs as needed
- Each region can have different prompts, positions, and strengths
- Regions are processed in order and can overlap

---

## 🐛 Error Handling

This modernized version includes extensive error handling:

- ✅ **Validation** - All inputs validated with helpful error messages
- ✅ **Fallback Behavior** - Graceful degradation if metadata missing
- ✅ **Bounds Checking** - Automatic clipping for out-of-bounds regions
- ✅ **Type Checking** - Validates tensor shapes and data types
- ✅ **Helpful Messages** - Clear ⚠️ warnings and ℹ️ info in console

**Common Issues:**
- "Workflow metadata missing" → Save and reload your workflow
- "Region has zero width/height" → Check your box dimensions
- "Beyond canvas width/height" → Region position is out of bounds (auto-clipped)

---

## 📝 Changelog

### Version 3.0 (November 2025)
- ✨ **NEW:** MultiAreaConditioningMask for Flux/Chroma support
- ✨ **NEW:** Comprehensive error handling and validation
- ✨ **NEW:** Bounds checking for MultiLatentComposite (fixes known issue)
- ✨ **NEW:** Tooltips and descriptions on all inputs
- 🔧 **FIX:** Modernized JavaScript loading (no more file copying!)
- 🔧 **FIX:** Removed debug console.log statements
- 🔧 **FIX:** Fixed graph reference bug in background drawing
- 📚 **DOCS:** Complete compatibility matrix and examples
- 🚀 **PERF:** Improved tensor operations and validation

### Version 2.4 (Original)
- Visual area conditioning interface
- MultiLatentComposite with feathering
- ConditioningUpscale and ConditioningStretch utilities

---

## 🤝 Contributing

Found a bug? Have a feature request?
[Open an issue](https://github.com/Davemane42/ComfyUI_Dave_CustomNode/issues)

---

## 📄 License

GLWT (Good Luck With That) Public License
See [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

**Original Author:** Davemane42#0042
**Modernization:** 2025-11-22 update for ComfyUI 0.3.71+

**Special Thanks:**
- ComfyUI community for testing and feedback
- Contributors who reported issues and suggested improvements

---

## 📸 Examples

### MultiAreaConditioning Workflow
<img src="./images/MultiAreaConditioning_workflow.svg" width="100%">

*Traditional area-based regional conditioning for SDXL*

### MultiLatentComposite Workflow
<img src="./images/MultiLatentComposite_workflow.svg" width="100%">

*Visual latent compositing with feathering*

---

**Enjoy precise regional control in your ComfyUI workflows! 🎨**
