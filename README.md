# ComfyUI EasyRegion

Control different parts of your image with separate prompts using visual box drawing.

## Quick Start

1. **Install**: Clone to `ComfyUI/custom_nodes/` or use ComfyUI Manager
2. **Add Node**: Search for "EasyRegion"
3. **Connect**: CLIP → EasyRegion → Sampler
4. **Draw**: Use canvas to position regions, type prompts
5. **Generate**: Connect to your sampler and run

## Nodes

### EasyRegion (Mask-Based)
**For:** Flux, Chroma, SD3, SD3.5, Qwen-Image

**Inputs:**
- `clip`: CLIP from checkpoint
- `width`/`height`: Must match your latent dimensions
- `soften_masks`: Feathering at edges (recommended ON)
- `background_prompt`: Scene description
- `background_strength`: Background conditioning strength (0.5 default)
- `region1-4_prompt`: Region-specific prompts
- `region1-4_strength`: Per-region strength (2.5-4.5 for Flux)

**Tips:**
- Use CFG 1.0 with Flux Base (higher = blur)
- Keep to 3-4 regions max for Flux/Chroma
- **Position regions FAR APART** for best results (left/right thirds)
- Strength 2.5-4.5 works well with bg_strength=0.5 (too high = soft/lose details)

### EasyRegion (Area-Based)
**For:** SD1.5, SD2.x, SDXL

Same interface, uses area-based conditioning instead of masks.

## Canvas Controls

- **region**: Select which region to edit (1-4)
- **box_x, box_y**: Region top-left position (pixels)
- **box_w, box_h**: Region dimensions (pixels)

## Example Workflow

```
Checkpoint Loader
├→ CLIP → EasyRegion (Mask-Based)
│           ├ width: 1024
│           ├ height: 1024
│           ├ soften_masks: true
│           ├ background_prompt: "empty city street at night"
│           ├ background_strength: 0.5
│           ├ region1_prompt: "red sports car on left side (left third)"
│           ├ region1_strength: 2.5
│           ├ region2_prompt: "giraffe on right side (right third)"
│           └ region2_strength: 3.5
├→ MODEL → KSampler ← conditioning
└→ VAE → VAE Decode
```

## Troubleshooting

**Regions not showing:**
- **Increase region strength** (try 3.0-5.0 for Flux)
- Lower background_strength (try 0.3-0.5)
- Check width/height match your latent exactly
- Verify boxes aren't outside image bounds
- **Position regions FAR APART** - overlapping regions compete

**Soft/blurry regions:**
- **Lower region strength** (too high = loss of detail)
- For Flux: 2.5-4.5 range works well with bg_strength=0.5

**Validation errors:**
- Ensure width/height are multiples of 64
- Check no regions overlap fullscreen

**CFG Issues with Flux:**
- Use CFG 1.0 for Flux Base (NO negative prompt)
- Higher CFG = blur and artifacts

## Advanced Nodes

Original nodes available for complex workflows:

- **Multi Area Conditioning**: Area-based, requires external CLIP encode
- **Multi Area Conditioning Mask**: Mask-based, requires external CLIP encode
- **Multi Latent Composite**: Visual latent compositing with feathering

## Credits

Based on visual area conditioning by [Davemane42](https://github.com/Davemane42).

Maintained by EnragedAntelope - [github.com/EnragedAntelope/ComfyUI_RegionalConditioning](https://github.com/EnragedAntelope/ComfyUI_RegionalConditioning)

## License

MIT License - use freely in personal and commercial projects.
