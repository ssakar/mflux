import os
import sys
import argparse
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from flux_1_schnell.config.config import Config
from flux_1_schnell.flux import Flux1
from flux_1_schnell.post_processing.image_util import ImageUtil

def main():
    parser = argparse.ArgumentParser(description='Generate an image based on a prompt.')
    parser.add_argument('--prompt', type=str, required=True, help='The textual description of the image to generate.')
    parser.add_argument('--output', type=str, default="image.png", help='The filename for the output image. Default is "image.png".')
    parser.add_argument('--model', type=str, default="black-forest-labs/FLUX.1-schnell", help='The model to use. Default is "black-forest-labs/FLUX.1-schnell".')
    parser.add_argument('--max_sequence_length', type=int, default=256, help='Max Sequence Length (Default is 256)')
    parser.add_argument('--seed', type=int, default=0, help='Entropy Seed (Default is time-based random-seed)')
    parser.add_argument('--height', type=int, default=1024, help='Image height (Default is 1024)')
    parser.add_argument('--width', type=int, default=1024, help='Image width (Default is 1024)')
    parser.add_argument('--steps', type=int, default=4, help='Inference Steps')
    parser.add_argument('--guidance', type=float, default=3.5, help='Guidance Scale (Default is 3.5)')

    args = parser.parse_args()

    seed = args.seed or int(time.time())

    flux = Flux1("black-forest-labs/FLUX.1-schnell", max_sequence_length=args.max_sequence_length)

    image = flux.generate_image(
        seed=args.seed,
        prompt=args.prompt,
        config=Config(
            num_inference_steps=args.steps,
            height=args.height,
            width=args.width,
            guidance=args.guidance,
        )
    )

    ImageUtil.save_image(image, "image.png")


if __name__ == '__main__':
    main()
