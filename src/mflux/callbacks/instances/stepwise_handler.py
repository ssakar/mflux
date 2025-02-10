from pathlib import Path

import mlx.core as mx
import tqdm

from mflux import StopImageGenerationException
from mflux.callbacks.callback import InLoopCallback, InterruptCallback
from mflux.config.runtime_config import RuntimeConfig
from mflux.post_processing.array_util import ArrayUtil
from mflux.post_processing.image_util import ImageUtil


class StepwiseHandler(InLoopCallback, InterruptCallback):
    def __init__(
        self,
        flux,
        output_dir: str,
    ):
        self.flux = flux
        self.output_dir = Path(output_dir)
        self.step_wise_images = []

        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def call_in_loop(
        self,
        seed: int,
        prompt: str,
        step: int,
        latents: mx.array,
        config: RuntimeConfig,
        time_steps: tqdm
    ) -> None:  # fmt: off
        unpack_latents = ArrayUtil.unpack_latents(latents=latents, height=config.height, width=config.width)
        stepwise_decoded = self.flux.vae.decode(unpack_latents)
        stepwise_img = ImageUtil.to_image(
            decoded_latents=stepwise_decoded,
            config=config,
            seed=seed,
            prompt=prompt,
            quantization=self.flux.bits,
            lora_paths=self.flux.lora_paths,
            lora_scales=self.flux.lora_scales,
            generation_time=time_steps.format_dict["elapsed"],
        )
        self.step_wise_images.append(stepwise_img)

        stepwise_img.save(
            path=self.output_dir / f"seed_{seed}_step{step}of{len(time_steps)}.png",
            export_json_metadata=False,
        )
        self._save_composite(seed=seed)

    def call_interrupt(
        self,
        seed: int,
        prompt: str,
        step: int,
        latents: mx.array,
        config: RuntimeConfig,
        time_steps: tqdm
    ) -> None:  # fmt: off
        self._save_composite(seed=seed)
        raise StopImageGenerationException(f"Stopping image generation at step {step + 1}/{len(time_steps)}")

    def _save_composite(self, seed: int) -> None:
        if self.step_wise_images:
            composite_img = ImageUtil.to_composite_image(self.step_wise_images)
            composite_img.save(self.output_dir / f"seed_{seed}_composite.png")
