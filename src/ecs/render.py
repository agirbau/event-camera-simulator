import logging
import argparse

from omegaconf import OmegaConf
from tqdm.auto import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from ecs import BlenderScene
from ecs.logger import ECSLogHandler

root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(ECSLogHandler())

def main():
    parser = argparse.ArgumentParser(description="A render pipeline to create datasets using a blender enviornment and custom sensor implementations.")
    parser.add_argument(
        "--config", type=str, help="Path to the config file", default="config.yaml"
    )
    args = parser.parse_args()
    cfg = OmegaConf.load(args.config)

    log = logging.getLogger()
    if 'log_level' in cfg:
        log.setLevel(getattr(logging, cfg.log_level))
    log.info('Start')

    scene = BlenderScene(cfg)

    with logging_redirect_tqdm():
        progress_bar = tqdm(total=cfg.render.steps)
        progress_bar.set_description(f"Render")

        for p in range(0, cfg.render.steps, 1):
            progress_bar.update(1)
            log.debug(f'Step {p+1}/{cfg.render.steps}')

            scene.render(p)
        scene.complete()

    log.info('Done')